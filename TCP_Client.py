import socket
import pickle


def main():
    SERVER = "127.0.0.1"
    PORT = 8083
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER, PORT))
    isLoggedIn = False

    in_data = client.recv(1024)
    print("From Server: {}".format(in_data))
    while not isLoggedIn:
        out_data = raw_input(">>>")
        client.sendall(out_data)
        in_data = client.recv(1024)
        loginTupleResponse = pickle.loads(in_data)
        print("From Server: {}".format(loginTupleResponse[1]))
        if loginTupleResponse[0]:
            isLoggedIn = True
            break

    print("Enter the command you want to activate")

    while isLoggedIn:
        out_data = raw_input(">>>")
        client.sendall(out_data)
        in_data = client.recv(1024)
        print("From Server: {}".format(in_data))


if __name__ == "__main__":
    main()
