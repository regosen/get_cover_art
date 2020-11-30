import re

from urllib.request import Request, urlopen
from urllib.parse import quote

def normalize_album_name(album):
    # HACK: strip "disc 1", etc. from album name
    return album.lower().split("(disc ")[0].split("[disc ")[0].strip()

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
        artist_lower = meta.artist.lower()
        album_lower = normalize_album_name(meta.album)
        query = "%s %s" % (artist_lower, album_lower)
        if album_lower in artist_lower:
            query = artist_lower
        elif artist_lower in album_lower:
            query = album_lower

        url = "https://itunes.apple.com/search?term=%s&media=music&entity=album" % quote(query)
        print(url)
        json_text = self._urlopen_text(url)
        if json_text:
            try:
                info = eval(json_text)
                
                art = ""
                # go through albums, use exact match or first contains match if no exacts found
                for album_info in reversed(info['results']):
                    album = album_info['collectionName'].lower()
                    artist = album_info['artistName'].lower()
                    
                    if artist_lower != artist.lower():
                        continue
                    if not album_lower in album.lower():
                        continue
                    
                    art = album_info['artworkUrl100'].replace('100x100bb','500x500bb')
                    if album_lower == album.lower():
                        break # exact match found
                if art:
                    self._dload(art, art_path)
                    return True
            except Exception as error:
                print("ERROR encountered downloading for %s" % query)
                print(error)
        return False
