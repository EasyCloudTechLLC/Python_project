#!/usr/bin/env python3


from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii  
		
ICMP_ECHO_REQUEST = 8
MAX_HOPS = 15
TIMEOUT  = 3.0 
TRIES    = 2

def checksum(string):
    # Fill in
    string = bytearray(string)
    csum = 0
    countN = (len(string) // 2) * 2

    for count in range(0, countN, 2):
        value = string[count+1] * 256 + string[count]
        csum = csum + value
        csum = csum & 0xffffffff

    if countN < len(string):
        csum = csum + string[-1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    result = ~csum
    result = result & 0xffff
    result = result >> 8 | (result << 8 & 0xff00)
    return result

def build_packet():
    # Fill in
    myChecksum = 0
    myId = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myId, 1)
    data = struct.pack("d", time.time())
    myChecksum = checksum(header + data)    
    if sys.platform == 'darwin':
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myId, 1)
    packet = header + data
    return packet

def get_route(hostname):
	timeLeft = TIMEOUT
	for ttl in range(1,MAX_HOPS):
		for tries in range(TRIES):

			destAddr = socket.gethostbyname(hostname)
			#Fill in, make a raw socket named mySocket
			icmp=socket.getprotobyname("icmp")
			mySocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM, icmp)
			mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
			mySocket.settimeout(TIMEOUT)
			try:
				d = build_packet()
				mySocket.sendto(d, (hostname, 0))
				t= time.time()
				startedSelect = time.time()
				whatReady = select.select([mySocket], [], [], timeLeft)
				howLongInSelect = (time.time() - startedSelect)
				if whatReady[0] == []: # Timeout
					print("  *        *        *    Request timed out.")
				recvPacket, addr = mySocket.recvfrom(1024)
				timeReceived = time.time()
				timeLeft = timeLeft - howLongInSelect
				if timeLeft <= 0:
					print("  *        *        *    Request timed out.")
				
			except timeout:
				continue			
			
			else:
				icmpHeader=recvPacket[20:28]
				types,code, checksum, packetID, sequence=struct.unpack("bbHHh", icmpHeader)

				if types == 11:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived -t)*1000, addr[0]))
				
				elif types == 3:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived-t)*1000, addr[0]))
				
				elif types == 0:
					bytes = struct.calcsize("d") 
					timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
					print("  %d    rtt=%.0f ms    %s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
					return
			
				else:
					print("error")			
				break	
			finally:				
				mySocket.close()		
get_route("www.apple.com")	

