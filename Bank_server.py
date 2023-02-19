from socket import *
import csv
import random

print("********** CHECKPOINT: Bank Process **********")

#Input port numbers
while (True):
    serverPort = int(input("BANK:: Enter a port number from 8500 - 8999: "))
    if 8500 <= serverPort <=8999:
        break
    else:
        print("BANK:: Wrong port number")

#create socket
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("BANK:: Bank Application Started")

#read the database
customer_data_file = "customer_data.csv"
customer_fields = ["name", "balance", "ip_address", "port1", "port2", "cohort", "exit_state"]
customers = []
cohortNumber = 0

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

#printing the customer data
def print_customer_data():
    for customer in customers:
        print(customer)


#add customer data
def open_customer(name, balance, ip_address, port1, port2):
    print(customers)
    for row in customers:
        if (row["name"] == name):
            if(row["exit_state"]== '0'):
                print("BANK->CLIENT:: customer with name {0} already found in the database", name)
                return ("FAILURE")
            else:
                row["exit_state"] = '0'
                row['balance'] = balance
                row['ip_address'] = ip_address
                row['port1'] = port1
                row['port2'] = port2
                row['cohort'] = '0'
                print("BANK->CLIENT:: Welcome back {0} !!", name)
                with open(customer_data_file, "a") as file:
                    writer = csv.DictWriter(file, fieldnames=customer_fields)
                    writer.writerows(customers)
                return("SUCCESS")
    
    print("BANK->CLIENT:: Adding customer to database...")
    customer = {}
    customer['name'] = name
    customer['balance'] = balance
    customer['ip_address'] = ip_address
    customer['port1'] = port1
    customer['port2'] = port2
    customer['cohort'] = '0'
    customer['exit_state'] = '0'

    #updating the local db
    customers.append(customer)

    #updating the main db
    with open(customer_data_file, "a") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writerow(customer)
    print("BANK->CLIENT:: Customer added successfully.")
    return ("SUCCESS")

#creating a new cohort
def new_cohort(name,n):
    #checking available customers not in any cohort
    global cohortNumber
    availablecohorts = []
    for cust in customers:
        print(type(cust['cohort']))
        if(cust['cohort'] == '0' and cust['name'] != name):
            availablecohorts.append(cust)

    print("Available cohorts: \n", availablecohorts)

    if len(availablecohorts) < int(n) or int(n) < 2:
        print("fail 1")
        return "FAILURE"
    
    for cust in customers:
        if cohortNumber < int(cust['cohort']):
            cohortNumber = int(cust['cohort'])
    cohortNumber += 1

    print("\nCohort number to be assigned: ", cohortNumber)
    
    curr_cust = {}
    for customer in customers:
        print("Customer:" + customer["name"] + " Cohort: " +customer["cohort"] + " type: " + str(type(customer["cohort"])))
        if customer["name"] == name:
            if(customer['cohort'] != '0'):
                print("fail 2")
                return "FAILURE"
            else:
                customer["cohort"] = str(cohortNumber)
                curr_cust = customer
                break
            
    print("\ncreating cohort Tuples...")
    num = int(n)
    cohortTuples = random.sample(availablecohorts,num-1)
    cohortTuples.append(curr_cust)
   
    print("\nCohort tuples: \n", cohortTuples)

    for cohortCustomer in cohortTuples:
        for customer in customers:
            if cohortCustomer['name'] == customer['name']:
                customer['cohort'] = str(cohortNumber)
    print("\ncheck2\n")

    with open(customer_data_file, "w") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writeheader()
        writer.writerows(customers) 
    print("\ncheck3\n")

    for customer in cohortTuples:
        Keys = list(customer.keys())
        for key in Keys:
            if key not in ['name', 'balance', 'ip_address', 'port1','port2']:
                del customer[key]   
    print("\nFinal Cohort Tuples: \n", cohortTuples)
    return str(cohortTuples)

#deleting the cohort   
def delete_cohort(name):
    print(customers)
    #fetch the cohort number and delete the cohort information in the database
    cohort_num = 0
    for customer in customers:
        if(customer["name"] == name):
            cohort_num = customer['cohort']
            customer['cohort'] = 0
            if cohort_num == 0:
                print("fail 3")
                return "FAILURE"
            break

    #fetching the customers with same cohort 
    customer_in_cohort = []
    for customer in customers:
        temp_cust = {}
        if(customer['cohort'] == cohort_num):
            print("/nNulling"+customer["name"])
            customer['cohort'] = 0
            temp_cust['name'] = customer['name']
            temp_cust['ip_address'] = customer['ip_address']
            temp_cust['port1'] = customer['port1']
            customer_in_cohort.append(temp_cust)

    msg = "delete-cohort"
    flag = True
    for cust_in_coh in customer_in_cohort:
        print("bank-sending to customer")
        serverSocket.sendto(msg.encode(), (cust_in_coh['ip_address'], int(cust_in_coh['port1'])))
        reply, cust_address = serverSocket.recvfrom(2048)
        if(reply.decode() != "SUCCESS"):
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
    print(customers)
    print("BANK->CLIENT:: Customer exiting the application:")
    customer_name = name
    for customer in customers:
        #If customer is present in the db and not in any cohort, then he can exit
        if customer["name"] == customer_name and customer['cohort'] == '0':
            customer["exit_state"] = '1'
            with open(customer_data_file, "w") as file:
                writer = csv.DictWriter(file, fieldnames=customer_fields)
                writer.writeheader()
                writer.writerows(customers)
            print("BANK->CLIENT:: Customer exited successfully.")
            return ("SUCCESS")
        #if the customer is in cohort then he cannot exit
        elif(customer["name"] == customer_name and customer['cohort'] != '0'):
            print("BANK->CLIENT:: Customer is in Cohort. Hence cannot exit")
            return("FAILURE")
    print("BANK->CLIENT:: Customer not found.")
    return ("FAILURE")

while True:
    print("BANK:: Waiting for a command from customers")
    message, clientAddress = serverSocket.recvfrom(2048)
    rcvd_command = message.decode()
    print("Command recieved: ", rcvd_command)
    command_params = rcvd_command.split(" ")
    msg =""
    if(command_params[0] == "open"):
        msg = open_customer(command_params[1], command_params[2], command_params[3], command_params[4], command_params[5])
    elif(command_params[0] == "exit"):
        msg = exit_customer(command_params[1])
    elif(command_params[0] == "new-cohort"):
        msg = new_cohort(command_params[1],command_params[2])
    elif(command_params[0] == "delete-cohort"):
        msg = delete_cohort(command_params[1])

    serverSocket.sendto(msg.encode(), clientAddress)
    print("BANK:: Sent the response to customers")
