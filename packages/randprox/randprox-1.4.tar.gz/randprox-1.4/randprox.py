import requests, random

def socks5(link="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"):
     if link.lower() == 'speedx':
          r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt")
     elif link.lower() == 'shiftytr':
          r = requests.get("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt")
     elif link.lower() == 'monosans':
          r = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt")
     elif link.lower() == 'mmpx12':
          r = requests.get("https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port

def http(link="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"):
     if link.lower() == 'speedx':
          r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt")
     elif link.lower() == 'shiftytr':
          r = requests.get("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt")
     elif link.lower() == 'monosans':
          r = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt")
     elif link.lower() == 'mmpx12':
          r = requests.get("https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port

def socks4(link="https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"):
     if link.lower() == 'speedx':
          r = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt")
     elif link.lower() == 'shiftytr':
          r = requests.get("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt")
     elif link.lower() == 'monosans':
          r = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt")
     elif link.lower() == 'mmpx12':
          r = requests.get("https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt")
     proxy_list = r.text.split('\n')
     proxy_ip_port = random.choice(proxy_list)
     return proxy_ip_port
