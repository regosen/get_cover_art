import re, time

from urllib.request import Request, urlopen
from urllib.parse import quote

# from https://stackoverflow.com/questions/10294032/python-replace-typographical-quotes-dashes-etc-with-their-ascii-counterparts
NORMALIZATION_TABLE = dict( [ (ord(x), ord(y)) for x,y in zip( u"‘’´“”–-[{}]",  u"'''\"\"--(())") ] ) 

def normalize_field(field):
    return field.lower().strip().translate(NORMALIZATION_TABLE)

def normalize_artist_name(artist):
    artist_norm = normalize_field(artist)
    if artist_norm.endswith(', the'):
        # account for "The X" vs "X, The"
        artist_norm = "the " + artist_norm[:-5]
    return artist_norm

def normalize_album_name(album):
    album_norm = normalize_field(album)
    # strip "(disc 1)", etc. from album name
    album_norm = re.sub(r" \(disc \d+\)", "", album_norm)
    return album_norm

class AppleDownloader(object):
    def __init__(self, verbose, throttle):
        self.verbose = verbose
        self.throttle = throttle
        
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

    def _dload(self, image_url, dest_path):
        image_data = self._urlopen_safe(image_url)
        output = open(dest_path,'wb')
        output.write(image_data)
        output.close()
        print("Downloaded cover art: "  + dest_path)

    def download(self, meta, art_path):
        if self.throttle:
            time.sleep(self.throttle)
        artist_lower = normalize_artist_name(meta.artist)
        album_lower = normalize_album_name(meta.album)
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
                    artist = normalize_artist_name(album_info['artistName'])
                    album = normalize_album_name(album_info['collectionName'])
                    
                    if not artist_lower in artist.lower():
                        continue
                    if not album_lower in album.lower():
                        continue
                    
                    art = album_info['artworkUrl100'].replace('100x100bb','500x500bb')
                    if album_lower == album.lower():
                        break # exact match found
                if art:
                    self._dload(art, art_path)
                    return True
                elif self.verbose:
                    print("Failed to find matching artist (%s) and album (%s)" % (artist_lower, album_lower))
                    return False
            except Exception as error:
                print("ERROR encountered downloading for %s" % query)
                print(error)
        return False
