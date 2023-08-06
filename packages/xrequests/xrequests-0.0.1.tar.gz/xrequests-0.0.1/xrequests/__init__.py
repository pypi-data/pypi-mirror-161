import colorama, httpx

RS = colorama.Fore.RESET
CR = colorama.Fore.LIGHTRED_EX
CG = colorama.Fore.LIGHTGREEN_EX


jays_fav_site="pornhub.com/gayporn"

def print(stat:bool, *, msg):
    if stat == True:
        return print(f"{CG}[{RS} success {CG}]{RS} {msg}")
    

def send_request(type:str, url:str):
    if type == "GET":
        return httpx.get(url)
    if type == "POST":
        return httpx.post(url)
    if type == "DELETE":
        return httpx.delete(url)
    if type == "PATCH":
        return httpx.patch(url)
    else:
        return "TypeError: Invalid Request Method."