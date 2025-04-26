import requests

ciphertext = b"f183b083799d715be74880394b581e798f18349e313c0e9b4484b92f0b922ff66e7cfa83c9a15cc3a27191ce879e2223"
iv = b"30"*16

def int_to_hex(i:int) ->str :
    s = hex(i)[2:]
    s = "0"*(32-len(s))+s
    return s

def log(string):
    print(string)

def is_valid_padding(iv:int, block:int ) -> bool:
    waiting = True
    while(waiting):
        r = requests.post("http://krypto.ptera.cz/delphi.php", data={"ciphertext": int_to_hex(block), "iv": int_to_hex(iv)})
        if r.status_code != 200: 
            log(r)
        else : waiting = False
    return "OK" in r.text

def blockify(ciphertext: str ) -> list[int]:
    return [int(ciphertext[i*32:(i+1)*32],16) for i in range(len(ciphertext)//32)]

def decrypt_block(prev_block:int,block:int)-> int:
    iv = prev_block

    for targetted_padding in range(1,16):
        padding_part_hex = ("0"+hex(targetted_padding)[2:])
        if targetted_padding > 1: 
            iv ^= int(padding_part_hex *(targetted_padding-1),16) # add n-1 0x0n to guess the n-th padding

        found = False
        for i in range(256):
            xor_guess = (i<<((targetted_padding-1)*8))
            log(f" trying: {i}/255, {targetted_padding}/15")
            if is_valid_padding(iv ^ xor_guess,block):
                if (targetted_padding == 1): # cover false positives
                    if i == 0 :continue # trivial case
                    if not is_valid_padding(iv ^ xor_guess ^ (int("ff",16)<<8) ,block): # 0xff so that we change both nibbles of the byte
                        # if -2nd byte of the block is 0x02, guessing 0x02 for the last produces false positive
                        # => if changing the -2nd byte breaks the padding, we know this has occured
                        continue
                log("Zasah, potopena")
                iv ^= xor_guess # add n-th 0x0n to the padding
                iv ^= int(padding_part_hex *(targetted_padding),16) # remove all the padding (will be added in the next round)
                found = True
                break
        
        
        if not found: raise Exception("No suitable padding candidate found. WTF?")
    return iv ^ prev_block
        

    



if __name__ == "__main__":
    blocks = [int(iv,16)] + blockify(ciphertext)
    print(blocks)
    decrypted = decrypt_block(blocks[-2],blocks[-1])
    print(int_to_hex(decrypted))
    # _adding oracle n_ver went out of_fashion.
    # Padding oracle never went out of fashion.
    # KRYPTO{8L4M3_0R4CL3_0F_D3LPH1}

