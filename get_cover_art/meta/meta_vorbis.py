from mutagen.oggvorbis import OggVorbis
from .base_ogg import MetaOgg

class MetaVorbis(MetaOgg):
    def __init__(self, path: str):
        return MetaOgg.__init__(self, path, OggVorbis(path))
