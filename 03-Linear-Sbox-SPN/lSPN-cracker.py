import requests
import galois
import numpy as np

target = "b048400a537a207ae12b20c8812b647bd1c8912b30c8557a"
GF2 = galois.GF(2)


def bytestring_to_GF(bs):
    l = lambda x: GF2([int(b,16) for hex_digit in x for b in format(int(hex_digit, 16), '04b')])
    return [l(bs[i:i+4]) for i in range(0, len(bs), 4)]


def ask(plaintext:str) -> requests.Response:
    resp = requests.post("http://krypto.ptera.cz/linear.php", data={"plaintext":plaintext}).text
    return bytestring_to_GF(resp)



lspn_zero = ask("\x00\x00")[0]

lspn_base = []
bit_base_cannonic = ["\x00\x01","\x00\x02","\x00\x04","\x00\x08","\x00\x10","\x00\x20","\x00\x40","\x00\x80","\x01\x00","\x02\x00","\x04\x00","\x08\x00","\x10\x00","\x20\x00","\x40\x00","\x80\x00"]
for e_i in bit_base_cannonic:
    lspn_base.append(ask(e_i)[0]+lspn_zero)
matrix = GF2(lspn_base)

# lspn_zero = GF2([1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1])
# matrix = GF2([
#     [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#     [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
# ])

inv_matrix = np.linalg.inv(np.transpose(matrix))
encrypted_bytes = bytestring_to_GF(target)

decrypted_bytes = [inv_matrix @ (block + lspn_zero) for block in encrypted_bytes]
decrypted_ints = [int(''.join(map(str, block[::-1])),2) for block in decrypted_bytes]

decrypted_ints=[(i // 256, i %256) for i in decrypted_ints]
decrypted_ints = [item for tup in decrypted_ints for item in tup]
decrypted_ascii = [chr(i) for i in decrypted_ints]

cracked = ''.join(decrypted_ascii)

print(cracked) # Wasnt_that_hard,_was_it?
response = requests.post("http://krypto.ptera.cz/linear.php", data={"answer": cracked}) # KRYPTO{L1N3AR1TY_SUCKS}
print(response.text)


