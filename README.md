# Bank and Customer Process Application

This project is a comprehensive application designed for managing bank processes and customer interactions using sockets for communication. It features secure customer data management, cohort creation, and rollback mechanisms.

## Features

- **Bank Process**:
  - Manages customer data with functionalities to open accounts, exit, create cohorts, and delete cohorts.
  - Communicates with customers via UDP sockets.
  - Stores customer data in a CSV file.

- **Customer Process**:
  - Allows customers to open accounts, perform deposits and withdrawals, transfer money, and handle checkpoints and rollbacks.
  - Communicates with the bank and other peers via UDP sockets.

## Getting Started

### Prerequisites

- Python 3.x

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/bank-customer-process.git
    cd bank-customer-process
    ```

2. Ensure you have the necessary Python packages installed:

    ```bash
    pip install -r requirements.txt
    ```

3. Create an initial `data.csv` file with the required fields if it doesn't exist:

    ```plaintext
    name,balance,ip_address,port1,port2,cohort,exit_state
    ```

### Running the Application

1. **Start the Bank Process**:

    ```bash
    python bank_process.py
    ```

    - Input a port number between 8500 and 8999 when prompted.

2. **Start the Customer Process**:

    ```bash
    python customer_process.py
    ```

    - Input the IP address and port number of the bank server when prompted.
    - Input unique port numbers for communication with the bank and peers between 8500 and 8999.

### Commands

#### Bank Commands

- **Open Customer**: 
    ```
    open <name> <balance> <ip_address> <port1> <port2>
    ```
- **Exit Customer**: 
    ```
    exit <name>
    ```
- **Create New Cohort**: 
    ```
    new-cohort <name> <number_of_customers>
    ```
- **Delete Cohort**: 
    ```
    delete-cohort <name>
    ```

#### Customer Commands

- **Deposit Money**: 
    ```
    deposit <amount>
    ```
- **Withdraw Money**: 
    ```
    withdrawal <amount>
    ```
- **Transfer Money**: 
    ```
    transfer <amount> <receiver_name>
    ```
- **Lost Transfer Simulation**: 
    ```
    lost-transfer <amount> <receiver_name>
    ```
- **Checkpoint**: 
    ```
    checkpoint
    ```
- **Rollback**: 
    ```
    rollback
    ```

### Exiting the Application

To exit the application, use the `exit` command in the customer process. This will close the sockets and end the program.
