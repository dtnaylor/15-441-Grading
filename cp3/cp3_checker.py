#!/usr/bin/python

import socket
import sys
import random
import os

if len(sys.argv) < 7:
    sys.stderr.write('Usage: %s <ip> <port> <#trials> <#writes and reads per trial> <max # bytes to write at a time> <#connections> \n' % (sys.argv[0]))
    sys.exit(1)

serverHost = sys.argv[1]
serverPort = int(sys.argv[2])
numTrials = int(sys.argv[3])
numWritesReads = int(sys.argv[4])
numBytes = int(sys.argv[5])
numConnections = int(sys.argv[6])

socketList = []

socket.setdefaulttimeout(5)

for i in xrange(numConnections):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    s.connect((serverHost, serverPort))
    socketList.append(s)


for i in xrange(numTrials):
    socketSubset = []
    randomData = []
    randomLen = []
    socketSubset = random.sample(socketList, numWritesReads if numWritesReads < len(socketList) else len(socketList))
    readwriteorder = range(len(socketSubset))
    for j in readwriteorder:
            random_string = 'GET /index.html HTTP/1.1\r\n\r\n' 
            random_len = len(random_string)
            randomLen.append(random_len)
            randomData.append(random_string)    
            # could hang with a bad server...
            socketSubset[j].send(random_string)

    if random.randint(0,100) > 95:
        socketSubset[j].close()
        del randomLen[j]
        del randomData[j]
        del socketList[socketList.index(socketSubset[j])]
        del socketSubset[j]

    readwriteorder = range(len(socketSubset))
    random.shuffle(readwriteorder)
    for j in readwriteorder:
        data = ''
        # could hang with a bad server...
        while (len(data) < randomLen[j]):
            got = socketSubset[j].recv(randomLen[j] - len(data))
            if got != None: data += got
            elif len(got) == 0: sys.exit(1)
            else: break
        #if(data != randomData[j]):
        #    sys.stderr.write("Error: Data received is not the same as sent! \n")
        #    sys.exit(1)

    if random.randint(0,100) > 95:
        socketSubset[j].close()
        del socketList[socketList.index(socketSubset[j])]
        del socketSubset[j]


                

for sock in socketList:
    sock.close()

sys.exit(0)
