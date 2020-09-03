import os, sys, unicodedata, re

from apple_downloader import AppleDownloader
from meta_mp3 import MetaMP3
from meta_mp4 import MetaMP4

# This script searches apple music for artwork that is missing from your library
# It saves the artwork alongside the audio and embeds the artwork into the meta tags

# utility class to cache a set of values
class ValueStore(object):
    def __init__(self, cache_file):
        self.filename = cache_file
        self.delim = "\n"

        if os.path.isfile(self.filename):
            file = open(self.filename)
            contents = file.read()
            file.close()
            self.keys = set(contents.split(self.delim))
        else:
            self.keys = set([])

    def has(self, key):
        return key in self.keys
    
    def add(self, key):
        if not self.has(key):
            self.keys.add(key)
            self._update()

    def _update(self):
        file = open(self.filename,'w')
        contents = file.write(self.delim.join(sorted(self.keys)))
        file.close()


class LibraryScanner(object):
    def __init__(self):
        self.ignore_artwork = ValueStore("ignore_artwork.txt")
        self.ignore_artists = ValueStore("ignore_artists.txt")
        self.ignore_albums = ValueStore("ignore_albums.txt")
        self.downloader = AppleDownloader()

    def _should_skip(self, meta, art_path):
        if self.ignore_artists.has(meta.artist):
            return True
        if self.ignore_albums.has(meta.album):
            return True
        if meta.has_embedded_art():
            return True
        if self.ignore_artwork.has(art_path):
            return True
        return False
            
    # based on https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    def _slugify(self, value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = re.sub('[^\w\s-]', '', bytes.decode(value)).strip().lower()
        value = re.sub('[-\s]+', '-', value)
        
        return value

    def scan_folder(self, folder):
        processed = 0
        skipped = 0
        failed = 0
        for root, dirs, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                base, ext = os.path.splitext(f.lower())
                try:
                    meta = None
                    if ext == '.mp3':
                        meta = MetaMP3(path)
                    elif ext == '.m4a':
                        meta = MetaMP4(path)
                    else:
                        continue
                    
                    if meta:
                        filename = self._slugify("%s_%s" % (meta.artist, meta.album))
                        art_path = os.path.join(os.path.dirname(path), filename + ".jpg")
                        if self._should_skip(meta, art_path):
                            skipped += 1
                        elif meta.process(self.downloader, art_path):
                            processed += 1
                        else:
                            self.ignore_artwork.add(art_path)
                            skipped += 1
                except Exception as e:
                    print("ERROR: failed to process %s, %s" % (path, str(e)))
                    failed += 1
        return (processed, skipped, failed)

def main():
    sourceBase = ""
    if len(sys.argv) != 2:
        print('SYNTAX: get_cover_art.py <path_to_audio_library>')
        return

    scanner = LibraryScanner()
    (processed, skipped, failed) = scanner.scan_folder(sys.argv[1])
    print()
    print("Done!  Processed: %d, Skipped: %d, Failed: %d" % (processed, skipped, failed))
    print()

if __name__ == "__main__":
    main()