import time
from urllib.request import Request, urlopen, HTTPError
from urllib.parse import urlparse, quote
from .normalizer import ArtistNormalizer, AlbumNormalizer
from .deromanizer import DeRomanizer
from .meta import MetaAudio

QUERY_TEMPLATE = "https://itunes.apple.com/search?term=%s&media=music&entity=%s"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36"
THROTTLED_HTTP_CODES = [403, 429]

class AppleDownloader(object):
    def __init__(self, verbose: bool, throttle: float, art_size: int, art_quality: int):
        quality_suffix = "bb" if art_quality == 0 else f"-{art_quality}"
        self.file_suffix = f"{art_size}x{art_size}{quality_suffix}"
        self.verbose = verbose
        self.throttle = throttle
        self.artist_normalizer = ArtistNormalizer()
        self.album_normalizer = AlbumNormalizer()
        self.deromanizer = DeRomanizer()
        
    def _urlopen_safe(self, url: str) -> str:
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

    def _urlopen_text(self, url: str) -> str:
        try:
            return self._urlopen_safe(url).decode("utf8")
        except Exception as error:
            if ("certificate verify failed" in str(error)):
                print(f"ERROR: Python doesn't have SSL certificates installed, can't access {url}")
                print("Please run 'Install Certificates.command' from your Python installation directory.")
            else:
                print(f"ERROR: reading URL ({url}): {str(error)})")
            return ""

    def _download_from_url(self, image_url: str, dest_path: str):
        image_data = self._urlopen_safe(image_url)
        if self.verbose:
            print(f"Downloading from: {image_url}")
        with open(dest_path,'wb') as file:
            file.write(image_data)
        print(f"Downloaded cover art: {dest_path}")

    def _query(self, artist: str, album: str, title: str) -> dict:
        token = album or title
        entity = "album" if album else "musicTrack"
        query_term = f"{artist} {token}"
        if token in artist:
            query_term = artist
        elif artist in token:
            query_term = token
        url = QUERY_TEMPLATE % (quote(query_term), entity)
        json = self._urlopen_text(url)
        if json:
            try:
                safe_json = json.replace('true', 'True').replace('false', 'False')
                return eval(safe_json)
            except Exception:
                pass
        return {}

    def _get_data(self, meta: MetaAudio) -> tuple[str, str, dict, bool]:
        artist = self.artist_normalizer.normalize(meta.artist)
        album = self.album_normalizer.normalize(meta.album)
        title = self.album_normalizer.normalize(meta.title)
        info = self._query(artist, album, title)
        if not info or not info.get('resultCount'):
            # no result found, try replacing any roman numerals
            artist = self.deromanizer.convert_all(artist)
            album = self.deromanizer.convert_all(album)
            info = self._query(artist, album, title)
        return (artist, album, info, len(album) == 0)

    def download(self, meta: MetaAudio, art_path: str) -> bool:
        (meta_artist, meta_album, info, title_only) = self._get_data(meta)
        if info:
            try:
                art = ""
                # go through albums, use exact match or first contains match if no exacts found
                results = reversed(info.get('results'))
                if title_only:
                    # if no album name provided, use earliest matching release
                    results = reversed(sorted(results, key=lambda x: x.get('releaseDate')))
                for album_info in results:
                    artist = self.artist_normalizer.normalize(album_info.get('artistName'))
                    album = self.album_normalizer.normalize(album_info.get('collectionName'))
                    
                    if not meta_artist in artist:
                        continue
                    if not title_only and not meta_album in album:
                        continue
                    
                    art = album_info.get('artworkUrl100').replace('100x100bb', self.file_suffix)
                    if not title_only and meta_album == album:
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
