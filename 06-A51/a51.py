import requests

class LSFR:
    def __init__(self,length:int, feedback_regs:list[bool], shift_reg:int ):
        self.length = length
        self.feedback_regs_mask = sum([2**r for r in feedback_regs])
        self.shift_reg_mask = 2**shift_reg

    def back_shift(self, state:int):
        # compute state one step back 
        feedback_regs_state = state&self.shift_reg_mask
        feedback_input = bin(feedback_regs_state).count('1') % 2 # calculate xor by counting the ones
        reversed_output

        return state >> 1 + "feedback_input" * 2**(self.length-1)
    
    def get_register_state(self,state,n):
        return (state >> n) & 1




def get_input():
    r = requests.post("https://krypto.ptera.cz/a5-2.php", data={"name": "Benda"})
    r = r.text
    r = r.split("\n")






print(r.text)