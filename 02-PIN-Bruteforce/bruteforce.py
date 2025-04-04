import requests

def check_response(response):
    state = [False,False,False]
    if "Checksum does not match." not in response.text:
        state[0] = True
    if "First half does not match." not in response.text:
        state[1] = True
    if "Second half does not match." not in response.text:
        state[2] = True
    return state

class MockResponse:
    def __init__(self,text):
        self.text = text

def send(payload):
    return requests.post("http://krypto.ptera.cz/wps.php", data={"pin": payload})
    pin = 57839068
    text = ""
    if payload%10000 != pin%10000:
        text += "Second half does not match."
    if payload//10000 != pin//10000:
        text += "First half does not match."
    if sum(map(int, str(payload//10)))%10 != payload%10:
        text +="Checksum does not match."
    response=object()

    response = MockResponse(text)
    return response




def phase_1(send):
    for i in range(10000):
        payload = i*10000+i
        response = send(payload)
        state = check_response(response)
        if state[1]:
            return i, 0
        if  state[2]:
            return i, 1
        
def combine (prev_part, new_part, chosen_part):
    if chosen_part == 0:
        a = prev_part*10000+new_part*10
        checksum = sum(map(int, str(a)))%10
        a+=checksum
        return a
    else:
        a = new_part*100000+prev_part
        a_last = a % 10
        a_all_but_last =(a//10) * 10
        incomplete_checksum =  sum(map(int, str(a_all_but_last)))%10
        correction = (a_last-incomplete_checksum)%10
        return a + correction *10000


def phase_2(halfcode, chosen_part):
    for i in range(1000):
        pin_try = combine (halfcode, i, chosen_part)
        response = send(pin_try)

        if all(check_response(response)):
            print(f"PIN: {pin_try}")
            print(response.text)
            return pin_try
    


if __name__ == "__main__":
    halfcode, chosen_part = phase_1(send)
    l=["First","Second"]
    print(f"{l[chosen_part]} part is {halfcode}")
    phase_2(halfcode, chosen_part)



