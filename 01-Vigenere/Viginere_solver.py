from Vigenere import Vigenere_string

class Solver:
    def __init__(self, cybertext):
        self.__ct = cybertext
        self.__alphabeth_fequencies = {'U': 0.037, 'B': 0.016, 'D': 0.034, 'M': 0.022, 'T': 0.079, 'K': 0.012, 'I': 0.061, 'R': 0.054, 'O': 0.076, 'L': 0.044, 'V': 0.009, 'H': 0.06, '.': 0.022, "'": 0.01, '?': 0.005, 'Y': 0.025, '!': 0.015, 'C': 0.022, 'N': 0.06, 'E': 0.106, 'S': 0.053, ',': 0.021, 'F': 0.014, 'Q': 0.002, 'P': 0.013, 'J': 0.001, 'A': 0.075, 'G': 0.027, 'Z': 0.0, ';': 0.0, 'W': 0.023, 'X': 0.001}

    def __count_char_frequency(self,ct):
        counts  = dict()
        for c in ct:
            if c in counts.keys():
                counts[c] += 1
            else:
                counts[c] = 1
        return counts

    def __coincidence_index(self,ct):
        counts  = self.__count_char_frequency(ct)

        l = len(ct)
        return sum([counts[k]*(counts[k]-1) for k in counts.keys()])/(l*(l-1))

    def __relative_coincidence_index(self,ct):
        counts  = self.__count_char_frequency(ct)

        l = len(ct)
        return sum([counts[k]*self.__alphabeth_fequencies[k] for k in counts.keys()])/l
    
    def __find_key_length(self,start_len=1, max_len=20):
        
        last_biggest = 0
        for k in range(start_len,max_len+1):
            coincidence_index_list=[]
            for offset in range(k):
                skipped_ct = self.__ct[offset::k]
                coincidence_index_list.append(self.__coincidence_index(skipped_ct))

            coincidence_index = sum(coincidence_index_list)/len(coincidence_index_list)

            if last_biggest < coincidence_index:
                last_biggest = coincidence_index
                print(k,coincidence_index, "<--- NEW BEST")
            else: print(k,coincidence_index)

        guessed_key_length = 0
        print("Enter your guess for the lenght of the key:")
        while True:
            try:
                guessed_key_length = int(input())
                if guessed_key_length > 0:
                    break
            except:
                pass
            print("Entered invalid value. Try again:")
        self.__key_length = guessed_key_length
        print("\n")

    def __find_key_letter(self, ct):
        ct = Vigenere_string(ct)
        key_guess = Vigenere_string("")
        rci_list = []
        for k in self.__alphabeth_fequencies.keys():
            key_guess.string = k
            shifted_ct = ct - key_guess
            rci = self.__relative_coincidence_index(shifted_ct.string)
            rci_list.append((k,rci))
        
        rci_list.sort(key = lambda i: i[1], reverse=True)

        for i in range(min(len(self.__alphabeth_fequencies),7)):
            print(rci_list[i][0],rci_list[i][1])
        print("...")

    def __find_key(self):
        key_lenght = self.__key_length
        key_guess = ""
        for i in range(key_lenght):
            print(f"Guess the key ({i+1}/{key_lenght}). Current guess: {key_guess}")
            self.__find_key_letter(self.__ct[i::key_lenght])

            letter_guess = ""
            print("Enter your guess:")
            while True:
                letter_guess = input()
                if letter_guess in self.__alphabeth_fequencies.keys():
                    break
                print("Entered letter not present in the alphabet. Try again:")

            key_guess += letter_guess
            print("\n")

        self.__key = key_guess

    def __decrypt(self):
        print(f"Found key: {self.__key}")
        ct = Vigenere_string(self.__ct)
        key = Vigenere_string(self.__key)
        pt = ct - key
        print("Corresponding plaintext:")
        print(pt.string)



    def solve(self):
        self.__find_key_length(max_len=20)
        self.__find_key()
        self.__decrypt()


if __name__ == "__main__":
    ct = "NHKHY;''DKGAC!ZW'MH!.TWSZXTCGAOM,RDSE.HPYU';!HY;X'JB'XXNGNNBLQXNJ!HYUEXE.BER;GNIYTG.'GH.TG.'JNGFHDSDNYF.Q;BYYE.UA;FNTTDSE.GYC'GQHI!RMNHKHY;.JGYY;UVGNNWBO.GKESF.Q;BYYE.BZOUZBOBHNZ?ERX';E!EA;JH!Q!UBZK!TTTS';EHE.;JB?!L;HXOGHXXWGNZHE.;JBOY!VB'QNYUR;GNIYTHVV?NUFTYTN!!DRN'HLYE.UA;FNTTDSDNYLDUVHPHY;DSKIX!O,MOIQO;BZSLTTBMGNNB,URMO'HE.;JBOEYU'FNZBU,BZHZXTUVNH!UBAXGE?M;BCGNHISUUR,O!O;YAMEMD,XG!RB'KCVMOHLQXNJCG!OVYK!RM"
    solver = Solver(ct)
    solver.solve()