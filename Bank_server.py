from socket import *
import csv
import random

print("********** CHECKPOINT: Bank Process **********")

while (True):
    serverPort = int(input("BANK:: Enter a port number from 8501 - 8999: "))
    if 8500 <= serverPort <=8999:
        break
    else:
        print("BANK:: Wrong port number")

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

print("BANK:: Bank Application Started")

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
        if (row["name"] == name):
            print("BANK->CLIENT:: customer with name {0} already found in the database", name)
            return ("FAILURE")
    
    print("BANK->CLIENT:: Adding customer to database...")
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
    print("BANK->CLIENT:: Customer added successfully.")
    return ("SUCCESS")

def new_cohort(name,n):
    updateLocalCustomers()
    for cust in customers:
        if cohortNumber < cust['cohort']:
            cohortNumber = cust['cohort']
    cohortNumber += 1
    availablecohorts = [cust for cust in customers if ((customer['cohort'] == 0) < n)]
    if len(availablecohorts) < n:
        return "FAILURE"
    for customer in customers:
        if customer["name"] == name:
            if customer["cohort"] == 0:
                customer["cohort"] = cohortNumber
                break
            else:
                return "FAILURE"
    print("creating cohort")
    cohortTuples = random.sample(availablecohorts,n-1)
    cohortTuples.append(customer)  
    for cohortCustomer in cohortTuples:
        for customer in customers:
            if cohortCustomer['name'] == customer['name']:
                customer['cohort'] = cohortNumber
    with open(customer_data_file, "w") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writeheader()
        writer.writerows(customers) 
    for customer in cohortTuples:
        Keys = list(customer.keys())
        for key in Keys:
            if key not in ['name', 'balance', 'ip_address', 'port1','port2']:
                del customer[key]   
    return cohortTuples

#deleting the cohort   
def delete_cohort(name):
    #fetch the cohort number and delete the cohort information in the database
    cohort_num = 0
    for customer in customers:
        if(customer["name"] == name):
            cohort_num = customer["cohort"]
            if cohort_num == 0:
                return "FAILURE"
            break

    #fetching the customers with same cohort 
    customer_in_cohort = {}
    for customer in customers:
        temp_cust = []
        if(customer["cohort"] == cohort_num):
            customer["cohort"] = 0
            temp_cust['ip_address'] = customer['ip_address']
            temp_cust['port2'] = customer['port2']
            customer_in_cohort.append(temp_cust)

    msg = "delete-cohort"
    flag = True
    for cust_in_coh in customer_in_cohort:
        serverSocket.sendto(msg.encode(), (cust_in_coh['ip_address'], int(cust_in_coh['port2'])))
        reply, cust_address = serverSocket.recvfrom(2048)
        if(reply != "SUCCESS"):
            flag = False
            break
    
    if(flag == False):
        return "FAILURE"
    else:
        with open(customer_data_file, "w") as file:
            writer = csv.DictWriter(file, fieldnames=customer_fields)
            writer.writeheader()
            writer.writerows(customers)
        return "SUCCESS"


#deleting the customer data
def exit_customer(name):
    print("BANK->CLIENT:: Customer exiting the application:")
    customer_name = name
    for customer in customers:
        if customer["name"] == customer_name:
            customer["exit_state"] = 1
            with open(customer_data_file, "w") as file:
                writer = csv.DictWriter(file, fieldnames=customer_fields)
                writer.writeheader()
                writer.writerows(customers)
            print("BANK->CLIENT:: Customer exited successfully.")
            return ("SUCCESS")     
    print("BANK->CLIENT:: Customer not found.")
    return ("FAILURE")

def updateLocalCustomers():
    customers.clear()
    try:
        with open(customer_data_file, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers.append(row)
    except FileNotFoundError:
        with open(customer_data_file, "w") as file:
            writer = csv.DictWriter(file, fieldnames=customer_fields)
            writer.writeheader()

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
    elif(command_params[0] == "new-cohort"):
        msg = new_cohort(command_params[1],command_params[2])
    elif(command_params[0] == "delete-cohort"):
        msg = delete_cohort(command_params[1])

    serverSocket.sendto(msg.encode(), clientAddress)
