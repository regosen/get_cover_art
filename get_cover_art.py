import os, unicodedata, re
from pathlib import Path

from apple_downloader import AppleDownloader
from meta_mp3 import MetaMP3
from meta_mp4 import MetaMP4

# This script searches apple music for artwork that is missing from your library
# It saves the artwork alongside the audio and embeds the artwork into the meta tags

# By default it will scan from the current working directory, you can override this
# with commandline parameters or arguments passed into scan_folder()

DEFAULT_COVER_ART_FOLDER = "_cover_art_"
DEFAULT_SKIP_ARTISTS_FILE = "./skip_artists.txt"
DEFAULT_SKIP_ALBUMS_FILE = "./skip_albums.txt"
DEFAULT_SKIP_ARTWORK_FILE = "./skip_artwork.txt"

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
    def __init__(self, options={}):
        self.ignore_artists = ValueStore(options.get('skip_artists', DEFAULT_SKIP_ARTISTS_FILE))
        self.ignore_albums = ValueStore(options.get('skip_albums', DEFAULT_SKIP_ALBUMS_FILE))
        self.ignore_artwork = ValueStore(options.get('skip_artwork', DEFAULT_SKIP_ARTWORK_FILE))

        self.art_folder_override = ""
        self.downloader = None
        if not options.get('no_download'):
            self.downloader = AppleDownloader()
        if not options.get('inline'):
            self.art_folder_override = options.get('dest')
            if self.art_folder_override:
                Path(self.art_folder_override).mkdir(parents=True, exist_ok=True)
        self.embed = not (options.get('no_embed') or options.get('test'))
        self.verbose = options.get('verbose')

    def _should_skip(self, meta, art_path, verbose):
        if self.ignore_artists.has(meta.artist):
            if verbose: print("Skipping ignored artist (%s) for %s" % (meta.artist, art_path))
            return True
        if self.ignore_albums.has(meta.album):
            if verbose: print("Skipping ignored album (%s) for %s" % (meta.album, art_path))
            return True
        if meta.has_embedded_art():
            if verbose: print("Skipping existing embedded artwork for %s" % (art_path))
            return True
        if self.ignore_artwork.has(art_path):
            if verbose: print("Skipping ignored art path %s" % (art_path))
            return True
        return False
            
    # based on https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    def _slugify(self, value):
        """
        Normalizes string, removes non-alpha characters
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = re.sub('[^\w\s-]', '', bytes.decode(value)).strip()
        
        return value
    
    def _download(self, meta, art_path):
        if not os.path.exists(art_path):
            return self.downloader.dload_apple_art(meta, art_path)
        elif self.verbose:
            print('Skipping existing download for ' + art_path)
        
        return True
        

    def scan_folder(self, folder="."):
        if self.verbose: print("Scanning folder: " + folder)
        processed = 0
        skipped = 0
        failed = 0
        for root, dirs, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                base, ext = os.path.splitext(f.lower())
                art_folder = self.art_folder_override or os.path.dirname(path)
                try:
                    meta = None
                    if ext == '.mp3':
                        meta = MetaMP3(path)
                    elif ext == '.m4a':
                        meta = MetaMP4(path)
                    else:
                        continue
                    
                    if meta:
                        filename = self._slugify("%s - %s" % (meta.artist, meta.album))
                        art_path = os.path.join(art_folder, filename + ".jpg")
                        if self._should_skip(meta, art_path, self.verbose):
                            skipped += 1
                            continue

                        success = True
                        if self.downloader:
                            success = success and self._download(meta, art_path)
                        if self.embed:
                            success = success and meta.embed(art_path)
                        
                        if success:
                            processed += 1
                        else:
                            self.ignore_artwork.add(art_path)
                            skipped += 1

                except Exception as e:
                    print("ERROR: failed to process %s, %s" % (path, str(e)))
                    failed += 1
        return (processed, skipped, failed)

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help="folder to recursively scan for music", default=".")
    parser.add_argument('--dest', help="destination of artwork", default=DEFAULT_COVER_ART_FOLDER)

    parser.add_argument('--test', '--no_embed', help="scan and download only, don't embed artwork", action='store_true')
    parser.add_argument('--no_download', help="embed only previously-downloaded artwork", action='store_true')
    parser.add_argument('--inline', help="put artwork in same folders as music files", action='store_true')
    parser.add_argument('--verbose', help="print verbose logging", action='store_true')

    parser.add_argument('--skip_artists', help="file containing artists to skip", default=DEFAULT_SKIP_ARTISTS_FILE)
    parser.add_argument('--skip_albums', help="file containing albums to skip", default=DEFAULT_SKIP_ALBUMS_FILE)
    parser.add_argument('--skip_artwork', help="file containing destination art files to skip", default=DEFAULT_SKIP_ARTWORK_FILE)
    args = parser.parse_args()

    scanner = LibraryScanner(vars(args))
    (processed, skipped, failed) = scanner.scan_folder(args.path)
    print()
    print("Done!  Processed: %d, Skipped: %d, Failed: %d" % (processed, skipped, failed))
    if scanner.art_folder_override:
        print("Artwork folder: " + scanner.art_folder_override)
    else:
        print("Artwork files are alongside audio files.")
    print()

if __name__ == "__main__":
    main()