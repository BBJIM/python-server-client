import socket
import pickle
import sys

# TODO: add try catch 

def main():
    SERVER = "127.0.0.1"
    PORT = 8083
    isConnected = False
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        isConnected = True
    except:
        print("\nCould not connect the server\n")
    if isConnected:
        isLoggedIn = False
        in_data = client.recv(1024)
        print("From Server: {}".format(in_data))
        while not isLoggedIn:
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            if check_command=="register" or check_command=="connect":
                client.sendall(out_data)
                in_data = client.recv(1024)
                loginTupleResponse = pickle.loads(in_data)
                print("From Server: {}".format(loginTupleResponse[1]))
                if loginTupleResponse[0]:
                    isLoggedIn = True
                    break
            else:
                print("From Client: You can only enter the register or connect command at this time")

        print("Enter the command you want to activate")

        while isLoggedIn:
            out_data = raw_input(">>>")
            check_command = out_data.split(";")[0].lower()
            if check_command=="register" or check_command=="connect":
                print("From Client: You are already logged in")
            else:
                client.sendall(out_data)
                in_data = client.recv(1024)
                print("From Server: {}".format(in_data))
                if in_data.lower()=="bye bye":
                    sys.exit()


if __name__ == "__main__":
    main()
