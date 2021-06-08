  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 16:00:23 2021

@author: pw
"""

#import socket module
from socket import *
serverSocket = socket(AF_INET, SOCK_STREAM) 
#Prepare a sever socket 
serverPort=80
serverSocket.bind(('', serverPort)) 
serverSocket.listen(1)
print("the web server is up on port:",serverPort)

while True:
	#Establish the connection
	print('Ready to serve...')
	connectionSocket, addr = serverSocket.accept() 
	try:
		message = connectionSocket.recv(1024) 
		filename = message.split()[1]
		f = open(filename[1:])
		outputdata = f.read();
		#Send one HTTP header line into socket
		header = ' HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html\nContent-Length: %d\n\n' % (len(outputdata))
		connectionSocket.send(header.encode())

		#Send the content of the requested file to the client
		for i in range(0, len(outputdata)):
			connectionSocket.send(outputdata[i].encode())
		connectionSocket.close()
	except IOError:
		#Send response message for file not found
		header = ' HTTP/1.1 404 Not Found'
		connectionSocket.send(header.encode())
		
		#Close client socket
		connectionSocket.close()
        serverSocket.close()#Terminate the program after sending the corresponding data