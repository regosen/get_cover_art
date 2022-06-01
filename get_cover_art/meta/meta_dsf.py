from .base_id3 import MetaID3
from mutagen.dsf import DSF

class MetaDSF(MetaID3):
    def __init__(self, path):
        return MetaID3.__init__(self, path, DSF(path))
