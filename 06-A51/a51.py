import requests
from collections import deque

class LFSR:
    def __init__(self,length:int, feedback_regs:list[bool], shift_reg:int ):
        self.length = length
        self.feedback_regs_mask = sum([1<<r for r in feedback_regs])
        self.shift_reg = shift_reg

    def shift(self, state:int)->int:
        feedback_regs_state = state&self.feedback_regs_mask
        first_reg_val = bin(feedback_regs_state).count('1') % 2 # calculate xor by counting the ones
        return (state << 1) % (1 << self.length) ^ first_reg_val # shift registers, remove the overflowing bit and append the new bit
        

    def shift_back(self, state:int)->int:
        # compute state one step back
        first_reg_val = state % 2
        state = state >> 1
        feedback_regs_state = state&self.feedback_regs_mask
        last_reg_val = (bin(feedback_regs_state).count('1') +first_reg_val) % 2
        return state ^ (last_reg_val << (self.length-1))

    def get_shift_reg_val(self,state):
        return (state >> self.shift_reg) & 1

class A51State:
    def __init__(self, lsfr_states:list[int], prev_a51_state):
        self.states = lsfr_states
        self.prev = prev_a51_state
        self.next = []
        self.depth = prev_a51_state.depth if prev_a51_state else 0
    
    def __repr__(self):
        return "["+", ".join([int_to_bin(state) for state in self.states])+"]"
    def __str__(self):
        return self.__repr__()
    def __eq__(self, other):
        if not isinstance(other, A51State):
            raise Exception(f"NotImplementedError(), cannot compare variables of types {type(self)} and {type(other)}")
        
        for self_state, other_state in zip(self.states,other.states):
            if self_state != other_state:
                return False
        return True
    def remove(self):
        self.prev.next.remove(self)
        if len(self.prev.states) == 0:
            self.prev.remove()

class A51:
    def __init__(self):
        self.lfsrs = [
            LFSR(19,[18,17,16,13],8),
            LFSR(22,[21,20],10),
            LFSR(23,[22,21,20,7],10)
        ]
    def step(self,a51_state:A51State)->A51State:
        states = a51_state.states
        new_states = []
        shift_reg_vals = [lfsr.get_shift_reg_val(state) for state, lfsr in zip(states,self.lfsrs)]
        majority = 1 if sum(shift_reg_vals)>=2 else 0

        for state, lfsr in zip(states,self.lfsrs):
            if lfsr.get_shift_reg_val(state) == majority:
                new_state =lfsr.shift(state)
            else:
                new_state = state
            new_states.append(new_state)

        return A51State(new_states,None)

    def step_back(self,a51_states:A51State,stepback_mask:tuple[int])->A51State:
        """
        Steps back the LSFRs according to the stepback_mask
        """
        states  = a51_states.states
        new_states = []
        for state, lfsr, should_step_back in zip(states, self.lfsrs,stepback_mask):
            if should_step_back:
                new_state = lfsr.shift_back(state)
            else:
                new_state = state
            new_states.append(new_state)
        return A51State(new_states,a51_states)



def int_to_bin(i:int)->str:
        b = bin(i)[2:].zfill(23)
        return b

def get_input()->str:
    r = requests.post("https://krypto.ptera.cz/a5-2.php", data={"name": "Benda"})
    return r.text

def process_input()->A51State:
    r = get_input()
    r = r.split("\n")[1:4]
    states = [int(line[5:-1],2) for line in r]

    return A51State(states,None)





if __name__ == "__main__":
    valid_stepbacks = [
        (True,True,True),
        (False,True,True),
        (True,False,True),
        (True,True,False),
    ]
    stop_depth = 10
    
    initial_a51_state = process_input()
    state_queue = deque([initial_a51_state])
    a51 = A51()

    while True:
        if len(state_queue) == 0:
            break
        a51_state = state_queue.popleft()
        if a51_state.depth >= stop_depth:
            break

        found_next_state = False
        for stepback_mask in valid_stepbacks:
            stepped_a51_state = a51.step_back(a51_state,stepback_mask)
            reverted_a51_state = a51.step(stepped_a51_state)
            if reverted_a51_state == a51_state:
                found_next_state = True
                a51_state.next.append(stepped_a51_state)
                state_queue.append(stepped_a51_state)

        if not found_next_state:
            a51_state.remove()

    print("t-0 :",[initial_a51_state])

    a51_state = initial_a51_state
    for i in range(stop_depth):
        print(f"t-{i+1} :",a51_state.next)
        if len(a51_state.next) == 0:
            break
        a51_state = a51_state.next[0]

# [1010000000000011010, 0100100110100110000011, 00011101001101110100110]
# KRYPTO{N0T_3V3N_0UR_PH0N3S_4R3_S3CUR3}

# r = requests.post("https://krypto.ptera.cz/a5-2.php", data={"name": "Benda", "R1": "1010000000000011010","R2": "0100100110100110000011","R3": "00011101001101110100110"})
# print(r.text)









