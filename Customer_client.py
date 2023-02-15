from socket import *

#required flags
exit_flag = False

#cohort details
cohort_tuple = {}

#cmd input
input_command = ""

def sendCohortDetailsToPeers(rcvd_msg):
    print("Sending cohort details to peers: ", rcvd_msg)


def bankWorker(input_command):
    global exit_flag        
    print("CLIENT->BANK:: Inside Bank Thread")
    command_bank = input_command
    print("command: ", command_bank)
    #sending command to bank
    print("Sending command to bank")
    clientSocketBank.sendto(command_bank.encode(), (serverName, serverPort))
    print("Waiting for response..")
    #waiting for response from bank
    serverResponse, serverAddress = clientSocketBank.recvfrom(2048)
    #decoding response
    rcvd_msg = serverResponse.decode()
    print("Response received")
    print(rcvd_msg)

    msg_cmd = command_bank.split(" ")
    if(msg_cmd[0] == "new-cohort" and rcvd_msg != "FAILURE"):
        sendCohortDetailsToPeers(rcvd_msg)
    
    if(msg_cmd[0] == "exit" and rcvd_msg == "SUCCESS"):
        exit_flag = True
        clientSocketBank.close()
    

def peerWorker(input_command):
    global exit_flag
    if not exit_flag:
        print("CLIENT->PEER:: Inside Peer thread")
        command_peer = input_command
        print("commad: ", command_peer)
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


    while not exit_flag:
        user_input_command = input("CLIENT:: Enter the command: ")
        cmd = user_input_command.split(" ")
        if(cmd[0] == "open" or cmd[0] == "new-cohort" or cmd[0] == "delete-cohort" or cmd[0] == "exit"):
            bankWorker(user_input_command)
        elif(cmd[0] == "deposit" or cmd[0] == "withdrawal" or cmd[0] == "transfer" or cmd[0] == "lost-transfer" or cmd[0] == "checkpoint" or cmd[0] == "rollback"):
            peerWorker(user_input_command)

        else:
            print("Wrong command")


    print("Exiting bank application")
    clientSocketPeer.close()