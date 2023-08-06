# RandProx
Get random proxy from github lists via python   
supports socks5, socks4 and http
supports speedx, shiftytr, monosans, mmpx12 

# USAGE EXAMPLES
import randprox  
socks5_proxy = randprox.socks5()  
socks4_proxy = randprox.socks4)  
http_proxy = randprox.http()
or supply your own lists like  
http_proxy = randprox.socks5(raw.github.com/user_supplied_list)  
or pass a supported list like  
http_proxy = randprox.socks5(speedx)  
