from socket import *
from _thread import *
import threading
import select
import logging
import os

class chatRoomServer(threading.Thread):
    # chatRoomServer server initialization
    def __init__(self, username, chatRoomServerPort):
        threading.Thread.__init__(self)
        # usernam of the peer
        self.username = username
        # tcp socket for chat room server
        self.tcpServerChatRoomSocket = socket(AF_INET, SOCK_STREAM)
        # port number of chat room server
        self.chatRoomServerPort = chatRoomServerPort
        
    # main function for chat room server that accepts the connections
    def run(self):

        # chat room server started
        print("Chat room server started...")    
        # binding the socket
        self.tcpServerChatRoomSocket.bind(("127.0.0.1", self.chatRoomServerPort))
        # listening to the socket
        self.tcpServerChatRoomSocket.listen(30)
        
        # lists of clients and their corresponding nicknames to be used in group chat
        clients = []
        nicknames = []

        # broadcasting messages to all the person in the group chat room
        def broadcast(inputs,message):
            for client in inputs:
                # sending messages to all the peers in the room
                client.send(message)

        # handle the data received from all the cleints
        def handle(nicknames,client):
            while True:
                try:
                    # message received
                    message = client.recv(1024)
                    # if the message recived is QUIT
                    if(message[-4:].decode("ascii")=='QUIT'):
                        index = clients.index(client)
                        # broadcast the QUIT message only to the client
                        # who quitted
                        broadcast([client],message)
                        # remove client formt the list
                        clients.remove(client)
                        # closing client socket once he leaves the group chat
                        client.close()
                        # removing the nickname from the list
                        nickname = nicknames[index]
                        nicknames.remove(nickname)
                        # brodcast mssg to clients 
                        broadcast(clients,f"{nickname} has left the chat!".encode("ascii"))
                        break
                    else:
                        broadcast(clients,message)
                # remove the client if any exception occurs
                except Exception as e:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    broadcast(clients,f"{nickname} has left the chat!".encode("ascii"))
                    break
    
        while True:
            # accepts the connection
            connected, addr = self.tcpServerChatRoomSocket.accept()
            # flag NICK send to get the nickname
            connected.send("NICK".encode("ascii"))
            # nickname recieved
            nickname =  connected.recv(1024).decode("ascii")
            # append nickname to the list
            nicknames.append(nickname)
            # append client to the list
            clients.append(connected)
            print(f"Username of the client  is {nickname}!")
            # broadcast mssg about users arrival
            broadcast(clients,f"{nickname} joined the chat!".encode("ascii"))
            connected.send("Connected to the server!".encode("ascii"))

            # starting a thread for each user
            threadUser = threading.Thread(target=handle, args=(nicknames,connected,))
            threadUser.start()
        self.tcpServerChatRoomSocket.close()
        print("Returning from room")