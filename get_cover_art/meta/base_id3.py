from .meta_audio import MetaAudio
from mutagen.id3 import APIC
from mutagen import FileType

class MetaID3(MetaAudio):
    def _get_tag(self, tag: str) -> str:
        return self.audio.tags[tag].text[0] if tag in self.audio.tags else ""
    
    def __init__(self, path: str, audio: FileType):
        self.audio_path = path
        self.audio = audio
        # prefer Album Artist
        self.artist = self._get_tag('TPE2') or self._get_tag('TPE1') 
        self.album = self._get_tag('TALB')
        self.title = self._get_tag('TIT2')
        if self.artist == "" or self.title == "":
            raise Exception("missing ID3 tags")

    def has_embedded_art(self) -> bool:
        return self.audio.tags.getall("APIC") != []

    def detach_art(self):
        self.audio.tags.delall("APIC")

    def embed_art(self, art_path: str):
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