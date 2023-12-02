from .meta_audio import MetaAudio
from mutagen.flac import Picture, FLAC

class MetaFLAC(MetaAudio):
    def _get_tag(self, tag: str) -> str:
        return self.audio[tag][0] if tag in self.audio else ""
    
    def __init__(self, path: str):
        self.audio_path = path
        self.audio = FLAC(path)
        # prefer Album Artist
        self.artist = self._get_tag('albumartist') or self._get_tag('artist') 
        self.album = self._get_tag('album')
        self.title = self._get_tag('title')
        if self.artist == "" or self.title == "":
            raise Exception("missing FLAC tags")
    
    def has_embedded_art(self) -> bool:
        return self.audio.pictures != []

    def detach_art(self):
        self.audio.clear_pictures()

    def embed_art(self, art_path: str):
        pic = Picture()
        with open(art_path, "rb") as f:
            pic.data = f.read()
        pic.type = 3 # front cover
        pic.mime = MetaAudio.get_mime_type(art_path)
        pic.desc = 'front cover'
        self.audio.add_picture(pic)

    def save(self):
        self.audio.save()