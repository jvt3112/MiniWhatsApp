# This python file contains all the utility function 
# used in peermain

# importing required libraries
from socket import *
from _thread import *
import threading
import os

BUFFER_SIZE = 32

# function for running client thread when group-chat has been requested
def chatClient(port):
    # nickname to be used in group chat
    nickname = input("Enter a nickname to be used in group chat: ")
    # creating a new socket
    tcpClientSocket1 = socket(AF_INET, SOCK_STREAM)
    #socket connected
    tcpClientSocket1.connect(('127.0.0.1', port))
    # function to constantly receive the messages
    def recieve():
        while True:
            try:
                # try if message received decode
                message = tcpClientSocket1.recv(1024).decode("ascii")
                # if message recieved is flag NICK sends nickname to chat room server
                if message == "NICK":
                    tcpClientSocket1.send(nickname.encode("ascii"))
                # if message received is flag QUIT, clients quits the chat room and is removed from the server
                # and recieve thread of client closes
                elif message[-4:] == 'QUIT':
                    print('QUITTED')
                    break
                else:
                    # prints message of other user in chat
                    print(message)
            except Exception as e:
                print(e)
                print("Some error occured!")

    # function to send the message constantly in a  group
    def send():
        while True:
            message = f"{nickname}: {input()}"
            # encode the message and send to the server it is connected
            tcpClientSocket1.send(message.encode("ascii"))
            # if send message is QUIT, clients quits the chat room and is removed from the server
            # and sending thread of client closes
            if(message[-4:] == 'QUIT'):
                something = 'QUIT'
                break
                
    # recieving thread
    r_thread = threading.Thread(target=recieve)
    r_thread.start()

    # sending thread
    s_thread = threading.Thread(target=send)
    s_thread.start()

    # wait for both sending and recievig thread to complete
    s_thread.join()
    r_thread.join()

    # client leaves the chat room
    print('Leaving Chat room')


# function that creates a save file if user wants to save the message as well
def chatsaver(username,msg):
    # path to save the file
    PATH = r'.\receiveFile'
    filename = os.path.join(PATH,username)
    # opening a file in append mode
    fp = open(filename,"a+")
    # writes message in the file
    fp.write(msg)
    fp.write("\n")
    # closes the file
    fp.close() 

# function responsible to send the file to the client
def clientSenderHandler(connectionSocket):
    # file name to be sent
    filename = input("enter file name: ")
    print('\n')
    # sends name of the file
    connectionSocket.send(filename.encode())
    while 1:
        # gets filename to be opened
        filename = './' + filename
        filesize = os.path.getsize(filename)
        # starts sending the file
        with open(filename, "rb") as f:
            for _ in range(0, filesize):
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                connectionSocket.sendall(bytes_read)
                if not bytes_read:
                    # file transmitting is done
                    # sending EOF to know end of the file
                    connectionSocket.send('EOF'.encode())
                    print('File Sent')
                    break
        break