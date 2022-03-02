from urllib.request import urlopen
from json import load

my_ip = urlopen('http://ip.42.pl/raw').read()
print('ip.42.pl', my_ip)

my_ip = load(urlopen('http://jsonip.com'))['ip']
print('jsonip.com', my_ip)

my_ip = load(urlopen('http://httpbin.org/ip'))['origin']
print('httpbin.org', my_ip)

my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
print('api.ipify.org', my_ip)