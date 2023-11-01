# For this script to work, one device has to be turned on 10 seconds before
# the other device. The process goes like this:
#
# 1) when device is turned on it tries to connect to the "PICO" wifi access
# point which is provided by the other pico.
#
# 2) after 10 seconds of no connection, the device will createa wifi network
#called PICO.
#
# 3) When the second device is turned on, it will connect to the first.
# The code on each device is identical.
#
# In the case that the connection is not working:
# 1) Turn off both devices.
# 2) Turn on one device, wait until it creates AP and displays IP address.
# 3) Turn on second device, it usually takes 5-6 seconds to connect to PICO
# AP. So in less than 20 seconds, both devices can be setup and running.

import network
import socket
import time
import _thread

tlock = _thread.allocate_lock()

class WifiHandler():
    def __init__(self):
        self.name = 'pico1'
        self.ip1 = ''
        self.ip2 = ''
        self.p1 = 0
        self.p2 = 0
        self.conntype = 'STA'

    def wifi_connect(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect('PICO', '123456789')
        tries = 1
        while wlan.isconnected() == False:
            if tries < 11:
                print('Waiting for connection... tries:', tries)
                time.sleep(1)
                tries += 1
            else:
                wlan.active(False)
                self.wifi_create()
                break
                
        if wlan.isconnected() == True:
            self.conntype = 'STA'
            self.name = 'pico2'
            self.ip1 = str(wlan.ifconfig()[0])
            self.ip2 = '192.168.4.1'
            self.p1 = 30001
            self.p2 = 20001
            print(f'connected to wifi, ip address: {self.ip1}')
        else:
            pass

    def wifi_create(self):
        ap = network.WLAN(network.AP_IF)
        ap.config(essid='PICO', password='123456789')
        ap.active(True)
        if ap.active() == True:
            self.conntype = 'AP'
            self.name = 'pico1'
            self.ip1 = str(ap.ifconfig()[0])
            self.ip2 = '192.168.4.16'
            self.p1 = 20001
            self.p2 = 30001
            print(f'wifi AP created, ip address: {self.ip1}')
            
wh = WifiHandler()


if wh.conntype == 'STA':
    wh.wifi_connect()
else:
    wh.wifi_create()
    
class SockHandler():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip1 = wh.ip1
        self.ip2 = wh.ip2
        self.p1 = wh.p1
        self.p2 = wh.p2

    def srx(self):
        while True:
            self.sock.bind((self.ip1, self.p1))
            data, addr = self.sock.recvfrom(512)
            tlock.acquire()
            print(data.decode())
            tlock.release()

    def stx(self):
        while True:
            MESSAGE = input()
            if MESSAGE == '' or MESSAGE == '\n':
                pass
            if MESSAGE == "m_reset":
                machine.reset()
            else:
                tlock.acquire()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(f'{wh.name}: {MESSAGE}', (wh.ip2, wh.p2))
                sock.close()
                tlock.release()


sh = SockHandler()

print(f'ip1: {sh.ip1}:{sh.p1}, ip2: {sh.ip2}:{sh.p2}')

second_thread = _thread.start_new_thread(sh.srx, ())
sh.stx()

