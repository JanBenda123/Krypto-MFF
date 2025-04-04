class Char:
    char_list = "!',.;?ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    @staticmethod
    def add(a,b):
        a=Char.char_list.index(a)
        b=Char.char_list.index(b)
        return Char.char_list[(a+b) % len(Char.char_list)]
    
    @staticmethod
    def sub(a,b):
        a=Char.char_list.index(a)
        b=Char.char_list.index(b)
        return Char.char_list[(a-b) % len(Char.char_list)]
        
class Char_XOR:
    char_list = "!',.;?ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    @staticmethod
    def add(a,b):
        a=Char.char_list.index(a)
        b=Char.char_list.index(b)
        return Char.char_list[(a^b) % len(Char.char_list)]
    
    @staticmethod
    def sub(a,b):
        a=Char.char_list.index(a)
        b=Char.char_list.index(b)
        return Char.char_list[(a^b) % len(Char.char_list)]
        

class Vigenere_string:
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return self.string
    def __add__(self, other):
        res = []
        for i, e in enumerate(self.string):
            res.append(Char_XOR.add(e,other.string[i % len(other.string)]))
        res = "".join(res)
        return Vigenere_string(res)
    
    def __sub__(self, other):
        res = []
        for i, e in enumerate(self.string):
            res.append(Char_XOR.sub(e,other.string[i % len(other.string)]))
        res = "".join(res)
        return Vigenere_string(res)

            





if __name__ == "__main__":
    pt = Vigenere_string("ZPRAVA")
    key = Vigenere_string("KLIC")

    ct = pt + key
    print(ct)
    print(ct - key)
