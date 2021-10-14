from .meta_audio import MetaAudio
# It might look odd to be importing from FLAC in the OGG
# metadata encoder, but the VorbisComment spec (used by OGG formats) 
# specifies that it uses the FLAC structure, base64-encoded.
from mutagen.flac import Picture
import base64

ART_TAG = 'metadata_block_picture'

class MetaOgg(MetaAudio):
    def __init__(self, path):
        self.audio_path = path
        self.audio = self.fileparser(path)
        try:
            if 'albumartist' in self.audio:
                # use Album Artist first
                self.artist = self.audio['albumartist'][0]
            else:
                self.artist = self.audio['artist'][0]
            self.album = self.audio['album'][0]
            self.title = self.audio['title'][0]
        except:
            raise Exception("missing VorbisComment tags (in ogg vorbis or opus file)")
    
    def has_embedded_art(self):
        return bool(self.audio.get(ART_TAG, None))

    def detach_art(self):
        self.audio.pop(ART_TAG)
    
    def embed_art(self, art_path):
        pic = Picture()
        with open(art_path, "rb") as f:
            pic.data = f.read()
        pic.type = 3 # front cover
        pic.mime = MetaAudio.get_mime_type(art_path)
        pic.desc = 'front cover'
        self.audio[ART_TAG] = base64.b64encode(pic.write()).decode('utf8')

    def save(self):
        self.audio.save()
