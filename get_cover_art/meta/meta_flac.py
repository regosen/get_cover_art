from .meta_audio import MetaAudio
from mutagen.flac import Picture, FLAC

class MetaFLAC(MetaAudio):
    def __init__(self, path):
        self.audio_path = path
        self.audio = FLAC(path)
        try:
            if 'albumartist' in self.audio:
                # use Album Artist first
                self.artist = self.audio['albumartist'][0]
            else:
                self.artist = self.audio['artist'][0]
            self.album = self.audio['album'][0]
            self.title = self.audio['title'][0]
        except:
            raise Exception("missing FLAC tags")
    
    def has_embedded_art(self):
        return self.audio.pictures != []

    def detach_art(self):
        self.audio.clear_pictures()

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
        self.audio.add_picture(pic)

    def save(self):
        self.audio.save()