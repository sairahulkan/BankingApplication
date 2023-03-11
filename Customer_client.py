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

#State Variables:
customer_name = ""
bank_balance = 0
class cohortCustomerClass:
    name = ""
    ipAddress = ""
    currentBalance = 0
    lastLabelrecvd = {}
    firstLabelSent = {}
    lastLabelSent = {}
    oKToTakeChkPoint = True
    willingToRollBack = True
    resumeExecution = True
    rollCohort = []
    chkptCohort = []

    def print_data(self):
        print("Customer Details:")
        print("Name: ", self.name)
        print("Bank balance: ", self.currentBalance)
        print("lastLabelrecvd: ", self.lastLabelrecvd)
        print("firstLabelSent: ", self.firstLabelSent)
        print("lastLabelSent: ", self.lastLabelSent)
        print("oKToTakeChkPoint: ", self.oKToTakeChkPoint)
        print("willingToRollBack: ", self.willingToRollBack)
        print("resumeExecution: ", self.resumeExecution)
        print("rollCohort: ", self.rollCohort)
        print("chkptCohort: ", self.chkptCohort)

    def initializeData(self):
        global cohort_tuple
        if cohort_tuple:
            for cohortPeer in cohort_tuple:
                self.firstLabelSent.update({cohortPeer['name'] : 0})
                self.lastLabelrecvd.update({cohortPeer['name'] : 0})
                self.lastLabelSent.update({cohortPeer['name'] : 999})

cohortCustomer = cohortCustomerClass()

#once the new cohort is created, the cohort details are sent to other peers in the cohort
def sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer):
    print("PEER:: Sending cohort details to peers: ", cohort_tuple)

    #update object
    cohortCustomer.initializeData()
    cohortCustomer.print_data()

    (ip_address, port) = clientSocketBank.getsockname()

    for peer in cohort_tuple:
        tupleMsg = str(cohort_tuple)
        peerAddress = peer['ip_address']       
        peerSocket = int(peer['port2'])

        flag = (ip_address != peerAddress) or ((ip_address == peerAddress) and (int(clientPortBank) != int(peer['port1']) and int(clientPortPeer) != peerSocket))
        if(flag):
            clientSocketPeer.sendto(tupleMsg.encode(), (peerAddress, peerSocket))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            if(peerResponse.decode() == "SUCCESS"):
                print("\nCLIENT->PEER:: Cohort details successfully sent to client: ", peer['name'])
            else:
                continue

#Bank worker function
def bankWorker(input_command, clientPortBank, clientPortPeer):
    global exit_flag  
    global cohort_tuple     
    global customer_name
    global bank_balance

    command_bank = input_command
    #sending command to bank
    print("CLIENT->BANK:: Sending command to bank...")
    clientSocketBank.sendto(command_bank.encode(), (serverName, serverPort))
    print("CLIENT->BANK:: Waiting for response...")
    #waiting for response from bank
    serverResponse, serverAddress = clientSocketBank.recvfrom(2048)
    #decoding response
    rcvd_msg = serverResponse.decode()
    print("CLIENT->BANK:: Response received: ", rcvd_msg)

    msg_cmd = command_bank.split(" ")
    if(msg_cmd[0] == "open" and rcvd_msg == "SUCCESS"):
        #object update
        customer_name = msg_cmd[1]
        bank_balance = int(msg_cmd[2])
        cohortCustomer.name = customer_name
        cohortCustomer.currentBalance = bank_balance
        cohortCustomer.ipAddress = msg_cmd[3]
        print("Customer: " + customer_name + " Balance: " + str(bank_balance))
    
    if(msg_cmd[0] == "new-cohort" and rcvd_msg != "FAILURE"):
        cohort_tuple = (eval(rcvd_msg))
        sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer)
    
    if(msg_cmd[0] == "delete-cohort" and rcvd_msg == "SUCCESS"):
        cohort_tuple.clear()
    
    if(msg_cmd[0] == "exit" and rcvd_msg == "SUCCESS"):
        exit_flag = True
        clientSocketBank.close()
    
#peer to peer worker function
def peerWorker(input_command):
    global exit_flag
    global bank_balance
    if not exit_flag:
        command = input_command.split(" ")
        if((command[0] == "deposit") or (command[0]) == "withdrawal"):
            self_functions(input_command)
        else:
            print("CLIENT->PEER:: Inside Peer Function")
            command_peer = input_command
            print("command: ", command_peer)
            
            if (command[0] == "transfer"):
                inCohortFlag = False
                for tuple in cohort_tuple:
                    if tuple["name"] == command[2]:
                        inCohortFlag = True
                        recieverTuple = tuple
                        if(int(command[1]) > bank_balance):
                            print("Transfer cannot be performed due to insufficient funds")
                            return
                        else:
                            print("Transfer initiated.")
                            bank_balance = bank_balance - int(command[1])
                            #object update
                            cohortCustomer.currentBalance = bank_balance
                            cohortCustomer.firstLabelSent[command[2]] += 1
                            receiverMessage = 'transfer' + ' ' + command[1] + ' ' + cohortCustomer.name + ' ' + str(cohortCustomer.firstLabelSent[command[2]])
                            print("Command to transfer: ", receiverMessage)
                            cohortCustomer.print_data()
                            clientSocketPeer.sendto(receiverMessage.encode(),(recieverTuple['ip_address'], int(recieverTuple['port2'])))
                if(inCohortFlag != True):
                    print("Receiver is not in your cohort. Enter another")

            elif(command[0] == "lost-transfer"):
                print("\nSimulating a lost transfer...")
                if (command[0] == "transfer"):
                    inCohortFlag = False
                    for tuple in cohort_tuple:
                        if tuple["name"] == command[2]:
                            inCohortFlag = True
                            recieverTuple = tuple
                            if(int(command[1]) > bank_balance):
                                print("Transfer cannot be performed due to insufficient funds")
                                return
                            else:
                                print("Transfer initiated.")
                                bank_balance = bank_balance - int(command[1])
                                #object update
                                cohortCustomer.currentBalance = bank_balance
                                cohortCustomer.firstLabelSent[command[2]] += 1
                                cohortCustomer.print_data()
                                
                    if(inCohortFlag != True):
                        print("Receiver is not in your cohort. Enter another")

            else:
                clientSocketPeer.sendto(command_peer.encode(), (serverName, serverPort))
                peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
                rcvd_msg = peerResponse.decode()
                print(rcvd_msg)


#self functions:
def self_functions(input_command):
    global exit_flag
    global bank_balance
    if not exit_flag:
        print("Functions performing at customer end.")
        cmnd = input_command.split(" ")
        if(cmnd[0] == "deposit"):
            print("Performing a deposit of " + cmnd[1] + " USD.")
            #object update
            bank_balance = bank_balance + int(cmnd[1])
            cohortCustomer.currentBalance = bank_balance
            print("Latest bank balance: ", bank_balance)
        elif(cmnd[0] == "withdrawal"):
            if(bank_balance < int(cmnd[1])):
                print("Withdrawal cannot be performed due to insufficient funds.")
                print("Bank balance: ", bank_balance)
            else:
                print("Withdrawal of amount " + cmnd[1] + " USD.")
                #object update
                bank_balance = bank_balance - int(cmnd[1])
                cohortCustomer.currentBalance = bank_balance
                print("Updated bank balance: ", bank_balance)
        else:
            print("Wrong command.")




#main function
if __name__ == "__main__":
    print("********** CHECKPOINT: Customer Process **********")
    serverName = input("\nCLIENT:: Enter the IP address of the Bank Server Process: ")
    serverPort = int(input("CLIENT:: Enter the Port number of the Bank Server Process: "))

    #customer port for communicating with bank
    while (True):
        clientPortBank = int(input("\nCLIENT:: Enter a port number for Bank communication b/w 8500 - 8999: "))
        if 8500 <= clientPortBank <=8999:
            break
        else:
            print("CLIENT:: Wrong port number")

    #customer port for communicating with peer
    while (True):
        clientPortPeer = int(input("CLIENT:: Enter a port number for Peer communication b/w 8500 - 8999: "))
        if 8500 <= clientPortPeer <=8999 and clientPortPeer != clientPortBank:
            break
        else:
            print("CLIENT:: Wrong port number")
    
    clientSocketBank = socket(AF_INET, SOCK_DGRAM)
    clientSocketBank.bind(('', clientPortBank))
    print("CLIENT:: Socket to communicate with Bank created successfully.")
    clientSocketPeer = socket(AF_INET, SOCK_DGRAM)
    clientSocketPeer.bind(('', clientPortPeer))
    print("CLIENT:: Socket to communicate with Peer created successfully.")
    
    sockets = []
    sockets.append(clientSocketBank)
    sockets.append(clientSocketPeer)

    #checking each socket if the data is present at the socket
    while not exit_flag:
        print("\nCLIENT:: Enter the command to send to bank: ")
        readable, writable, exceptional = select.select(sockets + [sys.stdin], [], [])

        #foreach socket 
        for sock in readable:
            #if there is any data
            if sock is sys.stdin:
                user_input_command = sys.stdin.readline().strip()
                cmd = user_input_command.split(" ")

                if(cmd[0] == "open" or cmd[0] == "new-cohort" or cmd[0] == "delete-cohort" or cmd[0] == "exit"):
                    bankWorker(user_input_command, clientPortBank, clientPortPeer)
                elif(cmd[0] == "deposit" or cmd[0] == "withdrawal" or cmd[0] == "transfer" or cmd[0] == "lost-transfer" or cmd[0] == "checkpoint" or cmd[0] == "rollback"):
                    peerWorker(user_input_command)
                else:
                    print("CLIENT:: Wrong command")

            if sock is clientSocketBank:
                msg,ret_address = clientSocketBank.recvfrom(1024)
                if (msg.decode() == "delete-cohort"):
                    print("\nCLIENT:: Received 'delete-cohort' command from bank.")

                    print("\nCLIENT:: Current cohort (before deleting): ", cohort_tuple)
                    cohort_tuple.clear()
                    print("\nCLIENT:: Cohort tuple (after deleting): ", cohort_tuple)
                    print("CLIENT:: Cohort deleted successfully.")
                    clientSocketBank.sendto("SUCCESS".encode(),ret_address)

            if sock is clientSocketPeer:
                msg,ret_address = clientSocketPeer.recvfrom(1024)
                msgData = msg.decode().split(' ')
                if (msgData[0] == 'transfer'):
                    bank_balance = bank_balance + int(msgData[1])
                    cohortCustomer.currentBalance = bank_balance
                    if(msgData[2] not in cohortCustomer.chkptCohort):
                        cohortCustomer.chkptCohort.append(msgData[2])
                    cohortCustomer.lastLabelrecvd[msgData[2]] += 1
                    cohortCustomer.print_data()
                    print("Updated bank balance: ", bank_balance)
                else:
                    print("\nCLIENT:: Received Cohort tuple")
                    cohort_tuple = eval(msg.decode())
                    print("\nCLIENT:: Current Cohort: ", cohort_tuple)
                    cohortCustomer.initializeData()
                    cohortCustomer.print_data()
                    clientSocketBank.sendto("SUCCESS".encode(),ret_address)
        
    print("\nCLIENT:: Exiting bank application")
    clientSocketPeer.close()
