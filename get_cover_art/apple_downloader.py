import re

from urllib.request import Request, urlopen
from urllib.parse import quote

class AppleDownloader(object):
    def __init__(self):
       return
        
    def _urlopen_safe(self, url):
        q = Request(url)
        q.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
        data = urlopen(q)
        return data.read()

    def _urlopen_text(self, url):
        try:
            return self._urlopen_safe(url).decode("utf8")
        except:
            print("ERROR: reading URL: %s" % url)
            return ""

    def _dload(self, image_url, dest_path):
        image_data = self._urlopen_safe(image_url)
        output = open(dest_path,'wb')
        output.write(image_data)
        output.close()
        print("Downloaded cover art: "  + dest_path)

    def dload_apple_art(self, meta, art_path):
        artist = meta.artist
        album = meta.album
        query = "%s %s" % (artist, album)
        if album in artist:
            query = artist
        elif artist in album:
            query = album

        url = "https://music.apple.com/search?term=%s" % quote(query)
        source = self._urlopen_text(url)
        artist_lower = artist.lower()
        album_lower = album.lower()

        matcher = re.compile(r'<script type="fastboot/shoebox" id="shoebox-media-api-cache-amp-music">(.+?)</script', re.I)
        json = matcher.findall(source)
        if json:
            try:
                info = eval(json[0])
                keys = filter(lambda x: x != '\uf8ff.storefronts.us', list(info.keys()))
                key = next(keys)
                data = eval(info[key].replace('false','False').replace('true','True'))
                albums = data['d']['results']['album']['data']
                art = ""
                # go through albums, use exact match or first contains match if no exacts found
                for album_info in reversed(albums):
                    attr = album_info['attributes']
                    album = attr['name'].lower()
                    artist = attr['artistName'].lower()
                    
                    if artist_lower != artist.lower():
                        continue
                    if not album_lower in album.lower():
                        continue
                    
                    art = attr['artwork']['url'].replace('{w}','500').replace('{h}','500')
                    if album_lower == album.lower():
                        break # exact match found
                if art:
                    self._dload(art, art_path)
                    return True
            except Exception as error:
                print("ERROR encountered downloading for %s" % query)
                print(error)
        return False
