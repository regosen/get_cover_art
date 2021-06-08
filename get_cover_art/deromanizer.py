import re

# based on https://www.tutorialspoint.com/roman-to-integer-in-python
class DeRomanizer(object):
    def __init__(self):
        self.romans = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000,'IV':4,'IX':9,'XL':40,'XC':90,'CD':400,'CM':900}

    def convert_word(self, word):
        if not re.match(r"^[I|V|X|L|C|D|M]+$", word, flags=re.IGNORECASE):
            return word

        i = 0
        num = 0
        word = word.upper()
        while i < len(word):
            if i+1<len(word) and word[i:i+2] in self.romans:
                num+=self.romans[word[i:i+2]]
                i+=2
            else:
                num+=self.romans[word[i]]
                i+=1
        return str(num)

    def convert_all(self, field):
        converted = [self.convert_word(word) for word in field.split()]
        return ' '.join(converted)
