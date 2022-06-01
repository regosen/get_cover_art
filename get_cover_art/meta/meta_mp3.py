from .base_id3 import MetaID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class MetaMP3(MetaID3):
    def __init__(self, path):
        return MetaID3.__init__(self, path, MP3(path, ID3=ID3))
