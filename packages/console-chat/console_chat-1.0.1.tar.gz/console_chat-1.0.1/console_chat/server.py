import socket
import threading
import syslog

host = '127.0.0.1'
port = 50

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


def disconnect(client):
    index = clients.index(client)
    clients.remove(client)
    client.close()
    nickname = nicknames[index]
    broadcast('{} left!'.format(nickname).encode('ascii'))
    nicknames.remove(nickname)


def broadcast(message, currentClient=None):
    for client in clients:
        if client != currentClient:
            client.send(message)


def handle(client):
    index = clients.index(client)
    while True:
        try:
            message = client.recv(1024)
            print(message)
            syslog.syslog(message.decode('ascii'))
            broadcast(message, client)
            client.send('(Message send successfully!)'.encode('ascii'))
        except:
            disconnect(client)
            break


def receive():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send('NicknameKeyWord'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii'))
        client.send(' Connected to server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server started!")
receive()
