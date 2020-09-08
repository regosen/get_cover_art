from .meta_audio import MetaAudio
from mutagen.mp4 import MP4
from mutagen.m4a import M4ACover

class MetaMP4(MetaAudio):
    def __init__(self, mp4_path):
        self.audio_path = mp4_path
        self.audio = MP4(mp4_path)
        try:
            self.artist = self.audio.tags['©ART'][0]
            self.album = self.audio.tags['©alb'][0]
            self.title = self.audio.tags['©nam'][0]
        except:
            raise Exception("missing XMP tags")
    
    def has_embedded_art(self):
        return 'covr' in self.audio.tags

    def embed_art(self, art_path):
        covr = []
        artworkfile = open(art_path, 'rb').read()
        covr.append(M4ACover(artworkfile, M4ACover.FORMAT_JPEG))
        self.audio.tags['covr'] = covr
        self.audio.save()
