from mutagen.oggvorbis import OggVorbis
from .base_ogg import MetaOgg

class MetaVorbis(MetaOgg):
    def __init__(self, path):
        return MetaOgg.__init__(self, path, OggVorbis(path))
