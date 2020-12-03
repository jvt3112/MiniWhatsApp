# importing libraries
from os import stat
from socket import *
import threading
import select
import db
import netifaces as ni

# Class main aim is to send the client messages to registry - Main server
# For each new client that will be connected to registry new client thread is created
class NewClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip address of connected peer
        self.IPAddr = ip
        # connected peer's portnumber
        self.portAddr = port
        # peer socket
        self.tcpClientSocket = tcpClientSocket
        # username, online status and udp server initializations
        self.username = None
        self.isOnline = True
        self.udpServer = None
        print("New thread started for " + ip + ":" + str(port))

    # thread main
    def run(self):
        # locking the thread 
        self.lock = threading.Lock()
        print("Connection from: " + self.IPAddr + ":" + str(self.portAddr))
        print("IP Connected: " + self.IPAddr)
        
        while True:
            try:
                # message incoming from the peer
                message = self.tcpClientSocket.recv(1024).decode().split()
                # if JOIN recieved  #
                if message[0] == "JOIN":
                    # if account exists 
                    # then account-exists is send as reponse
                    if db.is_account_exist(message[1]):
                        response = "account-exist"
                        self.tcpClientSocket.send(response.encode())
                    
                    # if account doesn't exists
                    # account created and account success message is sent
                    else:
                        db.register(message[1], message[2], " ".join(message[3:])) #messagep[3] status
                        response = "account-success"
                        self.tcpClientSocket.send(response.encode())
                # if CHANGE recieved  #
                elif message[0] == "CHANGE":
                    # if account exist 
                    # status changed mssg is sent 
                    if db.is_account_exist(message[1]):
                        db.update_status(message[1]," ".join(message[2:]))
                        response = "status-changed"
                        self.tcpClientSocket.send(response.encode())
                # if GET recieved  #
                elif message[0] == "GET":
                    # if account exists
                    # current status is sent as mssg
                    if db.is_account_exist(message[1]):
                        status = db.get_status(message[1])
                        self.tcpClientSocket.send(status.encode())
                # if LOGIN recieved  #
                elif message[0] == "LOGIN":
                    # if no account exist with the given username 
                    # flag is sent to the peer
                    if not db.is_account_exist(message[1]):
                        response = "Account-not-exist"
                        self.tcpClientSocket.send(response.encode())
                    # if an account is already online with given username
                    # flag is sent
                    elif db.is_account_online(message[1]):
                        response = "Account-online"
                        self.tcpClientSocket.send(response.encode())
                    # if an account is log in successfully 
                    # extracts the password from the string
                    else:
                        # checks the password from looking into database
                        retrievedPass = db.get_password(message[1])
                        if retrievedPass == message[2]:
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                tcpThreads[self.username] = self
                            finally:
                                self.lock.release()

                            db.user_login(message[1], self.IPAddr, message[3])
                            # login-success is sent to the peer and udp thread is started to 
                            # watch the time
                            response = "Account-success"
                            self.tcpClientSocket.send(response.encode())
                            # udp server created
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            # udp server started 
                            self.udpServer.start()
                            # start the timer of udp
                            self.udpServer.timer.start()
                        # if wrong password then flag is sent
                        else:
                            response = "Wrong-password" 
                            self.tcpClientSocket.send(response.encode())
                #   if LOGOUT recieved  #
                elif message[0] == "LOGOUT":
                    # if user logouts removes usre from the online list of peer
                    # thread removed from the list and socket is closed
                    # timer udp thread cancels 
                    if len(message) > 1 and message[1] is not None and db.is_account_online(message[1]):
                        db.user_logout(message[1])
                        # lock acquired 
                        self.lock.acquire()
                        try:
                            if message[1] in tcpThreads:
                                # removes thread form the list
                                del tcpThreads[message[1]]
                        finally:
                            # lock released
                            self.lock.release()
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break
                #   if SEARCH recieved  #
                elif message[0] == "SEARCH":
                    # checks for accounts existsence
                    if db.is_account_exist(message[1]):
                        # if account is online search success is send
                        if db.is_account_online(message[1]):
                            peer_info = db.get_peer_ip_port(message[1])
                            response = "Success " + peer_info[0] + ":" + peer_info[1]
                            self.tcpClientSocket.send(response.encode())
                        # else user not online is send
                        else:
                            response = "User-not-online"
                            self.tcpClientSocket.send(response.encode())
                    # if no user with given name is found serach user not found is sent
                    else:
                        response = "User-not-found"
                        self.tcpClientSocket.send(response.encode())
            except OSError as oErr:
                pass 


    # resets the UDP timer 
    def resetTimeout(self):
        self.udpServer.resetTimer()

                            
# udp thread for each client
class UDPServer(threading.Thread):


    # initilaizing udp server thread
    def __init__(self, username, clientSocket):
        threading.Thread.__init__(self)
        self.username = username
        # time thread initialization
        self.timer = threading.Timer(3, self.waitForAckMsg)
        self.tcpClientSocket = clientSocket
    

    #ACK mssg not recieved
    #client timeouts
    def waitForAckMsg(self):
        if self.username is not None:
            db.user_logout(self.username)
            if self.username in tcpThreads:
                del tcpThreads[self.username]
        self.tcpClientSocket.close()
        print("Removed " + self.username + " from online peers")


    # udp server timer restes
    def resetTimer(self):
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitForAckMsg)
        self.timer.start()


# initializing tcp and udp port 
print("Registy started...")
TCPport= 15600
UDPport = 15500

# db initialization
db = db.DB()

# gets the ip address of the given server
# first tries gettinf from the windows device if not 
# then gets form the macos device

hostname=gethostname()
try:
    # windows device
    host=gethostbyname(hostname)
except gaierror:
    # gets ip from macos device
    host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']


print("Registry IP address: " + host)
print("Registry port number: " + str(TCPport))

# tcpThreads list for online client's thread
tcpThreads = {}

#initializing tcp and udp socket 
tcpSocket = socket(AF_INET, SOCK_STREAM)
udpSocket = socket(AF_INET, SOCK_DGRAM)

# binding the socket with host and respective TCP and UDP port
tcpSocket.bind((host,TCPport))
udpSocket.bind((host,UDPport))

# listening... 
tcpSocket.listen(5)

# input sockets that are listened
socketInputs = [tcpSocket, udpSocket]

#initializing log file that contains all the details

# registry runs as long as any socket is present in socketInputs
while socketInputs:

    # watches for all the incoming request
    readable, writable, exceptional = select.select(socketInputs, [], [])
    for s in readable:
        # if new connection recieves to the tcp socket
        # connection is accepted and a new thread is started for the same
        if s is tcpSocket:
            # connection accepted
            tcpClientSocket, addr = tcpSocket.accept()
            # newThread is created
            newThread = NewClientThread(addr[0], addr[1], tcpClientSocket)
            # newThread is started
            newThread.start()
        # if new connection recieves to the udp socket
        elif s is udpSocket:
            # the incoming udp message is split
            message, clientAddress = s.recvfrom(1024)
            message = message.decode().split()
            # if the message is ACK
            if message[0] == "ACK":
                # checks if the account that sent the ACK message is online or not
                if message[1] in tcpThreads:
                    # reset the timer of the client whose ACK message was recieved
                    tcpThreads[message[1]].resetTimeout()
                    
# tcp socket is closed for registry
tcpSocket.close()