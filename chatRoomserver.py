import socket
from threading import Thread

# local host and port
host = "127.0.0.1"
port = 6969

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    """
    Broadcasts messages.
    """
    for client in clients:
        client.send(message)

def handle(client):
    """
    Handles a client at a time.
    """
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except Exception as e:
            index = clients.index(client)
            clients.remove(index)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f"{nickname} has left the chat!".encode("ascii"))
            break

def receive():
    """
    Recieves messages.  
    """
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send("NICK".encode("ascii"))
        nickname =  client.recv(1024).decode("ascii")
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client  is {nickname}!")
        broadcast(f"{nickname} joined the chat!".encode("ascii"))
        client.send("Connected to the server!".encode("ascii"))

        # starting a thread for each user
        t = Thread(target=handle, args=(client,))
        t.start()

if __name__ == "__main__":
    print("Server is listening...")
    receive()