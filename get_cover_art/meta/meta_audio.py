import os


class MetaAudio(object):
    @staticmethod
    def get_mime_type(art_path: str) -> str:
        return 'image/png' if art_path.lower().endswith('.png') else 'image/jpeg'
        
    def embed(self, art_path: str, detach_existing = True) -> bool:
        if os.path.exists(art_path):
            print(f"Embedding art into {self.audio_path}")
            if detach_existing and self.has_embedded_art():
                self.detach_art()
            self.embed_art(art_path)
            return True
        return False

    def clear(self) -> bool:
        if not self.has_embedded_art():
            return False
        self.detach_art()
        return True

    def has_embedded_art(self) -> bool:
        return False

    def detach_art(self):
        raise Exception("detach_art called on MetaAudio base class")
        
    def embed_art(self, art_path: str):
        raise Exception("embed_art called on MetaAudio base class")
    
    def save(self):
        raise Exception("save called on MetaAudio base class")