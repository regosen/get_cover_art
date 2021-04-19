from .meta_audio import MetaAudio
# It might look odd to be importing from FLAC in the opus
# metadata encoder, but the VorbisComment spec (used by Opus) 
# specifies that it uses the FLAC structure, base64-encoded.
from mutagen.flac import Picture
from mutagen.oggopus import OggOpus
import base64

class MetaOpus(MetaAudio):
    def __init__(self, path):
        self.audio_path = path
        self.audio = OggOpus(path)
        try:
            if 'albumartist' in self.audio:
                # use Album Artist first
                self.artist = self.audio['albumartist'][0]
            else:
                self.artist = self.audio['artist'][0]
            self.album = self.audio['album'][0]
            self.title = self.audio['title'][0]
        except:
            raise Exception("missing VorbisComment/opus tags")
    
    def has_embedded_art(self):
        rv = bool(self.audio.get('metadata_block_picture', None))
        return rv

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
        self.audio.save()

