import os, unicodedata, re
from pathlib import Path

from .apple_downloader import AppleDownloader
from .meta.meta_mp3 import MetaMP3
from .meta.meta_mp4 import MetaMP4
from .meta.meta_flac import MetaFLAC
from .meta.meta_opus import MetaOpus
from .meta.meta_vorbis import MetaVorbis

DEFAULTS = {
    "art_size": "500",
    "cover_art": "_cover_art",
    "skip_artists": "./skip_artists.txt",
    "skip_albums": "./skip_albums.txt",
    "skip_artwork": "./skip_artwork.txt",
    "external_art_mode": "none",
    "external_art_filename": ['cover.jpg', '_albumcover.jpg', 'folder.jpg'],
    "art_dest_filename": "{artist} - {album}.jpg",
    "throttle": 3,
}

# utility class to cache a set of values
class ValueStore(object):
    def __init__(self, cache_file):
        self.filename = cache_file
        self.delim = "\n"

        if os.path.isfile(self.filename):
            with open(self.filename) as file:
                contents = file.read()
            self.keys = set(contents.split(self.delim))
        else:
            self.keys = set([])

    def reset(self):
        self.keys = set([])
        self.filename = ''

    def has(self, key):
        return key in self.keys
    
    def add(self, key):
        if not self.has(key):
            self.keys.add(key)
            self._update()

    def _update(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'w') as file:
                file.write(self.delim.join(sorted(self.keys)))

class CoverFinder(object):
    def __init__(self, options={}):
        options = {k.replace('-', '_'): v for k, v in options.items()}
        self.art_size = int(options.get('art_size', DEFAULTS.get('art_size')))
        self.ignore_artists = ValueStore(options.get('skip_artists', DEFAULTS.get('skip_artists')))
        self.ignore_albums = ValueStore(options.get('skip_albums', DEFAULTS.get('skip_albums')))
        self.ignore_artwork = ValueStore(options.get('skip_artwork', DEFAULTS.get('skip_artwork')))
        self.art_dest_filename = options.get('art_dest_filename', DEFAULTS.get('art_dest_filename'))
        if options.get('no_skip'):
            self.ignore_artwork.reset()

        self.files_processed = [] # artwork was downloaded / embedded
        self.files_skipped = []   # no artwork was available / embeddable
        self.files_invalid = []   # not a unsupported audio file
        self.files_failed = []    # exception encountered

        self.art_folder_override = ""
        self.verbose = options.get('verbose')
        self.downloader = None
        self.external_art_mode = options.get('external_art_mode', None)
        self.external_art_filename = options.get('external_art_filename', None)
        if not options.get('no_download'):
            throttle = float(options.get('throttle') or DEFAULTS.get('throttle'))
            self.downloader = AppleDownloader(self.verbose, throttle, self.art_size)
        if not options.get('art_dest_inline'):
            self.art_folder_override = options.get('art_dest')
            if self.art_folder_override:
                self.art_folder_override = os.path.abspath(self.art_folder_override)
                Path(self.art_folder_override).mkdir(parents=True, exist_ok=True)

        self.clear = options.get('clear')
        self.embed = not (options.get('no_embed') or options.get('test'))
        self.force = options.get('force')

    def _should_skip(self, meta, art_path, verbose):
        if self.force:
            return False
        if self.ignore_artists.has(meta.artist):
            if verbose: print(f"Skipping ignored artist ({meta.artist}) for {art_path}")
            return True
        if self.ignore_albums.has(meta.album):
            if verbose: print(f"Skipping ignored album ({meta.album}) for {art_path}")
            return True
        if meta.has_embedded_art() and not self.clear:
            if verbose: print(f"Skipping existing embedded artwork for {art_path}")
            return True
        if self.ignore_artwork.has(art_path):
            if verbose: print(f"Skipping ignored art path {art_path}")
            return True
        return False
            
    # based on https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    def _slugify(self, value, has_extension=True):
        """
        Normalizes string, removes non-alpha characters

        This assumes that a filename being passed in has an
        extension, and preserves the period leading that extension.
        If you have an extensionless filename, specify has_extension=False
        """
        if has_extension:
            value, ext = os.path.splitext(value)
        else:
            ext = ""

        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = re.sub('[^\w\s-]', '', bytes.decode(value)).strip()

        value += ext
        
        return value
    
    def _download(self, meta, art_path):
        if self.force or not os.path.exists(art_path):
            return self.downloader.download(meta, art_path)
        elif self.verbose:
            print(f"Skipping existing download for {art_path}")
        
        return True
    
    def _find_folder_art(self, meta, folder):
        for f in self.external_art_filename:
            filename = self._slugify(f.format(artist=meta.artist, album=meta.album, title=meta.title), has_extension=True)
            filename = os.path.join(folder, filename)
            if os.access(filename, os.R_OK):
                return filename
        return None

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
                filename = self._slugify(self.art_dest_filename.format(artist=meta.artist, album=meta.album, title=meta.title))
                art_path = os.path.join(art_folder, filename)
                if self._should_skip(meta, art_path, self.verbose):
                    self.files_skipped.append(path)
                    return

                success = True
                file_changed = False
                # Logic:
                # If external_art_mode is "before" we want to avoid network 
                # traffic if possible and use the local file. If 
                # external_art_mode is "after" then we only use the local
                # file if the network lookup is unsuccessful.
                #
                # First, check if there is a local file (local_art will
                # be None if not).
                if self.external_art_mode in ("before", "after"):
                    local_art = self._find_folder_art(meta, folder)

                # Avoid downloading if it exists and we are in "before" mode
                if self.downloader and (not self.external_art_mode=="before" or not local_art):
                    success = self._download(meta, art_path)

                # Now, if "before" prefer the local art...
                if self.external_art_mode == "before":
                    if local_art:
                        art_path = local_art
                # Otherwise, if "after" then only look at the local art if
                # the download failed (or we were in no-download mode)
                elif self.external_art_mode == "after" and (not success or not self.downloader):
                    success = bool(local_art)
                    art_path = local_art

                if self.clear:
                    file_changed = meta.clear() # do this regardless of finding art
                
                if self.embed:
                    embedded = meta.embed(art_path)
                    file_changed = file_changed or embedded
                    success = success and embedded
                
                if file_changed:
                    meta.save()

                if success:
                    self.files_processed.append(path)
                else:
                    self.ignore_artwork.add(art_path)
                    self.files_skipped.append(path)

        except Exception as e:
            print(f"ERROR: failed to process {path}, {type(e).__name__}: {str(e)}")
            self.files_failed.append(path)
            
    def scan_folder(self, folder="."):
        if self.verbose: print(f"Scanning folder: {folder}")
        for root, dirs, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                self.scan_file(path)
