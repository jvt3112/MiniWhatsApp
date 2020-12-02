from socket import *
from _thread import *
import threading
import select
import os
import stdiomask
from utility import *
from chatRoomserver import *
from peerServer import *
from peerClient import *

BUFFER_SIZE = 32
SEPARATOR = "<SEPARATOR>"

class peerMain:
    def __init__(self):
        # initialisation
        self.registryName = '192.168.43.239' #input("Enter registry's IP address: ")
        self.registryPort = 15600
        # registry connection : tcp socket
        self.client_tcpsocket = socket(AF_INET, SOCK_STREAM)
        self.client_tcpsocket.connect((self.registryName,self.registryPort))
        #udp socket is used for sending msg
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        self.registryUDPPort = 15500
        self.loginCredentials = (None, None)
        self.isOnline = False
        self.peerServerPort = None
        self.chatRoomServerPort = 0
        self.chatRoomServer = None
        self.peerServer = None
        self.peerClient = None
        self.timer = None
        self.Status = 'Hi there!! We are using MiniWhatsApp'
        
        choice = "0"
        #option menu is sent
        while choice != "3":
            choice = input("Choose: \nCreate account: 1\nLogin: 2\nLogout: 3\nSearch: 4\nStart a chat: 5\nChange Status: 6\nSee Status: 7\nCreate ChatRoom: 8\n")
            if choice == "1": #create account
                username = input("username: ")
                password = stdiomask.getpass()  #entered by the user
                self.createAccount(username, password)
            elif choice == "2" and not self.isOnline: #login
                username = input("username: ")
                password = stdiomask.getpass() 
                peerServerPort = int(input("Enter a port number for peer server: "))
                status = self.login(username, password, peerServerPort)
                if status == 1: #successful login
                    self.isOnline = True
                    self.loginCredentials = (username, password)
                    self.peerServerPort = peerServerPort
                    self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort)
                    self.peerServer.start()
                    self.sendAckMessage()
            elif choice == "3" and self.isOnline: # logout
                self.logout(1)
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.peerServer.isOnline = False
                self.peerServer.server_tcpsocket.close()
                if self.peerClient != None:
                    self.peerClient.client_tcpsocket.close()
                print("Logged out successfully")
            elif choice == "3": #if not online then exit the program
                self.logout(2)
            elif choice == "4" and self.isOnline: # search any user
                username = input("Username to be searched: ")
                searchStatus = self.searchUser(username)
                if searchStatus != None and searchStatus != 0:
                    print("IP address of " + username + " is " + searchStatus)
            elif choice == "5" and self.isOnline: # start individual chatting
                username = input("Enter the username of user to start chat: ")
                searchStatus = self.searchUser(username)
                if searchStatus != None and searchStatus != 0:
                    searchStatus = searchStatus.split(":")
                    self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]) , self.loginCredentials[0], self.peerServer,None, None, 0)
                    self.peerClient.start()
                    self.peerClient.join()
            elif choice == "6" and self.isOnline: #change status
                print("Current Status: ", self.getStatus(self.loginCredentials[0]))
                answer = input("Want to change status? press 'Y': \n")
                if(answer=='Y'):
                    statusEnter = input('Enter your new status: ')
                    self.changeStatus(self.loginCredentials[0],statusEnter)
                else:
                    print('Status not changed')
            elif choice == "7" and self.isOnline: # check status 
                username = input("Enter username to see their status: ")
                searchStatus = self.searchUser(username)
                if searchStatus != None and searchStatus != 0:
                    print("Status of " + username + " is " + self.getStatus(username))
            elif choice == "8" and self.isOnline: # start a group chat
                chatRoomServerPort = int(input("Enter a port number for chat room server: "))
                self.chatRoomServerPort = chatRoomServerPort
                self.chatRoomServer= chatRoomServer(self.loginCredentials[0], self.chatRoomServerPort)
                self.chatRoomServer.start()
                usernameList = list(input("Enter the username of user that you want in your chat room: ").split())
                for i in range(len(usernameList)):
                    searchStatus = self.searchUser(usernameList[i])
                    if searchStatus != None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]) , self.loginCredentials[0], self.peerServer, self.chatRoomServer, None, 1)
                        self.peerClient.start()
                chatClient(self.chatRoomServerPort)
                self.peerServer.isChatRequested = 0
                
            # if this is the reciever side, then it functions according to the responses recieved
            elif choice[:8] == "OK-GROUP" and self.isOnline: #OK-GROUP is for accepting group chatting
                chatClient(int(choice[9:]))
                self.peerServer.isChatRequested=0
            elif choice == "OK" and self.isOnline: # OK is for accepting individual chatting
                okMessage = "OK " + self.loginCredentials[0]
                self.peerServer.peersocket_connection.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.peerIP_connection, self.peerServer.peerport_connection , self.loginCredentials[0], self.peerServer,None, "OK", None)
                self.peerClient.start()
                self.peerClient.join()
            elif choice == "OK-SAVE" and self.isOnline: # OK-SAVE is for accepting individual chatting with saving chat functionality
                self.peerServer.isSaveChat = 1
                okMessage = "OK-SAVE " + self.loginCredentials[0]
                self.peerServer.peersocket_connection.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.peerIP_connection, self.peerServer.peerport_connection , self.loginCredentials[0], self.peerServer,None, "OK-SAVE", None)
                self.peerClient.start()
                self.peerClient.join()
            elif choice == "REJECT" and self.isOnline: # REJECT is for rejecting the request
                self.peerServer.peersocket_connection.send("REJECT".encode())
                self.peerServer.isChatRequested = 0
        # socket closed
        if choice != "CANCEL":
            self.client_tcpsocket.close()

    # this function is for account creation, informs user accordingly about the status of account creation
    def createAccount(self, username, password):
        message = "JOIN " + username + " " + password + " " + self.Status
        self.client_tcpsocket.send(message.encode())
        response = self.client_tcpsocket.recv(1024).decode()
        if response == "account-success":
            print("Account created...")
        elif response == "account-exist":
            print("Account with this name already exist choose another login...")

    # this function is to change the status of a user
    def changeStatus(self, username, status):
        message = "CHANGE " + username + " " + status
        self.client_tcpsocket.send(message.encode())
        response = self.client_tcpsocket.recv(1024).decode()
        if response == "status-changed":
            print("Status changed")

    # this function is to get the status of a user
    def getStatus(self, username):
        message = "GET " + username
        self.client_tcpsocket.send(message.encode())
        status = self.client_tcpsocket.recv(1024).decode()
        return status

    # login function , login msg is sent to registry, and response recieved is in form of integer
    def login(self, username, password, peerServerPort):
        # 1 : login successful
        # 2 : account does not exist
        # 3 : already online
        # 4 : wrong password
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        self.client_tcpsocket.send(message.encode())
        response = self.client_tcpsocket.recv(1024).decode()
        if response == "Account-success":
            print("Logged in successfully")
            return 1
        elif response == "Account-not-exist":
            print("Account does not exist")
            return 0
        elif response == "Account-online":
            print("Account is already online")
            return 2
        elif response == "Wrong-password":
            print("Wrong password")
            return 3
    
    # logout function, also sends logout msg to the registry
    def logout(self, option):
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        self.client_tcpsocket.send(message.encode())
        
    # function for searching an online user
    def searchUser(self, username):
        #msg is sent to registry and custom value is recieved according to different responses
        message = "SEARCH " + username
        self.client_tcpsocket.send(message.encode())
        response = self.client_tcpsocket.recv(1024).decode().split()
        if response[0] == "Success":
            print(username + " is found successfully...")
            return response[1]
        elif response[0] == "User-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "User-not-found":
            print(username + " is not found")
            return None

    #send ACK msgs to udp socket of registry using a timer thread
    def sendAckMessage(self):
        message = "ACK " + self.loginCredentials[0]
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendAckMessage)
        self.timer.start()

#main process starts
main = peerMain()