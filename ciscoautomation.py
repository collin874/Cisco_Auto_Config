from netmiko import ConnectHandler
from netmiko import Netmiko
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException
import telnetlib
from scapy.all import ARP, Ether, srp
import time

start_time = time.time()

target_ip = "192.168.122.1/24"  # target IP range
arp = ARP(pdst=target_ip)
ether = Ether(dst="ff:ff:ff:ff:ff:ff")
packet = ether/arp
result = srp(packet, timeout=3, verbose=0)[0]
clients = []
file = open('ip.txt', 'w+')   # file Scapy writes the IP list to for the netmiko forloop 

for sent, received in result:
    clients.append({'ip': received.psrc, 'mac': received.hwsrc})

#writes IP list to readable file

for ips in clients:
    file.write(ips['ip'] + '\n')
    print(ips['ip'])

print('IP list saved to file')

#Attempt Telnet session to configure SSHv2 for Netmiko

for client in clients:
        try:
                tn = telnetlib.Telnet(client['ip'])
                print('Successfully connected to ' + (format(client['ip'])))

                tn.read_until(b"Username: ")
                tn.write(b"cisco\n")

                tn.read_until(b"Password: ")
                tn.write(b"cisco\n")
                tn.write(b"conf t\n")
                tn.write(b"ip domain-name cisco.local\n")
                tn.write(b"ip ssh rsa keypair-name ssh\n")
                time.sleep(3)
                tn.write(b"crypto key generate rsa usage-keys label ssh modulus 2048\n")
                time.sleep(7)
                tn.write(b"ip ssh version 2\n")
                tn.write(b"line vty 0 15\n")
                tn.write(b"transport input ssh\n")
                tn.write(b"exit\n")
                tn.write(b"exit\n")
                tn.write(b"exit\n")
                print(tn.read_all().decode('ascii'))
        except:
                print('connection failed to ' + (format(client['ip'])))
        else:
                print('Configuration on ' + (format(client['ip'])) + ' Successful')

#Attempting SSHv2 connection and configuration

ipfile = file.read().splitlines() #reads text file with list of IP addresses

with open ('ip.txt') as IP_list:
    for IP in IP_list:
        switch = {
                'device_type': 'cisco_ios',
                'ip': IP,
                'username': 'cisco',
                'password': 'cisco',
        }
 # Example configurations, can be edited to run any cisco commands
        try:                                                            
                net_connect = ConnectHandler(**switch)
                print('Connecting to the device ' + IP)
                config_commands = ['int range fa1/3 - 12', 'switch mode access', 'switchport access vlan 4','descr Access_Port', 'int range fa1/12 - 15', 'swit mode trunk']
                config_commands1 = ['vtp ver 2', 'vtp domain cisco', 'vtp mode transparent', 'ip default-gateway 192.168.122.1', 'ntp server 192.168.122.1']
                output = net_connect.send_config_set(config_commands)
                output1 = net_connect.send_config_set(config_commands1)
                print(output)
                print(output1)
        except:
                print('connection failed to ' + IP)
  # imbedded forloop? for creating vlans in a range, can also be edited to add whatever you would like 
        for n in range (2,6):
                try:
                    net_connect = ConnectHandler(**switch)
                    print ("CREATING VLAN " + str(n))
                    confing_command = ['vlan ' + str(n), 'name Python_Vlan' + str(n)]
                    output = net_connect.send_config_set(confing_command)
                    print (output)
                    print (IP + ' Sucessfully Configured')
                except:
                    print('connection failed to ' + IP)

execution_time  = (time.time() - start_time) 
print('Execution time in seconds: ' + str(execution_time)) # shows script run time
