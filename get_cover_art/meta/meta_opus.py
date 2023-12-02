from mutagen.oggopus import OggOpus
from .base_ogg import MetaOgg

class MetaOpus(MetaOgg):
    def __init__(self, path: str):
        return MetaOgg.__init__(self, path, OggOpus(path))
