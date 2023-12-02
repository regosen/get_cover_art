from .meta_audio import MetaAudio
# It might look odd to be importing from FLAC in the OGG
# metadata encoder, but the VorbisComment spec (used by OGG formats) 
# specifies that it uses the FLAC structure, base64-encoded.
from mutagen.flac import Picture
from mutagen import FileType
import base64

ART_TAG = 'metadata_block_picture'

class MetaOgg(MetaAudio):
    def _get_tag(self, tag: str) -> str:
        return self.audio[tag][0] if tag in self.audio else ""
    
    def __init__(self, path: str, audio: FileType):
        self.audio_path = path
        self.audio = audio
        # prefer Album Artist
        self.artist = self._get_tag('albumartist') or self._get_tag('artist') 
        self.album = self._get_tag('album')
        self.title = self._get_tag('title')
        if self.artist == "" or self.title == "":
            raise Exception("missing VorbisComment tags (in ogg vorbis or opus file)")
    
    def has_embedded_art(self) -> bool:
        return bool(self.audio.get(ART_TAG, None))

    def detach_art(self):
        self.audio.pop(ART_TAG)
    
    def embed_art(self, art_path: str):
        pic = Picture()
        with open(art_path, "rb") as f:
            pic.data = f.read()
        pic.type = 3 # front cover
        pic.mime = MetaAudio.get_mime_type(art_path)
        pic.desc = 'front cover'
        self.audio[ART_TAG] = base64.b64encode(pic.write()).decode('utf8')

    def save(self):
        self.audio.save()
