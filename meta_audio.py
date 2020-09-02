import os

class MetaAudio(object):
    def process(self, downloader, art_path):
        if not os.path.exists(art_path):
            if not downloader.dload_apple_art(self, art_path):
                return False
        
        if os.path.exists(art_path):
            print("Embedding art into " + self.audio_path)
            self.embed_art(art_path)
            return True
        
        return False
    
    def has_embedded_art(self):
        return False

    def embed_art(self, art_path):
        raise Exception("add_art called on MetaAudio base class")
    