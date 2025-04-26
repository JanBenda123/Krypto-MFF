import requests
import random
from concurrent.futures import ThreadPoolExecutor
from statistics import median

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Possible inputs:
#   'single char'   -   appends the character to the flag guess - must come from the alphabeth defined in code
#   'empty string'  -   repeats the guess with current flag
#   ..              -   removes last character from the guessed flag
#   -repeats <int>  -   modifies the number of repeats of the guess in a single payload 
#   -fillsize <int> -   modifies the fill size between guesses in a single payload 
#   -rounds <int>   -   modifies the number of rounds in a guess 
#   -method <str>   -   changes how are guesses ranked based on obtained data
#                       - sum   : sums the lenghts of outputs from each try
#                       - avg   : counts how many times was letter more compressed than average
#                       - med   : counts how many times was letter more compressed than 50% of results (more than median case)
#                       - first : counts how many times was letter among the most compressed in each run 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PayloadGenerator:
    def __init__(self,guess_repeats = 10, fill_size = 8):
        self.guess_repeats =guess_repeats
        self.fill_size=fill_size

    @staticmethod
    def __generate_fill(N): 
        return ''.join(random.choices(alphabeth, k = N))
    
    def generate_payloads(self,flag_guess,alphabeth):
        # All payloads are of form:
        #       RF_0 + FLAG_GUESS + RF_1 + FLAG_GUESS + ... + FLAG_GUESS + RF_N
        # Random fills are the same for all payloads to minimize the influence of randomness
        first_fill = self.__generate_fill(self.fill_size)
        payloads = [first_fill for _ in alphabeth]
        for _ in range(self.guess_repeats):
            fill = self.__generate_fill(self.fill_size)                                     
            payloads = [ p + flag_guess + c + self.__generate_fill(self.fill_size) for p, c in zip(payloads, alphabeth)]
#            payloads = [ p + flag_guess + c + fill for p, c in zip(payloads, alphabeth)]
        return payloads

class ParallelRequest:
    def __init__(self, threads):
        self.threads = threads
        self.executor = ThreadPoolExecutor(max_workers = threads)
    
    def _post(self,url, payloads):
        responses = self.executor.map(lambda payload:requests.post(url, data={"plaintext": payload}), payloads)
        responses = list(responses) # order of responses does NOT get shuffled
        
        for response in responses:
            if response.status_code // 100 !=2:
                print("bad response: ", response.status_code)
        return responses
    def post(self,url, payloads):
        responses =[]
        for payload in payloads:
            responses.append(requests.post(url, data={"plaintext": payload}))

        
        for response in responses:
            if response.status_code // 100 !=2:
                print("bad response: ", response.status_code)
        return responses

class ResultAggregator:
    # Contains methods that aggregate results and rank candidates
    @staticmethod
    def sum(round_results):
        # Add the results from all rounds to see, 
        # which character had the biggest compression on average
        round_results_sums = [0]*len(alphabeth)
        for rnd in round_results:
            for i, encr_length in enumerate(rnd):
                round_results_sums[i] += encr_length
        candidates = list(zip(alphabeth,round_results_sums))
        candidates.sort(key = lambda x:x[1])
        return candidates
    
    @staticmethod
    def count_first_place_occurences(round_results):
        # Counts how many times each letter performed the best
        round_results_firsts = [0]*len(alphabeth)
        for rnd in round_results:
            rnd = list(rnd)
            min_encr_len = min(rnd)
            for i, encr_length in enumerate(rnd):
                round_results_firsts[i] += int(encr_length == min_encr_len) 
        candidates = list(zip(alphabeth,round_results_firsts))
        candidates.sort(key = lambda x:x[1],reverse=True)
        return candidates

    @staticmethod 
    def count_above_average_occurences(round_results):
        # Count how many times the letter got compressed better than average
        round_results_above_avg = [0]*len(alphabeth)
        for rnd in round_results:
            rnd = list(rnd)
            avg_encr_len = sum(rnd)/len(rnd)
            for i, encr_length in enumerate(rnd):
                round_results_above_avg[i] += int(encr_length < avg_encr_len) 
        candidates = list(zip(alphabeth,round_results_above_avg))
        candidates.sort(key = lambda x:x[1],reverse=True)
        return candidates

    @staticmethod 
    def count_above_median_occurences(round_results):
        # Count how many times the letter got compressed better than average
        round_results_above_avg = [0]*len(alphabeth)
        for rnd in round_results:
            rnd = list(rnd)
            med_encr_len = median(rnd)
            for i, encr_length in enumerate(rnd):
                round_results_above_avg[i] += int(encr_length < med_encr_len) 
        candidates = list(zip(alphabeth,round_results_above_avg))
        candidates.sort(key = lambda x:x[1],reverse=True)
        return candidates



# alphabeth =  "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_}|{=[]<>-/\°;,?!.#@&$*"
alphabeth =  "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_}{" # maybe we'll get better results if we ommit characters which are likely not there. Who knows...
flag = "KRYPTO{0H_G0D"
rounds = 1

aggregator_methods={
    "sum":      ResultAggregator.sum,
    "first":    ResultAggregator.count_first_place_occurences,
    "avg":      ResultAggregator.count_above_average_occurences,
    "median":   ResultAggregator.count_above_median_occurences
                    }
chosen_agg_method = "sum"



payload_gen = PayloadGenerator()
parallel_request = ParallelRequest(threads=len(alphabeth))
while True:
    round_results = []

    # Multiple rounds eliminate noise introduced by random fill and block encoding
    for _ in range(rounds): 
        payloads = payload_gen.generate_payloads(flag, alphabeth)
        responses = parallel_request.post("https://krypto.ptera.cz/depressed_oracle.php", payloads) 
        response_lenghts = map(lambda response: len(response.text), responses)
        round_results.append(response_lenghts)

    candidates = aggregator_methods[chosen_agg_method](round_results)

    print((
        "\n\n"
        "Current parameters are:\n"
        f"\tguess_repeats: {payload_gen.guess_repeats}\n"
        f"\tfillsize: {payload_gen.fill_size}\n"
        f"\trounds: {rounds}\n"
        f"\taggregation method: {chosen_agg_method}\n"
        f"Current flag guess is: {flag}"
    ))
    print("The best candidates for the next flag character are:")

    best_val = candidates[0][1]
    for i in range(30):
        cand = candidates[i]
        print("\t",cand[0], cand[1], "<-"*(cand[1] == best_val))


    print("Make a choice (to go back enter \"..\"):")
    choice = input()
    try:
        if choice == "..":
            flag = flag [:-1]
            continue
        if choice.startswith("-repeats "):
            payload_gen.guess_repeats = int(choice[9:])
            continue
        if choice.startswith("-rounds "):
            rounds = int(choice[8:])
            continue
        if choice.startswith("-fillsize "):
            payload_gen.fill_size = int(choice[10:])
            continue
        if choice.startswith("-method "):
            method = choice[8:].strip()
            if method in aggregator_methods.keys():
                chosen_agg_method = method
            else:
                print(f"Method {method} not recognised.")
            continue
        if choice not in alphabeth:
            print("Unrecognised input. Try again.")
            continue
        flag += choice
    except:
        print("Something went wrong")




