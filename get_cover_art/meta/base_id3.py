from .meta_audio import MetaAudio
from mutagen.id3 import APIC

class MetaID3(MetaAudio):
    def __init__(self, path, audio):
        self.audio_path = path
        self.audio = audio
        try:
            if 'TPE2' in self.audio.tags:
                # use Album Artist first
                self.artist = self.audio.tags['TPE2'].text[0]
            else:
                self.artist = self.audio.tags['TPE1'].text[0]
            self.album = self.audio.tags['TALB'].text[0]
            self.title = self.audio.tags['TIT2'].text[0]
        except:
            raise Exception("missing ID3 tags")

    def has_embedded_art(self):
        return self.audio.tags.getall("APIC") != []

    def detach_art(self):
        self.audio.tags.delall("APIC")

    def embed_art(self, art_path):
        # from https://stackoverflow.com/questions/409949/how-do-you-embed-album-art-into-an-mp3-using-python
        self.audio.tags.add(
            APIC(
                encoding=3, # 3 is for utf-8
                mime = MetaAudio.get_mime_type(art_path),
                type=3, # 3 is for the cover image
                desc=u'Cover',
                data=open(art_path, 'rb').read()
            )
        )

    def save(self):
        self.audio.save()