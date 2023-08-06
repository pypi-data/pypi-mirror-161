import requests, random
def socks5():
     r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port

def http():
     r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port

def socks4():
     r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port


