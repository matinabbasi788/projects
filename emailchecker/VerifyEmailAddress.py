from pathlib import Path
import re
import smtplib
import dns.resolver
import socks
import socket
import requests
import configparser
import csv
import os


def read_config(filename, sec):
    config = configparser.ConfigParser()
    config.read(filename)
    return config[sec]


config = read_config('config.ini', 'Paths')
proxy_file = config['proxy_file']
mail_file = config['mail_file']
print("Proxy File:", Path(proxy_file).resolve())
print("Mail File:", Path(mail_file).resolve())
maillist = mail_file

# proxy list
def tunnel_through_proxy(proxy_type, proxy_host, proxy_port, user, passwd):
    try:
        if proxy_type == 'socks5':
            # Configure SOCKS proxy
            socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port, username=user, password=passwd)
            socket.socket = socks.socksocket  # Route all traffic through SOCKS proxy
        elif proxy_type == 'http':
            # Configure HTTP proxy
            proxies = {'http': f'http://{proxy_host}:{proxy_port}',
                       'https': f'http://{proxy_host}:{proxy_port}'}
            
        else:
            print(f"Unknown proxy type: {proxy_type}")
            return
        
        response = requests.get('http://httpbin.org/ip', timeout=5)
        
        # Make a request to a website to test the proxy
        
        if response.status_code == 200:
            print(f"Connection successful using {proxy_type} proxy: {proxy_host}:{proxy_port}")
            print("Your IP Address:", response.json()['origin'])
        else:
            print(f"Failed to connect using {proxy_type} proxy: {proxy_host}:{proxy_port}, status code: {response.status_code}")
    except Exception as e:
        pass
        # print(f"Error occurred while using proxy {proxy_host}:{proxy_port}")

def read_proxy_list(filename):
    proxy_list = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                proxy_type, proxy_host, proxy_port = parts
                proxy_list.append((proxy_type.lower(), proxy_host, int(proxy_port), None, None))
            if len(parts) == 5:
                proxy_type, proxy_host, proxy_port, user, passwd = parts
                proxy_list.append((proxy_type.lower(), proxy_host, int(proxy_port), user, passwd))
    return proxy_list

    
# Configure SOCKS proxy
# socks_proxy_host = '127.0.0.1'  # Replace with your SOCKS proxy host
# socks_proxy_port = 9150  # Replace with your SOCKS proxy port
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, socks_proxy_host, socks_proxy_port)
# socket.socket = socks.socksocket  # Route all traffic through SOCKS proxy


def verify(email):
    # Address used for SMTP MAIL FROM command
    fromAddress = 'corn@bt.com'

    # Simple Regex for syntax checking
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

    # Email address to verify
    addressToVerify = str(email)

    # Syntax check
    match = re.match(regex, addressToVerify.lower())
    if match is None:
        print('\033[91m' + 'DIE' + '\033[0m' + " => " + '\033[96m' + email + '\033[91m' + ' Bad Syntax', end='')
        stat = 'DIE'
        return stat, 'UNKNOWN'

    # Get domain for DNS lookup
    splitAddress = addressToVerify.split('@')
    domain = str(splitAddress[1])

    # MX record lookup
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
    except:
        print('\033[91m' + 'DIE' + '\033[0m' + " => " + '\033[96m' + email + '\033[90m' + ' No MX Record found for domain: ' + '\033[95m' + domain, end='')
        stat = 'DIE'
        return stat, domain

    # SMTP lib setup (use debug level for full output)
    server = smtplib.SMTP(timeout=45)
    server.set_debuglevel(0)

    # SMTP Conversation
    try:
        server.connect(mxRecord)
        server.helo(server.local_hostname)  # server.local_hostname(Get local server hostname)
        server.mail(fromAddress)
        code, message = server.rcpt(str(addressToVerify))
        server.quit()

        # Assume SMTP response 250 is success
        if code == 250:
            print('\033[92m' + "LIVE" + '\033[0m' + " => " + '\033[96m' + email + ' domain: ' + '\033[95m' + domain, end="")
            stat = 'LIVE'
        else:
            print('\033[91m' + "DIE" + '\033[0m' + " => " + '\033[96m' + email + ' domain: ' + '\033[95m' + domain, end="")
            stat = 'DIE'
    except smtplib.SMTPException as e:
        print('\033[1m' + "UNKNOWN" + '\033[0m' + " => " + '\033[96m' + email + '\033[91m' + 'SMTP Exception:', end='')
        stat = 'UNKNOWN'
        return stat, domain

    return stat, domain


class writter():
    def create_csv(self):
        with open('output.scv', 'w') as file:
            file.close()

    def write_csv(self, email, stat, domain):
        with open('output.scv', 'a') as file:
            writer = csv.writer(file)
            writer.writerows([[email, stat, domain]])


proxy_list = read_proxy_list('proxy_list.txt')
for proxy_type, proxy_host, proxy_port, user, passwd in proxy_list:
	tunnel_through_proxy(proxy_type, proxy_host, proxy_port, user, passwd)


out = writter()
if os.path.exists('output.scv'):
	result = input("i found `output.scv` file. Do you want to start over? y/n: ")

	if result == 'n':
		print(read_config('config.ini', 'Process')['current_line'])
		line_number = int(read_config('config.ini', 'Process')['current_line']) + 1

	else:
		line_number = 1
		out.create_csv()
else:
    line_number = 1
    out.create_csv()

counter = line_number 

print(f"start from line {line_number}")

with open(maillist, 'r') as mails:
    # for line in mails:
    for line_no, line in enumerate(mails, start=1):
        if line_no >= line_number:
            stat = 'UNKNOWN'
            domain = 'UNKNOWN'
            email = line.strip()
            print('\033[0m' + "[" + '\033[91m' + str(counter) + '\033[0m' + "] ", end="")
            try:
                stat, domain = verify(email)  # Update stat based on verify function's result
            except Exception as e:
                print('\033[1m' + "UNKNOWN" + '\033[0m' + " => " + f"an error with this email: {email}", end='')
                pass
            out.write_csv(email, stat, domain)
            config = configparser.ConfigParser()
            config.read('config.ini')
            config.set('Process', 'current_line', str(counter))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            print()
            counter += 1
    else:
        print("nothing to do.")
