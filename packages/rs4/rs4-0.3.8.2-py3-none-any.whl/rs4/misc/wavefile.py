import struct
import io
from rs4.attrdict import AttrDict

class WaveFile:
    def __init__ (self, filename):
        self.fh = io.open (filename, 'rb')
        self._info = self.read_header ()

    def __getattr__ (self, name):
        try:
            return self._info [name]
        except KeyError:
            raise AttributeError (name)

    def read_data (self):
        self.fh.seek (self.data_offset)
        d = self.fh.read ()
        self.fh.close ()
        return d

    def read_header (self):
        fh = self.fh
        d = AttrDict ()
        riff, size, fformat = struct.unpack('<4sI4s', fh.read(12))
        d.riff, d.chunk_size, d.format = riff, size, fformat
        chunk_header = fh.read(8)
        subchunkid, d.subchunksize = struct.unpack('<4sI', chunk_header)
        if (subchunkid == b'fmt '):
            aformat, channels, samplerate, byterate, blockalign, bps = struct.unpack('HHIIHH', fh.read(16))
            bitrate = (samplerate * channels * bps) / 1024
            d.aformat, d.channels, d.sample_rate, d.bit_rate = aformat, channels, samplerate, bitrate
        d.chunk_offset = fh.tell()
        d.subchunk2id, d.subchunk2size = struct.unpack('<4sI', fh.read(8))
        d.data_offset = fh.tell()
        return d
