import time
from urllib.request import Request, urlopen
from urllib.parse import quote
from .normalizer import ArtistNormalizer, AlbumNormalizer

class AppleDownloader(object):
    def __init__(self, verbose, throttle):
        self.verbose = verbose
        self.throttle = throttle
        self.artist_normalizer = ArtistNormalizer()
        self.album_normalizer = AlbumNormalizer()
        
    def _urlopen_safe(self, url):
        q = Request(url)
        q.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        data = urlopen(q)
        return data.read()

    def _urlopen_text(self, url):
        try:
            return self._urlopen_safe(url).decode("utf8")
        except Exception as error:
            if ("certificate verify failed" in str(error)):
                print("ERROR: Python doesn't have SSL certificates installed, can't access " + url)
                print("Please run 'Install Certificates.command' from your Python installation directory.")
            else:
                print("ERROR: reading URL (%s): %s" % (url, str(error)))
            return ""

    def _download_from_url(self, image_url, dest_path):
        image_data = self._urlopen_safe(image_url)
        output = open(dest_path,'wb')
        output.write(image_data)
        output.close()
        print("Downloaded cover art: "  + dest_path)

    def download(self, meta, art_path):
        if self.throttle:
            time.sleep(self.throttle)
        artist_lower = self.artist_normalizer.normalize(meta.artist)
        album_lower = self.album_normalizer.normalize(meta.album)
        query = "%s %s" % (artist_lower, album_lower)
        if album_lower in artist_lower:
            query = artist_lower
        elif artist_lower in album_lower:
            query = album_lower

        url = "https://itunes.apple.com/search?term=%s&media=music&entity=album" % quote(query)
        json_text = self._urlopen_text(url)
        if json_text:
            try:
                info = eval(json_text)
                
                art = ""
                # go through albums, use exact match or first contains match if no exacts found
                for album_info in reversed(info['results']):
                    artist = self.artist_normalizer.normalize(album_info['artistName'])
                    album = self.album_normalizer.normalize(album_info['collectionName'])
                    
                    if not artist_lower in artist.lower():
                        continue
                    if not album_lower in album.lower():
                        continue
                    
                    art = album_info['artworkUrl100'].replace('100x100bb','500x500bb')
                    if album_lower == album.lower():
                        break # exact match found
                if art:
                    self._download_from_url(art, art_path)
                    return True
                elif self.verbose:
                    print("Failed to find matching artist (%s) and album (%s)" % (artist_lower, album_lower))
                    return False
            except Exception as error:
                print("ERROR encountered downloading for %s" % query)
                print(error)
        return False
