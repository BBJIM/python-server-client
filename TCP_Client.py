import datetime
import os
import pickle
import socket
import sys
import threading

# TODO: add try catch

isConnected = False
t = datetime.datetime.now()
client = None


def ab((connection_client)):
    global isConnected
    global t
    global client
    isConnected = False if (datetime.datetime.now() -
                            t).total_seconds() > 10 else isConnected
    if isConnected:
        threading.Timer(10, ab, (connection_client,)).start()
    else:
        print("Connection is over")
        connection_client.close()
        client.close()
        sys.exit()
        return False


def connectionThread(SERVER, PORT):
    global isConnected
    global t

    connection_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_client.connect((SERVER, PORT))
    ab((connection_client))
    while True:
        in_data = connection_client.recv(1024)
        t = datetime.datetime.now()


def main():
    SERVER = "127.0.0.1"
    PORT = 8083
    global isConnected
    global client
    isConnected = False
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        threading._start_new_thread(
            connectionThread, (SERVER, PORT+1))
        isConnected = True
    except:
        print("\nCould not connect the server\n")
    if isConnected:
        isLoggedIn = False
        in_data = client.recv(1024)
        print("From Server: {}".format(in_data))
        while not isLoggedIn and isConnected:
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            if check_command == "register" or check_command == "connect":
                client.sendall(out_data)
                in_data = client.recv(1024)
                loginTupleResponse = pickle.loads(in_data)
                print("From Server: {}".format(loginTupleResponse[1]))
                if loginTupleResponse[0]:
                    isLoggedIn = True
                    break
            else:
                if isConnected:
                    print(
                        "From Client: You can only enter the register or connect command at this time")
        if isConnected:
            print("Enter the command you want to activate")

        while isLoggedIn and isConnected:
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            if check_command == "register" or check_command == "connect":
                print("From Client: You are already logged in")
            else:
                client.sendall(out_data)
                if check_command != "print_screen":
                    in_data = client.recv(4096)
                    print("From Server: {}".format(in_data))
                    if in_data.lower() == "bye bye":
                        client.close()
                        sys.exit()
                else:
                    bytesArray = []
                    in_data = client.recv(16384)
                    while in_data != "PRINT_IMAGE":
                        bytesArray.append(in_data)
                        in_data = client.recv(16384)
                    data = b"{}".format("".join(bytesArray))
                    dirname = os.path.dirname(__file__)
                    print("From Server: {}".format(in_data))
                    client.sendall("NAME")
                    name = client.recv(1024)
                    with open("{}/{}.png".format(dirname, name), 'ab') as img:
                        img.write(data)
                        img.close()
        print("Connection is over")
        client.close()
        sys.exit()


if __name__ == "__main__":
    main()
