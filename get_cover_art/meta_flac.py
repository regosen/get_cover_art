from .meta_audio import MetaAudio
from mutagen.flac import Picture, FLAC

class MetaFLAC(MetaAudio):
    def __init__(self, mp4_path):
        self.audio_path = mp4_path
        self.audio = FLAC(mp4_path)
        try:
            self.artist = self.audio['artist'][0]
            self.album = self.audio['album'][0]
            self.title = self.audio['title'][0]
        except:
            raise Exception("missing FLAC tags")
    
    def has_embedded_art(self):
        return self.audio.pictures != []

    def embed_art(self, art_path):
        self.audio.clear_pictures()
        artworkfile = open(art_path, 'rb').read()
        pic = Picture()
        with open(art_path, "rb") as f:
            pic.data = f.read()
        pic.type = 3 # front cover
        if art_path.endswith('png'):
            mime = 'image/png'
        else:
            mime = 'image/jpeg'
        pic.desc = 'front cover'
        self.audio.add_picture(pic)
        self.audio.save()
