import os

class MetaAudio(object):    
    def embed(self, art_path):
        if os.path.exists(art_path):
            print("Embedding art into " + self.audio_path)
            self.embed_art(art_path)
            return True
        
        return False

    def has_embedded_art(self):
        return False

    def embed_art(self, art_path):
        raise Exception("add_art called on MetaAudio base class")
    