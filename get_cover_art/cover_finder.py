import os, unicodedata, re
from pathlib import Path

from .apple_downloader import AppleDownloader
from .meta_mp3 import MetaMP3
from .meta_mp4 import MetaMP4
from .meta_flac import MetaFLAC
from .meta_opus import MetaOpus
from .meta_vorbis import MetaVorbis

DEFAULTS = {
    "cover_art": "_cover_art",
    "skip_artists": "./skip_artists.txt",
    "skip_albums": "./skip_albums.txt",
    "skip_artwork": "./skip_artwork.txt",
}

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

    def clear(self):
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


class CoverFinder(object):
    def __init__(self, options={}):
        self.ignore_artists = ValueStore(options.get('skip_artists', DEFAULTS.get('skip_artists')))
        self.ignore_albums = ValueStore(options.get('skip_albums', DEFAULTS.get('skip_albums')))
        self.ignore_artwork = ValueStore(options.get('skip_artwork', DEFAULTS.get('skip_artwork')))

        self.files_processed = [] # artwork was downloaded / embedded
        self.files_skipped = []   # no artwork was available / embeddable
        self.files_invalid = []   # not a unsupported audio file
        self.files_failed = []    # exception encountered

        self.art_folder_override = ""
        self.verbose = options.get('verbose')
        self.downloader = None
        if not options.get('no_download'):
            self.downloader = AppleDownloader(self.verbose, float(options.get('throttle') or 0))
        if not options.get('inline'):
            self.art_folder_override = options.get('dest')
            if self.art_folder_override:
                self.art_folder_override = os.path.abspath(self.art_folder_override)
                Path(self.art_folder_override).mkdir(parents=True, exist_ok=True)

        self.embed = not (options.get('no_embed') or options.get('test'))
        self.force = options.get('force')

    def _should_skip(self, meta, art_path, verbose):
        if self.force:
            return False
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
        if self.force or not os.path.exists(art_path):
            return self.downloader.download(meta, art_path)
        elif self.verbose:
            print('Skipping existing download for ' + art_path)
        
        return True
    
    def scan_file(self, path):
        folder, filename = os.path.split(path)
        base, ext = os.path.splitext(filename.lower())
        art_folder = self.art_folder_override or folder
        try:
            meta = None
            if ext == '.mp3':
                meta = MetaMP3(path)
            elif ext == '.m4a':
                meta = MetaMP4(path)
            elif ext == '.flac':
                meta = MetaFLAC(path)
            elif ext == '.opus':
                meta = MetaOpus(path)
            elif ext == '.ogg':
                meta = MetaVorbis(path)
            else:
                self.files_invalid.append(path)
                return
            
            if meta:
                filename = self._slugify("%s - %s" % (meta.artist, meta.album))
                art_path = os.path.join(art_folder, filename + ".jpg")
                if self._should_skip(meta, art_path, self.verbose):
                    self.files_skipped.append(path)
                    return

                success = True
                if self.downloader:
                    success = success and self._download(meta, art_path)
                if self.embed:
                    success = success and meta.embed(art_path)
                
                if success:
                    self.files_processed.append(path)
                else:
                    self.ignore_artwork.add(art_path)
                    self.files_skipped.append(path)

        except Exception as e:
            print("ERROR: failed to process %s, %s" % (path, str(e)))
            self.files_failed.append(path)
            
    def scan_folder(self, folder="."):
        if self.verbose: print("Scanning folder: " + folder)
        for root, dirs, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                self.scan_file(path)
