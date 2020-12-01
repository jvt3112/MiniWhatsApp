from socket import *
from _thread import *
import threading
import os

BUFFER_SIZE = 32
SEPARATOR = "<SEPARATOR>"

def chatClient(port):
    nickname = input("Enter a nickname: ")
    print("Print port", port)
    # port = int(input('Enter port: '))
    tcpClientSocket1 = socket(AF_INET, SOCK_STREAM)
    tcpClientSocket1.connect(('127.0.0.1', port))
    def recieve():
        while True:
            try:
                message = tcpClientSocket1.recv(1024).decode("ascii")
                if message == "NICK":
                    tcpClientSocket1.send(nickname.encode("ascii"))
                elif message[-4:] == 'QUIT':
                    print('QUITTED')
                    break
                else:
                    print(message)
            except Exception as e:
                print(e)
                print("Some error occured!")
                
    def send():
        while True:
            message = f"{nickname}: {input()}"
            tcpClientSocket1.send(message.encode("ascii"))
            if(message[-4:] == 'QUIT'):
                something = 'QUIT'
                break
                
    # recieving thread
    r_thread = threading.Thread(target=recieve)
    r_thread.start()

    # sending thread
    s_thread = threading.Thread(target=send)
    s_thread.start()
    s_thread.join()
    r_thread.join()
    print('Leaving Chat room')

def chatsaver(username,msg):
    # fname = r'C:\Users\AISHNA\OneDrive\Desktop\MiniWhatsApp'
    PATH = r'.\receiveFile'
    filename = os.path.join(PATH,username)
    #print(filename)
    fp = open(filename,"a+")
    fp.write(msg)
    fp.write("\n")
    fp.close() 

def clientSenderHandler(connectionSocket):
    filename = input("enter file name: ")
    print('\n')
    connectionSocket.send(filename.encode())
    while 1:
        filename = './' + filename
        filesize = os.path.getsize(filename)
        with open(filename, "rb") as f:
            for _ in range(0, filesize):
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                connectionSocket.sendall(bytes_read)
                if not bytes_read:
                    # file transmitting is done
                    connectionSocket.send('EOF'.encode())
                    print('File Sent')
                    break
        break