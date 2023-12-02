from .meta_audio import MetaAudio
from mutagen.mp4 import MP4
from mutagen.m4a import M4ACover

class MetaMP4(MetaAudio):
    def _get_tag(self, tag: str) -> str:
        return self.audio.tags[tag][0] if tag in self.audio.tags else ""
    
    def __init__(self, path: str):
        self.audio_path = path
        self.audio = MP4(path)
        # prefer Album Artist
        self.artist = self._get_tag('aART') or self._get_tag('©ART') 
        self.album = self._get_tag('©alb')
        self.title = self._get_tag('©nam')
        if self.artist == "" or self.title == "":
            raise Exception("missing XMP tags")
    
    def has_embedded_art(self) -> bool:
        return 'covr' in self.audio.tags

    def detach_art(self):
        self.audio.tags['covr'] = []

    def embed_art(self, art_path: str):
        artworkfile = open(art_path, 'rb').read()
        format = M4ACover.FORMAT_PNG if art_path.endswith('png') else M4ACover.FORMAT_JPEG
        self.audio.tags['covr'] = [M4ACover(artworkfile, format)]

    def save(self):
        self.audio.save()