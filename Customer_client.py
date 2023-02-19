import socket
from socket import *
import select
import sys
#required flags
exit_flag = False

#cohort details
cohort_tuple = []

#cmd input
input_command = ""

def sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer):
    print("Sending cohort details to peers: ", cohort_tuple)
    # Get the hostname of the current machine
    hostname = socket.gethostname()

    # Get the IP address of the current process
    ip_address = socket.gethostbyname(hostname)

    for peer in cohort_tuple:
        tupleMsg = str(cohort_tuple)
        peerAddress = peer['ip_address']
        peerSocket = int(peer['port2'])
        flag = (ip_address != peerAddress) or ((ip_address == peerAddress) and (clientPortBank != int(peer['port1']) and clientPortPeer != peerSocket))
        if(flag):
            clientSocketPeer.sendto(tupleMsg.encode(), (peerAddress, peerSocket))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            if(peerResponse == "SUCCESS"):
                print("CLIENT->PEER:: Cohort details successfully sent to client: ", peer['name'])
            else:
                print("CLIENT->PEER:: Failed to send the cohort details to client: ", peer['name'])

def bankWorker(input_command, clientPortBank, clientPortPeer):
    global exit_flag  
    global cohort_tuple     
    print("CLIENT->BANK:: Inside Bank Thread")
    command_bank = input_command
    print("CLIENT->BANK:: command: ", command_bank)
    #sending command to bank
    print("CLIENT->BANK:: Sending command to bank")
    clientSocketBank.sendto(command_bank.encode(), (serverName, serverPort))
    print("CLIENT->BANK:: Waiting for response..")
    #waiting for response from bank
    serverResponse, serverAddress = clientSocketBank.recvfrom(2048)
    #decoding response
    rcvd_msg = serverResponse.decode()
    print("CLIENT->BANK:: Response received")
    print(rcvd_msg)

    msg_cmd = command_bank.split(" ")
    if(msg_cmd[0] == "new-cohort" and rcvd_msg != "FAILURE"):
        cohort_tuple.append(eval(rcvd_msg))
        sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer)
    
    if(msg_cmd[0] == "delete-cohort" and rcvd_msg == "SUCCESS"):
        cohort_tuple.clear()
    
    if(msg_cmd[0] == "exit" and rcvd_msg == "SUCCESS"):
        exit_flag = True
        clientSocketBank.close()
    

def peerWorker(input_command):
    global exit_flag
    if not exit_flag:
        print("CLIENT->PEER:: Inside Peer thread")
        command_peer = input_command
        print("command: ", command_peer)
        clientSocketPeer.sendto(command_peer.encode(), (serverName, serverPort))
        peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
        rcvd_msg = peerResponse.decode()
        print(rcvd_msg)

if __name__ == "__main__":
    print("********** CHECKPOINT: Customer Process **********")

    serverName = input("CLIENT:: Enter the IP address of the Bank Server Process: ")
    serverPort = int(input("CLIENT:: Enter the Port number of the Bank Server Process: "))

    #customer port for communicating with bank
    while (True):
        clientPortBank = int(input("CLIENT::Enter a port number for Bank communication b/w 8500 - 8999: "))
        if 8500 <= clientPortBank <=8999:
            break
        else:
            print("CLIENT:: Wrong port number")

    #customer port for communicating with peer
    while (True):
        clientPortPeer = int(input("CLIENT:: Enter a port number Peer communication b/w 8500 - 8999: "))
        if 8500 <= clientPortPeer <=8999 and clientPortPeer != clientPortBank:
            break
        else:
            print("CLIENT:: Wrong port number")
    
    clientSocketBank = socket(AF_INET, SOCK_DGRAM)
    clientSocketBank.bind(('', clientPortBank))
    
    clientSocketPeer = socket(AF_INET, SOCK_DGRAM)
    clientSocketPeer.bind(('', clientPortPeer))
    
    sockets = []
    sockets.append(clientSocketBank)
    sockets.append(clientSocketPeer)
    while not exit_flag:
        print("CLIENT:: Enter the command: ")
        readable, writable, exceptional = select.select(sockets + [sys.stdin], [], [])
        for sock in readable:
            if sock is sys.stdin:
                user_input_command = sys.stdin.readline().strip()
                cmd = user_input_command.split(" ")
                if(cmd[0] == "open" or cmd[0] == "new-cohort" or cmd[0] == "delete-cohort" or cmd[0] == "exit"):
                    bankWorker(user_input_command, clientPortBank, clientPortPeer)
                elif(cmd[0] == "deposit" or cmd[0] == "withdrawal" or cmd[0] == "transfer" or cmd[0] == "lost-transfer" or cmd[0] == "checkpoint" or cmd[0] == "rollback"):
                    peerWorker(user_input_command)
                else:
                    print("Wrong command")
            if sock is clientSocketBank:
                msg,ret_address = clientSocketBank.recvfrom(1024)
                if (msg.decode() == "delete-cohort"):
                    cohort_tuple = []
                    clientSocketBank.sendto("SUCCESS",ret_address)
            if sock is clientSocketPeer:
                msg,ret_address = clientSocketBank.recvfrom(1024)
                cohort_tuple.append(msg.decode())
                clientSocketBank.sendto("SUCCESS",ret_address)
        
    print("Exiting bank application")
    clientSocketPeer.close()