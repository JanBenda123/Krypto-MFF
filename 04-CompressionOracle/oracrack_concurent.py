import requests
import random
from concurrent.futures import ThreadPoolExecutor


alphabeth = "QWERTZUIOPASDFGHJKLYXCVBNM1234567890_}{?!.#@&$*" # used alphabetth
flag = "KRYPTO"

guess_repeats = 15 
fill_size = 8
rounds = 20

def generate_fill(N): 
    return ''.join(random.choices(alphabeth, k=N))

def send(payload):
    return requests.post("http://krypto.ptera.cz/depressed_oracle.php", data={"plaintext": payload})

def generate_payloads():
    # random fills are the same for all payloads to minimize the influence of randomness
    # payloads differ only on the position of chars currently guessed
    first_fill = generate_fill(fill_size)
    payloads = [first_fill for c in alphabeth]
    for _ in range(guess_repeats):
        fill = generate_fill(fill_size)                                     
        payloads = [ p+ flag+c+fill for p,c in zip(payloads,alphabeth)]
    return payloads

def question_round(executor):
    payloads = generate_payloads()
    candidates =[]
    
    responses = list(executor.map(send, payloads)) # runs send() for each payload in parallel using threads/processes
    for response in responses:
        candidates.append(len(response.text))
    return candidates

def get_candidates(rounds):
    # runs the same set of request multiple times ()
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
    return candidates




while True:
    candidates = get_candidates(rounds)

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
        guess_repeats = int(choice[3:])
        continue
    if choice.startswith("-fs "):
        fill_size = int(choice[4:])
        continue
    if choice not in alphabeth:
        print("Wrong character entered")
        continue
    flag += choice




