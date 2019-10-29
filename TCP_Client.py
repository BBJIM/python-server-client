import datetime
import os
import pickle
import socket
import sys
import threading

# global vars
isConnected = False
last_time_of_ka_msg = None
client = None


"""
keep_connection_alive:

The keep alive method that checks every 10 seconds if 
there is still a connection message from the server
"""


def keep_connection_alive((connection_client)):
    try:
        global isConnected
        global last_time_of_ka_msg
        global client

        # if the differnce between the current time and
        # last_time_of_ka_msg(the last time the client
        # received the keep_connection_alive message)
        # is greater then 10 seconds then it closes
        # the conneciton
        isConnected = False if (datetime.datetime.now() -
                                last_time_of_ka_msg).total_seconds() > 10 else isConnected
        if isConnected:
            # the timer that calls itself at the .Timer() callback parameter
            threading.Timer(10, keep_connection_alive,
                            (connection_client,)).start()
        else:
            # closes the connection
            print("Connection is over")
            connection_client.close()
            client.close()
            sys.exit()
            return False
    except:
        print("Disconnected")


"""
connectionThread:

The keep_connection_alive thread method that connects to
the server and calls the keep_connection_alive method
"""


def connectionThread(SERVER, PORT):
    try:
        global isConnected
        global last_time_of_ka_msg
        # connects to the server
        connection_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection_client.connect((SERVER, PORT))
        keep_connection_alive((connection_client))
        while True:
            # receiving data from server
            connection_client.recv(1024)
            # after receiving data from server, it updates the
            # last_time_of_ka_msg global var to the current time
            last_time_of_ka_msg = datetime.datetime.now()
    except:
        print("Disconnected")


"""
main:

The main method of the program, when the server starts, 
this method get called
"""


def main():
    PORT = 8083
    global isConnected
    global client
    global last_time_of_ka_msg
    isConnected = False

    while not isConnected:
        try:
            # connects to the server
            print("\nEnter the server IP address\n")
            SERVER = raw_input(">>>")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((SERVER, PORT))
            # activates the keep_connection_alive thread
            last_time_of_ka_msg = datetime.datetime.now()
            threading._start_new_thread(
                connectionThread, (SERVER, PORT+1))
            isConnected = True
        except:
            print(
                "\nCould not connect the server, please try again\n")
    if isConnected:
        isLoggedIn = False
        print("Connection Successful")
        in_data = client.recv(1024)
        print("From Server: {}".format(in_data))
        # the loop for send/recv while the client is not logged in
        while not isLoggedIn and isConnected:
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            # if the user is not logged in then the only actions
            # he can activate are "connect" and "register"
            if check_command == "register" or check_command == "connect":
                client.sendall(out_data)
                in_data = client.recv(1024)
                loginTupleResponse = pickle.loads(in_data)
                print("From Server: {}".format(loginTupleResponse[1]))
                # if the response from the server is that the loging in
                # action worked then it goes to the second while loop
                if loginTupleResponse[0]:
                    isLoggedIn = True
                    break
            else:
                if isConnected:
                    print(
                        "From Client: You can only enter the register or connect command at this time")

        # the loop for send/recv while the client is logged in
        while isLoggedIn and isConnected:
            print("Enter the command you want to activate")
            # gets input
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            # cant call the "connect" and "register" actions if the
            # client is already logged in
            if check_command == "register" or check_command == "connect":
                print("From Client: You are already logged in")
            else:
                # sends the input data
                client.sendall(out_data)
                # if the actions is not print_screen
                if check_command != "print_screen":
                    # prints the data from the server
                    in_data = client.recv(4096)
                    print("From Server: {}".format(in_data))
                    # if the response is bye bye then it closes the
                    # connection and stops the program
                    if in_data.lower() == "bye bye":
                        client.close()
                        sys.exit()
                # if the actions is print_screen
                else:
                    # the print_screen action sends alot of data in a
                    # loop until the message "PRINT_IMAGE" is received
                    bytesArray = []
                    in_data = client.recv(16384)
                    while in_data != "PRINT_IMAGE":
                        bytesArray.append(in_data)
                        in_data = client.recv(16384)
                    # saves the bytes data
                    data = b"{}".format("".join(bytesArray))
                    dirname = os.path.dirname(__file__)
                    # gets the name of the client
                    client.sendall("NAME")
                    name = client.recv(1024)
                    # saves the image from the server with this client name
                    with open("{}/{}.png".format(dirname, name), 'ab') as img:
                        img.write(data)
                        img.close()
                    print("Image has be saved in the client dir")
        print("Connection is over")
        client.close()
        sys.exit()


if __name__ == "__main__":
    main()
