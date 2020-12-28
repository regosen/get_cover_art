from .meta_audio import MetaAudio
from mutagen.mp4 import MP4
from mutagen.m4a import M4ACover

class MetaMP4(MetaAudio):
    def __init__(self, path):
        self.audio_path = path
        self.audio = MP4(path)
        try:
            if 'aART' in self.audio.tags:
                # use Album Artist first
                self.artist = self.audio.tags['aART'][0]
            else:
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
