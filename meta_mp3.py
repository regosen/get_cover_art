from meta_audio import MetaAudio
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

class MetaMP3(MetaAudio):
    def __init__(self, mp3_path):
        self.audio_path = mp3_path
        self.audio = MP3(mp3_path, ID3=ID3)
        try:
            self.artist = self.audio.tags['TPE1'].text[0]
            self.album = self.audio.tags['TALB'].text[0]
            self.title = self.audio.tags['TIT2'].text[0]
        except:
            raise Exception("missing ID3 tags")

    def has_embedded_art(self):
        try:
            # some of these could have 'APIC:Cover' or something else
            # so we just look for APIC:<anything>
            return 'APIC:' in "".join(self.audio.tags.keys())
        except error:
            return False

    def embed_art(self, art_path):
        # from https://stackoverflow.com/questions/409949/how-do-you-embed-album-art-into-an-mp3-using-python
        self.audio.tags.add(
            APIC(
                encoding=3, # 3 is for utf-8
                mime='image/jpeg', # image/jpeg or image/png
                type=3, # 3 is for the cover image
                desc=u'Cover',
                data=open(art_path, 'rb').read()
            )
        )
        self.audio.save()