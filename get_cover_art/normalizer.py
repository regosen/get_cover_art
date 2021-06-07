import re

# based on https://www.tutorialspoint.com/roman-to-integer-in-python
def romanToInt(s):
    if not re.match(r"^[I|V|X|L|C|D|M]+$", s, flags=re.IGNORECASE):
        return 0
    roman = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000,'IV':4,'IX':9,'XL':40,'XC':90,'CD':400,'CM':900}
    i = 0
    num = 0
    s = s.upper()
    while i < len(s):
        if i+1<len(s) and s[i:i+2] in roman:
            num+=roman[s[i:i+2]]
            i+=2
        else:
            num+=roman[s[i]]
            i+=1
    return num

class Normalizer(object):
    def __init__(self):
        self.substitutions = {
            '&': ' and ',
            '^the ': '',
            '^a ': '',
        }
        
    def normalize(self, field):
        # this must come before removing punctuation
        for (key, value) in self.substitutions.items():
            field = re.sub(key, value, field, flags=re.IGNORECASE)
        
        # remove punctuation
        field = re.sub(r'[^\w\s]', '', field)

        # splitting + rejoining standardizes whitespace to a single space between words
        words = field.split()

        # also check if any word is a roman numeral, replace with numerical equivalent
        for i, word in enumerate(words):
            roman = romanToInt(word)
            if roman > 0:
                words[i] = str(roman)

        return ' '.join(words).lower()


class ArtistNormalizer(Normalizer):
    def normalize(self, artist):
        # If the artist name has a comma, strip it and swap the string segments.
        # e.g. "Beatles, The" -> "The Beatles", "Bowie, David" -> "David Bowie"
        (last, _sep, first) = artist.partition(',')
        if first:
            artist = '%s %s' % (first.strip(), last.strip())
        return super().normalize(artist)


class AlbumNormalizer(Normalizer):
    def normalize(self, album):
        # strip "(disc 1)", etc. from album names
        album = re.sub(r" [\(\[{]disc [\d|I|V|X]+[}\)\]]", "", album, flags=re.IGNORECASE)
        return super().normalize(album)
