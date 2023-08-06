# !pip3 install -U m3u8 streamlink
try:
    import m3u8
    import streamlink
    import moviepy.editor as mp
except ImportError:
    raise ImportError ("pip3 install -U m3u8 streamlink moviepy")

import queue
import requests
import os
import urllib
from . import wavefile
import tempfile
import rs4
import time
import datetime
import threading
from urllib.parse import urljoin
import requests

class WaveStream:
    def __init__ (self, source, limit = 0):
        self.source = source
        self.sample_rate = wavefile.WaveFile (self.source).sample_rate
        self.closed = False
        self.fp = None
        self.limit = limit
        self.niter = -1

    def read (self, size = 1024 * 16):
        if self.closed:
            return b''
        if self.fp is None:
            self.fp = open (self.source, 'rb')
        self.niter += 1
        chunk = self.fp.read (size)
        if not chunk or (self.limit and self.niter == self.limit):
            self.fp.close ()
            self.closed = True
        return chunk


class StreamLink:
    def __init__ (self, url, sample_rate = 0, limit = 0, verbose = False, nseg = 3):
        self.url = url
        _r = requests.get (url)
        if _r.history:
            self.url = _r.history [0].headers ['location']
        self.sample_rate = sample_rate
        self.limit = limit
        self.verbose = verbose
        self.nseg = nseg
        self.buffer = b''
        self.session = requests.Session ()
        self.queue = queue.Queue ()
        threading.Thread (target = self.download_streams).start ()

    def close (self, msg):
        self.queue.put (None)
        self.verbose and print (msg)

    def _extract_wave (self, stream_data, sr = 16000):
        tmp_ts = '/tmp/' + next (tempfile._get_candidate_names()) + '.ts'
        with open (tmp_ts, 'wb') as f:
            f.write (stream_data)
        clip = mp.VideoFileClip (tmp_ts)
        tmp_wav = '/tmp/' + next (tempfile._get_candidate_names()) + '.wav'
        clip.audio.write_audiofile (tmp_wav, ffmpeg_params = f"-ar {sr} -ac 1".split (), logger = None)
        wf = wavefile.WaveFile (tmp_wav)
        assert wf.sample_rate == sr
        stream_data = wf.read_data ()
        os.remove (tmp_ts)
        os.remove (tmp_wav)
        return stream_data

    def downalod_chunk (self, segment):
        r = self.session.get (urljoin (segment.base_uri, segment.uri))
        stream_data = r.content
        if self.sample_rate:
            stream_data = self._extract_wave (stream_data, self.sample_rate)
            self.verbose and print ('AUDIOLEN', (len (stream_data) // 2) / self.sample_rate)
        self.queue.put (stream_data)

    def download_streams (self):
        last_segment = None
        chunk_ids = {}
        niter = -1
        same_date_time = 0
        while 1:
            if self.limit and niter == self.limit:
                return self.close ('LIMITREACHED')

            niter += 1
            streams = streamlink.streams (self.url)
            stream_url = streams ["worst"]
            m3u8_obj = m3u8.load (stream_url.args ['url'])

            if m3u8_obj.is_variant:
                playlist = m3u8_obj.playlists [0]
                m3u8_obj = m3u8.load (urljoin (playlist.base_uri, playlist.uri))

            if not m3u8_obj.segments:
                return self.close ('ENDMEDIA')

            segments = []
            segment = m3u8_obj.segments [0]
            current_offset = segment.program_date_time
            chunk_id = segment.uri.split ("_") [-1]
            segment_duration = segment.duration

            if not current_offset:
                if chunk_id in chunk_ids:
                    current_offset = chunk_ids [chunk_id]
                else:
                    current_offset = datetime.datetime.now ()
                segment.program_date_time = current_offset

            chunk_ids [chunk_id] = current_offset

            for segment in m3u8_obj.segments:
                chunk_id = segment.uri.split ("_") [-1]
                if segment.program_date_time is None:
                    current_offset = segment.program_date_time = current_offset + datetime.timedelta (seconds = segment.duration)
                    chunk_ids [chunk_id] = current_offset
                if last_segment and current_offset <= last_segment.program_date_time:
                    continue
                segments.append (segment)

            if not segments:
                same_date_time += 1
                if same_date_time >= 10:
                    return self.close ('MAYBEENDMEDIA')

                self.verbose and print (f'NONEWSTREAMS {last_segment.program_date_time}')
                time.sleep (segment_duration / 10)
                continue

            self.verbose and print (f'NITER {niter}, VALID SEGMENTS {len (segments)}/{len (m3u8_obj.segments)}', current_offset)
            same_date_time = 0 # RESET
            if last_segment is None:
                skip = round (10 / segment_duration)
                print (f"SEGMENTSKIP {skip}")
                if len (segments) <= 1:
                    skip = 0
                skip = 0 # 불교방송
                segments = segments [skip:] # skip first few seconds

            for segment in segments:
                self.downalod_chunk (segment)
                last_segment = segment


    def get (self):
        stream_data = self.queue.get ()
        if not stream_data:
            return b''
        return stream_data


class FileChunkStream (StreamLink):
    def __init__ (self, source, sample_rate = 16000, limit = 0, verbose = False, delay = True):
        self.clip = mp.VideoFileClip (source)
        self.delay = delay
        self.sample_rate = sample_rate
        self.limit = limit
        self.verbose = verbose
        self.buffer = b''
        self.queue = queue.Queue ()
        threading.Thread (target = self.download_streams).start ()

    def _extract_wave (self, offset, limit):
        clip = self.clip.subclip (offset, limit)
        tmp_wav = '/tmp/' + next (tempfile._get_candidate_names()) + '.wav'
        clip.audio.write_audiofile (tmp_wav, ffmpeg_params = f"-ar {self.sample_rate} -ac 1".split (), logger = None)
        wf = wavefile.WaveFile (tmp_wav)
        assert wf.sample_rate == self.sample_rate
        stream_data = wf.read_data ()
        os.remove (tmp_wav)
        return stream_data

    def download_streams (self):
        duration = self.clip.duration
        for niter, offset in enumerate (range (0, int (duration - 5), 5)):
            s = time.time ()
            if self.limit and niter == self.limit:
                return self.close ('LIMITREACHED')
            limit = offset + 5
            if limit + 5 > self.clip.duration:
                limit = self.clip.duration
            stream_data = self._extract_wave (offset, limit)
            self.verbose and print ('AUDIOLEN', (len (stream_data) // 2) / self.sample_rate)
            self.queue.put (stream_data)
            if self.delay and niter > 6:
                time.sleep (5 - (time.time () - s))
        return self.close ('ENDMEDIA')
