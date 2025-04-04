import requests
import random
from concurrent.futures import ThreadPoolExecutor


alphabeth = "QWERTZUIOPASDFGHJKLYXCVBNM1234567890_}{?!.#@&$*"

def generate_fill(N):
    return ''.join(random.choices(alphabeth, k=N))

def send(payload):
    return requests.post("http://krypto.ptera.cz/depressed_oracle.php", data={"plaintext": payload[1]})

def question_round(executor):
    first_fill = generate_fill(fill_size)
    payloads = [first_fill for c in alphabeth]
    for _ in range(repeats):
        fill = generate_fill(fill_size)
        payloads = [ p+ flag+c+fill for p,c in zip(payloads,alphabeth)]


    candidates =[]
    
    responses = list(executor.map(send, payloads))
    for response in responses:
        candidates.append(len(response.text))
    return candidates


flag = "KRYPTO"

repeats = 10
fill_size = 16

rounds = 20

while True:
    round_results = []
    with ThreadPoolExecutor(max_workers=len(alphabeth)) as executor:
        for _ in range(rounds):
            round_results.append(question_round(executor))


    candidates = [0]*len(alphabeth)
    for rnd in round_results:
        for i, encr_length in enumerate(rnd):
            candidates[i]+=encr_length


    candidates=list(zip(alphabeth,candidates))
    candidates.sort(key=lambda x:x[1])

    print("current flag guess is: ", flag)
    print("the best candidates are:")
    for i in range(30):
        cand = candidates[i]
        print(cand[0], cand[1])
    print("make a choice (to go back enter \"..\"):")
    choice = input()
    print("\n")
    if choice == "..":
        flag = flag [:-1]
        continue
    if choice == ".":
        continue
    if choice.startswith("-r "):
        repeats = int(choice[3:])
        continue
    if choice.startswith("-fs "):
        fill_size = int(choice[4:])
        continue
    if choice not in alphabeth:
        print("Wrong character entered")
        continue
    flag += choice




