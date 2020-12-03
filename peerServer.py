from socket import *
from _thread import *
import threading
import select
#import logging
import os
from utility import *

class PeerServer(threading.Thread):
    #initialising all the parameters for peer's server side
    def __init__(self, username, port_peerserver):
        threading.Thread.__init__(self)
        # tcp socket initialization at server side
        self.server_tcpsocket = socket(AF_INET, SOCK_STREAM)
        self.username = username
        self.port_peerserver = port_peerserver
        self.peersocket_connection = None
        self.peerIP_connection = None
        self.peerport_connection = None
        #peer's status whether it is online or offline
        self.isOnline = True
        # chatting peer's username
        self.chattingClientName = None
        # keeping current file pointer if doing file transfer
        self.fileptr = None
        #the variables are 1 if activated, else they are 0
        self.isChatRequested = 0
        self.isFileIncoming = 0
        self.isNameReceived = 0
        self.isSaveChat = 0
        
    #main method for running the server thread of peer
    def run(self):
        print("Starting peer server...")    
        # checks and get the ip address 
        hostname=gethostname()
        self.peerServerHostname=gethostbyname(hostname)
        # ip address of this peer
        # self.peerServerHostname = 'localhost'
        # peer server socket initialisation
        self.server_tcpsocket.bind((self.peerServerHostname, self.port_peerserver))
        self.server_tcpsocket.listen(4)
        #sockets inputs to be listened
        inputs = [self.server_tcpsocket]
        # as long there are socket inputs to be listened and online user, server listens to them
        while inputs and self.isOnline:
            try:
                readable, writable, exceptional = select.select(inputs, [], [])
                for s in readable:
                    #tcp socket connections of peer server
                    if s is self.server_tcpsocket:
                        # connection accepted , appended to sockets inputs list
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        #ip and socket of this peer is allocated to server if it found idle, not chatting
                        if self.isChatRequested == 0:     
                            print(self.username + " is connected from " + str(addr))
                            self.peersocket_connection = connected
                            self.peerIP_connection = addr[0]
                    #socket used for communicating with connected peer recives data 
                    else:
                        #connected peer's msg recieved 
                        msgRecieved = s.recv(1024).decode()
                        # print(msgRecieved)
                        #recieved msg is logged into log file
                        #if chat request is the recieved msg
                        #this is reciever peer side
                        if len(msgRecieved) > 11 and msgRecieved[:12] == "CHAT-REQUEST":
                            # connected peer socket
                            if s is self.peersocket_connection:
                                msgRecieved = msgRecieved.split()
                                #getting port and username of the peer who sends the chat request msg
                                self.peerport_connection = int(msgRecieved[1])
                                self.chattingClientName = msgRecieved[2]
                                print("Chat request from " + self.chattingClientName + " >> ")
                                print("Enter OK to accept, REJECT to reject, OK-GROUP-" + str(self.peerport_connection) +" for Group chat or OK-SAVE to save chat:  ")
                                self.isChatRequested = 1
                            #if user is busy (chatting with someone else), busy msg is send and socket is removed from the list
                            elif s is not self.peersocket_connection and self.isChatRequested == 1:
                                msg = "BUSY"
                                s.send(msg.encode())
                                inputs.remove(s)
            
                        # OK msg for individual chat
                        elif msgRecieved == "OK" and self.isChatRequested == 0:
                            self.isChatRequested = 1
                        # OK msg for individual chat along with saving chat
                        elif msgRecieved == "OK-SAVE" and self.isChatRequested == 0:
                            self.isChatRequested = 1
                        # rejected chat request, server made available for other requests
                        elif msgRecieved == "REJECT" and self.isChatRequested == 0:
                            self.isChatRequested = 0
                            inputs.remove(s)
                        # msg is for file transfer
                        elif msgRecieved == ":f":
                            self.isFileIncoming = 1
                        # msg is recieved and has to be saved 
                        elif msgRecieved[:2] != ":q" and len(msgRecieved)!= 0 and self.isSaveChat:
                            chatsaver(self.username,self.chattingClientName + ": " + msgRecieved)
                            print(self.chattingClientName + ": " + msgRecieved)
                        #msg is revieved and it is a file 
                        elif msgRecieved[:2] != ":q" and len(msgRecieved)!= 0 and self.isFileIncoming:
                            if self.isNameReceived == 0:
                                PATH = r'.\receiveFile'
                                filename = os.path.join(PATH,msgRecieved)
                                self.fileptr = open(filename,"w")
                                self.isNameReceived = 1
                            else:
                                self.fileptr.write(msgRecieved)
                                if('EOF' in msgRecieved):
                                    self.fileptr.close()
                                    print("File Received")
                                    self.isFileIncoming = 0
                        elif msgRecieved[:2] != ":q" and len(msgRecieved)!= 0:
                            if(self.isSaveChat):
                                chatsaver(self.username,self.chattingClientName + ": " + msgRecieved)
                            print(self.chattingClientName + ": " + msgRecieved)
                        
                        #msg is for quiting the chat
                        elif msgRecieved[:2] == ":q":
                            # made open for new requests
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.server_tcpsocket)
                            #the peer ended the chat
                            if len(msgRecieved) == 2:
                                print("Peer ended the chat")
                                print("Press enter to quit the chat: ")
                        #chat is ended suddenly because either user ended it or error occured
                        elif len(msgRecieved) == 0:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.server_tcpsocket)
                            print("Peer ended the chat")
                            print("Press enter to quit the chat: ")
            # handle the execptions
            except OSError as oErr:
                pass
            except ValueError as vErr:
                pass