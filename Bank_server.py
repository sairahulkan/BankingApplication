from socket import *
import csv
import random
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("Bank Application Started")

customer_data_file = "customer_data.csv"
customer_fields = ["name", "balance", "ip_address", "port1", "port2", "cohort", "exit_state"]
customers = []

# Check if customer data file exists, create it if it doesn't
try:
    with open(customer_data_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            customers.append(row)
except FileNotFoundError:
    with open(customer_data_file, "w") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writeheader()

#add customer data
def add_customer(name, balance, ip_address, port1, port2):
    for row in customers:
        if (row["name"] == name and row["ip_address"] == ip_address and row["port1"] == port1 and row["port2"] == port2):
            return ("Customer Already exists!!")
    
    print("Adding customer to database...")
    customer = {}
    customer['name'] = name
    customer['balance'] = balance
    customer['ip_address'] = ip_address
    customer['port1'] = port1
    customer['port2'] = port2
    customer['cohort'] = 0
    customer['exit_state'] = 0
    customers.append(customer)

    with open(customer_data_file, "a") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writerow(customer)
    print("Customer added successfully.")
    return ("Customer added successfully.")

def new_cohert(name,n):
    print("creating Cohert")
    availableCoherts = [customer for customer in customers if ((customer['cohort'] == 0) < n)]
    if len(availableCoherts) < n:
        return "FAILURE"
    
    

#deleting the customer data
def exit_customer(name):
    print("Customer exiting the application:")
    customer_name = name
    for customer in customers:
        if customer["name"] == customer_name:
            customer["exit_state"] = 1
            with open(customer_data_file, "w") as file:
                writer = csv.DictWriter(file, fieldnames=customer_fields)
                writer.writeheader()
                writer.writerows(customers)
            print("Customer exited successfully.")
            return ("SUCCESS")        
    print("Customer not found.")
    return ("FAILURE")


while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    rcvd_command = message.decode()
    print("Command recieved: ", rcvd_command)
    command_params = rcvd_command.split(" ")
    msg =""
    if(command_params[0] == "open"):
        msg = add_customer(command_params[1], command_params[2], command_params[3], command_params[4], command_params[5])
    elif(command_params[0] == "exit"):
        msg = exit_customer(command_params[1])
    elif(command_params[0] == "new-cohert"):
        msg = new_cohert(command_params[1],command_params[2])

    serverSocket.sendto(msg.encode(), clientAddress)