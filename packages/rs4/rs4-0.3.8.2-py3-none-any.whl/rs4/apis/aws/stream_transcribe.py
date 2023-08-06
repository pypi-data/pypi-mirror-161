#!pip3 install -U amazon-transcribe

import asyncio
import os
import threading
from ...misc import wavefile
from functools import partial
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from awscrt.auth import AwsCredentialsProvider, AwsCredentials
from amazon_transcribe import AWSCRTEventLoop
from botocore.credentials import CredentialResolver
from rs4 import logger
import tempfile
import moviepy.editor as mp
import time

class AudioStream:
    def __init__ (self, source, sample_rate = None):
        self.source = source
        self.sample_rate = sample_rate or source.sample_rate
        self.buffer = b''
        self.closed = False

    def read (self, size = 1024 * 16):
        if self.closed and not self.buffer:
            return b''
        if not self.closed and len (self.buffer) < size:
            d = self.source.get ()
            if not d:
                self.closed = True
            self.buffer += d
        data, self.buffer = self.buffer [:size], self.buffer [size:]
        return data


class AwsCustomCredentialResolver(CredentialResolver):
    def __init__(self, eventloop):
        self._crt_resolver = AwsCredentialsProvider.new_default_chain (eventloop)
        self.credentials = None

    async def get_credentials(self):
        if self.credentials is None:
            self.credentials = await asyncio.wrap_future (self._crt_resolver.get_credentials())
        return self.credentials



class MyEventHandler (TranscriptResultStreamHandler):
    def __init__ (self, callback = None, *args, **kargs):
        self.callback = callback
        super ().__init__ (*args, **kargs)

    async def handle_transcript_event (self, transcript_event):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                self.callback (alt.transcript)


async def transcribe (source, language = 'ko-KR', callback = print):
    client = TranscribeStreamingClient (region = os.getenv ('AWS_DEFAULT_REGION', 'ap-northeast-1'))
    transcriber = await client.start_stream_transcription (
        language_code = language,
        media_sample_rate_hz = source.sample_rate,
        media_encoding = "pcm"
    )

    async def send_chunks ():
        while 1:
            chunk = source.read (source.sample_rate)
            if not chunk:
                closed = True
                break
            await transcriber.input_stream.send_audio_event (audio_chunk = chunk)
            await asyncio.sleep (0.5)
        await transcriber.input_stream.end_stream()

    handler = MyEventHandler (callback, transcriber.output_stream)
    await asyncio.gather (send_chunks (), handler.handle_events ())
