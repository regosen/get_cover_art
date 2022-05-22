import time
from urllib.request import Request, urlopen, HTTPError
from urllib.parse import urlparse, quote
from .normalizer import ArtistNormalizer, AlbumNormalizer
from .deromanizer import DeRomanizer

QUERY_TEMPLATE = "https://itunes.apple.com/search?term=%s&media=music&entity=album"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
THROTTLED_HTTP_CODES = [403, 429]

class AppleDownloader(object):
    def __init__(self, verbose, throttle, art_size):
        self.size_suffix = f"{art_size}x{art_size}bb"
        self.verbose = verbose
        self.throttle = throttle
        self.artist_normalizer = ArtistNormalizer()
        self.album_normalizer = AlbumNormalizer()
        self.deromanizer = DeRomanizer()
        
    def _urlopen_safe(self, url):
        while True:
            try:
                q = Request(url)
                q.add_header("User-Agent", USER_AGENT)
                response = urlopen(q)
                return response.read()
            except HTTPError as e:
                if e.code in THROTTLED_HTTP_CODES:
                    # we've been throttled, time to sleep
                    domain = urlparse(url).netloc
                    print(f"WARNING: Request limit exceeded from {domain}, trying again in {self.throttle} seconds...")
                    time.sleep(self.throttle)
                else:
                    raise e

    def _urlopen_text(self, url):
        try:
            return self._urlopen_safe(url).decode("utf8")
        except Exception as error:
            if ("certificate verify failed" in str(error)):
                print(f"ERROR: Python doesn't have SSL certificates installed, can't access {url}")
                print("Please run 'Install Certificates.command' from your Python installation directory.")
            else:
                print(f"ERROR: reading URL ({url}): {str(error)})")
            return ""

    def _download_from_url(self, image_url, dest_path):
        image_data = self._urlopen_safe(image_url)
        with open(dest_path,'wb') as file:
            file.write(image_data)
        print(f"Downloaded cover art: {dest_path}")

    def _query(self, artist, album):
        query_term = f"{artist} {album}"
        if album in artist:
            query_term = artist
        elif artist in album:
            query_term = album
        url = QUERY_TEMPLATE % quote(query_term)
        json = self._urlopen_text(url)
        if json:
            try:
                return eval(json)
            except Exception:
                pass
        return {}

    def _get_data(self, meta):
        artist = self.artist_normalizer.normalize(meta.artist)
        album = self.album_normalizer.normalize(meta.album)
        info = self._query(artist, album)
        if not info or not info['resultCount']:
            # no result found, try replacing any roman numerals
            artist = self.deromanizer.convert_all(artist)
            album = self.deromanizer.convert_all(album)
            info = self._query(artist, album)
        return (artist, album, info)

    def download(self, meta, art_path):
        (meta_artist, meta_album, info) = self._get_data(meta)
        if info:
            try:
                art = ""
                # go through albums, use exact match or first contains match if no exacts found
                for album_info in reversed(info['results']):
                    artist = self.artist_normalizer.normalize(album_info['artistName'])
                    album = self.album_normalizer.normalize(album_info['collectionName'])
                    
                    if not meta_artist in artist:
                        continue
                    if not meta_album in album:
                        continue
                    
                    art = album_info['artworkUrl100'].replace('100x100bb', self.size_suffix)
                    if meta_album == album:
                        break # exact match found
                if art:
                    self._download_from_url(art, art_path)
                    return True
            except Exception as error:
                print(f"ERROR encountered when downloading for artist ({meta_artist}) and album ({meta_album})")
                print(error)

        if self.verbose:
            print(f"Failed to find matching artist ({meta_artist}) and album ({meta_album})")
        return False
