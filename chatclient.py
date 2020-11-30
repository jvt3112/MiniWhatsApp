import socket
from threading import Thread

nickname = input("Enter a nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 6969))

def recieve():
    """
    Recieving messages from server.
    """
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            if message == "NICK":
                client.send(nickname.encode("ascii"))
            else:
                print(message)
        except Exception as e:
            print(e)
            print("Some error occured!")
            client.close()
            break


def send():
    while True:
        message = f"{nickname}: {input()}"
        client.send(message.encode("ascii"))

# recieving thread
r_thread = Thread(target=recieve)
r_thread.start()

# sending thread
s_thread = Thread(target=send)
s_thread.start()