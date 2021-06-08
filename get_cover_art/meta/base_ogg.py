from .meta_audio import MetaAudio
# It might look odd to be importing from FLAC in the OGG
# metadata encoder, but the VorbisComment spec (used by OGG formats) 
# specifies that it uses the FLAC structure, base64-encoded.
from mutagen.flac import Picture
import base64

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
        return bool(self.audio.get('metadata_block_picture', None))

    def detach_art(self):
        self.audio.pop('metadata_block_picture')
    
    def embed_art(self, art_path):
        artworkfile = open(art_path, 'rb').read()
        pic = Picture()
        with open(art_path, "rb") as f:
            pic.data = f.read()
        pic.type = 3 # front cover
        if art_path.endswith('png'):
            pic.mime = 'image/png'
        else:
            pic.mime = 'image/jpeg'
        pic.desc = 'front cover'
        self.audio['metadata_block_picture'] = base64.b64encode(pic.write()).decode('utf8')

    def save(self):
        self.audio.save()
