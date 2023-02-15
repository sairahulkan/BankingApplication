from socket import *
serverName = '10.120.70.146'
serverPort = 12000
while (True):
    clientPort = int(input("Enter a port number from 8501 - 8999: "))
    if 8501 <= clientPort <=8999:
        break

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('', clientPort))
while True:
    message = input("Input the command: ")
    clientSocket.sendto(message.encode(),(serverName, serverPort))
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    rcvd_msg = modifiedMessage.decode()
    print(rcvd_msg)
    msg_cmd = message.split(" ")
    if(msg_cmd[0] == "exit" and rcvd_msg == "SUCCESS"):
        break
clientSocket.close()