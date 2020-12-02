from socket import *
from _thread import *
import threading
from utility import *

BUFFER_SIZE = 32
SEPARATOR = "<SEPARATOR>"

class PeerClient(threading.Thread):
    #initialising all the parameters for peer's client side
    def __init__(self, ip_connection, port_connection, username, peer_server,  chatRoomServer, response, requestforGroup):
        threading.Thread.__init__(self)
        # tcp socket initialization at client side
        self.client_tcpsocket = socket(AF_INET, SOCK_STREAM)
        self.ip_connection = ip_connection
        self.username = username
        self.requestforGroup = requestforGroup
        self.port_connection = port_connection
        self.peer_server = peer_server
        self.chatRoomServer = chatRoomServer
        self.response = response
        #variable for client's wish of saving chat or not
        self.isSaveChat = 0
        #variable for client's wish of ending chat or not
        self.isEndingChat = False

    #main method for running the client thread of peer
    def run(self):
        print("Starting peer client...")
        # other peers server gets connected
        self.client_tcpsocket.connect((self.ip_connection, self.port_connection))
        #if this peer's server is not busy anywhere, i.e, not connected to other server, and if this peer client is requesting for chat
        if self.peer_server.isChatRequested == 0 and self.response is None:
            #a message is sent accordingly if request is for group chat or individual chat
            if(self.requestforGroup):
                requestMessage = "CHAT-REQUEST-FOR-GROUP " + str(self.chatRoomServer.chatRoomServerPort)+ " " + self.username
            else:
                requestMessage = "CHAT-REQUEST " + str(self.peer_server.port_peerserver)+ " " + self.username
            # chat request send
            self.client_tcpsocket.send(requestMessage.encode())
            print("Request message " + requestMessage + " is sent...")
            #response is recieved from the peer
            self.response = self.client_tcpsocket.recv(1024).decode()
            
            self.response = self.response.split()
            if(not self.response):
                self.client_tcpsocket.close()
            #the msgs recieved will be treated as client msg
            #"OK-GROUP" for group chatiing without saving chat
            elif self.response[0][:8] == "OK-GROUP":
                pass
            #"OK" for individual chatiing without saving chat
            elif self.response[0] == "OK":
                # chatting status is updated
                self.peer_server.isChatRequested = 1
                self.peer_server.chattingClientName = self.response[1]
                # client can send msg as long as the server status is chatting
                while self.peer_server.isChatRequested == 1:
                    msgsent = input(self.username + ": ")
                    self.client_tcpsocket.send(msgsent.encode())
                    #this msg is for file transfer
                    if msgsent == ":f":
                        clientSenderHandler(self.client_tcpsocket)
                    #this msg is for quiting the chat, hence status of chatting is updated
                    if msgsent == ":q":
                        self.peer_server.isChatRequested = 0
                        self.isEndingChat = True
                        break
            # "OK-SAVE" for saving the chat (individual chatting)
            elif self.response[0] == "OK-SAVE":
                # chatting status is updated
                self.peer_server.isChatRequested = 1
                self.peer_server.chattingClientName = self.response[1]
                # client can send msg as long as the server status is chatting
                while self.peer_server.isChatRequested == 1:
                    msgsent = input(self.username + ": ")
                    self.client_tcpsocket.send(msgsent.encode())
                    #this msg is for file transfer
                    if msgsent == ":f":
                        clientSenderHandler(self.client_tcpsocket)
                    #this msg is for quiting the chat, hence status of chatting is updated
                    if msgsent == ":q":
                        self.peer_server.isChatRequested = 0
                        self.isEndingChat = True
                        break
                #check if it is ending chat 
                if self.peer_server.isChatRequested == 0:
                    if not self.isEndingChat:
                        # a quit msg is sent to connected peer, if any error is encountered it is handled by log
                        try:
                            self.client_tcpsocket.send(":q ending-side".encode())
                        except BrokenPipeError as bpErr:
                            pass
                    self.response = None
                    # closes the socket
                    self.client_tcpsocket.close()
            #if the other peer rejects the request of chatting, then a reject msg is sent and logged into the log file    
            elif self.response[0] == "REJECT":
                self.peer_server.isChatRequested = 0
                #print("client of requester is closing...")
                self.client_tcpsocket.send("REJECT".encode())
                self.client_tcpsocket.close()
            # socket is closed if response received is busy
            elif self.response[0] == "BUSY":
                print("Receiver peer is busy")
                self.client_tcpsocket.close()
        #if response is OK , it gets connected to the peer and waits for the response
        elif self.response == "OK":
            self.peer_server.isChatRequested = 1
            #OK is sent to requester peer
            okmsg = "OK"
            self.client_tcpsocket.send(okmsg.encode())
            print("Sending messages, client is created")
            # client can send messsages as long as the server status is chatting
            while self.peer_server.isChatRequested == 1:
                msgsent = input(self.username + ": ")
                self.client_tcpsocket.send(msgsent.encode())
                #this msg is for file transfer
                if msgsent == ":f":
                    clientSenderHandler(self.client_tcpsocket)
                #this msg is for quiting the chat, hence status of chatting is updated
                if msgsent == ":q":
                    self.peer_server.isChatRequested = 0
                    self.isEndingChat = True
                    break
            #check if it is ending chat 
            if self.peer_server.isChatRequested == 0:
                if not self.isEndingChat:
                    self.client_tcpsocket.send(":q ending-side".encode())
                self.response = None
                self.client_tcpsocket.close()
        elif self.response == "OK-SAVE":
            self.isSaveChat = 1
            self.peer_server.isChatRequested = 1
            # ok response is sent to the requester side
            okmsg = "OK-SAVE"
            self.client_tcpsocket.send(okmsg.encode())
            print("Client with OK-SAVE message is created... and sending messages")
            # client can send messsages as long as the server status is chatting
            while self.peer_server.isChatRequested == 1:
                msgsent = input(self.username + ": ")
                if(self.isSaveChat):
                    chatsaver(self.username, self.username + ": " + msgsent)
                self.client_tcpsocket.send(msgsent.encode())
                #this msg is for file transfer
                if msgsent == ":f":
                    clientSenderHandler(self.client_tcpsocket)
                #this msg is for quiting the chat, hence status of chatting is updated   
                if msgsent == ":q":
                    self.peer_server.isChatRequested = 0
                    self.isEndingChat = True
                    break
            #check if it is ending chat 
            if self.peer_server.isChatRequested == 0:
                if not self.isEndingChat:
                    self.client_tcpsocket.send(":q ending-side".encode())
                self.response = None
                #closing the socket
                self.client_tcpsocket.close()
