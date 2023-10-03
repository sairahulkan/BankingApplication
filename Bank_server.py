from socket import *
import csv
import random

print("********* CHECKPOINT: Bank Process **********")

#Input port numbers from user
while (True):
    serverPort = int(input("BANK:: Enter a port number from 8500 - 8999: "))
    if 8500 <= serverPort <=8999:
        break
    else:
        print("BANK:: Wrong port number")

#create socket function called
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print("\nBANK:: Bank Socket created successfully.")

#read the database
customer_data_file = "data.csv"
customer_fields = ['name', 'balance', 'ip_address', 'port1', 'port2', 'cohort', 'exit_state']
customers = []
cohortNumber = 0

# Create customer data file if it doesn't exist
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
    for row in customers:
        if (row['name'] == name):
            if(row['exit_state']== '0'):
                print(f"BANK->CLIENT:: Customer with name {name} already found in the database")
                return ("FAILURE")
            else:
                row['exit_state'] = '0'
                row['balance'] = balance
                row['ip_address'] = ip_address
                row['port1'] = port1
                row['port2'] = port2
                row['cohort'] = '0'
                print(f"BANK->CLIENT:: Welcome back {name}!!")
                with open(customer_data_file, "w") as file:
                    writer = csv.DictWriter(file, fieldnames=customer_fields)
                    writer.writeheader()
                    writer.writerows(customers)
                return("SUCCESS")
    
    print(f"BANK->CLIENT:: Adding new customer {name} to database...")
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
        writer.writerows(customers)
    print(f"BANK->CLIENT:: Customer {name} added successfully.\n")
    return ("SUCCESS")

#creating a new cohort
def new_cohort(name,n):
    #checking available customers not in any cohort
    global customers
    global cohortNumber
    availablecohorts = []

    for cust in customers:
        if(cust['cohort'] == '0' and cust['name'] != name and cust['exit_state'] != '1'):
            availablecohorts.append(cust)
    print("BANK:: Available cohorts: \n", availablecohorts)

    #checking the cohort length
    if len(availablecohorts)+1 < int(n) or int(n) < 2:
        print("BANK:: Invalid cohort / Cohort limit exceeded\n")
        return "FAILURE"
    
    #finding cohort number to assign
    for cust in customers:
        if cohortNumber < int(cust['cohort']):
            cohortNumber = int(cust['cohort'])
    cohortNumber += 1
    print("\nBANK:: Cohort number to be assigned: ", cohortNumber)
    
    #finding if the current customer is already in any cohort
    curr_cust = {}
    for customer in customers:
        if customer["name"] == name:
            if(customer['cohort'] != '0'):
                print("\nBANK:: Customer already present in the cohort ", customer['cohort'])
                return "FAILURE"
            else:
                customer['cohort'] = str(cohortNumber)
                curr_cust = customer
                break    
    print("BANK:: creating cohort Tuples...")

    #randomly choosing the customers
    num = int(n)
    cohortTuples = random.sample(availablecohorts,num-1)
    cohortTuples.append(curr_cust)
    print("\nBANK:: Cohort tuples: \n", cohortTuples)

    #changing the cohort numbers in the database
    for cohortCustomer in cohortTuples:
        for customer in customers:
            if cohortCustomer['name'] == customer['name']:
                customer['cohort'] = str(cohortNumber)

    with open(customer_data_file, "w") as file:
        writer = csv.DictWriter(file, fieldnames=customer_fields)
        writer.writeheader()
        writer.writerows(customers)
    print("\nBANK:: Cohort created successfully.\n")
    return str(cohortTuples)

#deleting the cohort   
def delete_cohort(name):
    #fetch the cohort number and delete the cohort information in the database
    global customers
    cohort_num = '0'

    #finding the cohort group of the customer
    for customer in customers:
        if(customer['name'] == name):
            cohort_num = customer['cohort']
            if cohort_num == '0':
                print(f"\nBANK:: Customer {name} not in any cohort.")
                return "FAILURE"
            break

    #fetching the customers with same cohort 
    customer_in_cohort = []
    for customer in customers:
        temp_cust = {}
        if(customer['cohort'] == cohort_num and customer['name'] != name):
            customer['cohort'] = '0'
            temp_cust['ip_address'] = customer['ip_address']
            temp_cust['port1'] = customer['port1']
            customer_in_cohort.append(temp_cust)
        elif (customer['cohort'] == cohort_num and customer['name'] == name):
            customer['cohort'] = '0'
    print("\nBANK:: Customers in cohort: ", customer_in_cohort)

    #Sending the delete-cohort command to other peers so they can delete at their end
    msg = "delete-cohort"
    flag = True
    for cust_in_coh in customer_in_cohort:
        print("\nBANK:: Sending the \"delete-cohort\" command to ", cust_in_coh['ip_address'])
        serverSocket.sendto(msg.encode(), (cust_in_coh['ip_address'], int(cust_in_coh['port1'])))
        reply, cust_address = serverSocket.recvfrom(2048)
        reply = reply.decode()
        if(reply != "SUCCESS"):
            flag = False
            break
        else:
            continue
    
    #checking if all the customers have deleted the cohort
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
    global customers
    print(f"BANK->CLIENT:: Customer {name} trying to exit the application.")

    customer_name = name
    for customer in customers:
        #If customer is present in the db and not in any cohort, then he can exit
        if customer['name'] == customer_name and customer['cohort'] == '0':
            customer['exit_state'] = '1'
            with open(customer_data_file, "w") as file:
                writer = csv.DictWriter(file, fieldnames=customer_fields)
                writer.writeheader()
                writer.writerows(customers)
            print(f"BANK->CLIENT:: Customer {name} exited successfully.")
            return ("SUCCESS")
        #if the customer is in cohort then he cannot exit
        elif(customer['name'] == customer_name and customer['cohort'] != '0'):
            print(f"\nBANK->CLIENT:: Customer {name} is already in Cohort. Hence he cannot exit.\n")
            return("FAILURE")
    print(f"\nBANK->CLIENT:: Customer {name} not found.\n")
    return ("FAILURE")

while True:
    print("BANK:: Waiting for a command from customers..\n")
    message, clientAddress = serverSocket.recvfrom(2048)
    rcvd_command = message.decode()
    print(f"BANK:: Command recieved from customer: {rcvd_command} \n")
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
    print("BANK:: Sent the response message to customers\n")
