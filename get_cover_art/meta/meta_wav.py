from .base_id3 import MetaID3
from mutagen.wave import WAVE

class MetaWAV(MetaID3):
    def __init__(self, path):
        return MetaID3.__init__(self, path, WAVE(path))
