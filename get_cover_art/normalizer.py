import re

class Normalizer(object):
    def __init__(self):
        self.substitutions = {
            '&': ' and ',
            '^the ': '',
            '^a ': '',
        }
        
    # TODO: deal reliably with roman numerals vs numbers
    def normalize(self, field):
        # this must come before removing punctuation
        for (key, value) in self.substitutions.items():
            field = re.sub(key, value, field, flags=re.IGNORECASE)
        
        # remove punctuation
        field = re.sub(r'[^\w\s]', '', field)

        # this will standardize whitespace to a single space between words
        return ' '.join(field.split()).lower()


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
        album = re.sub(r" [\(\[{]disc \d+[}\)\]]", "", album, flags=re.IGNORECASE)
        return super().normalize(album)
