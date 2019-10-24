import hashlib
import os
import pickle
import socket
import threading

# TODO: add show all available actions
# TODO: add try catch to all actions
# TODO: add comments

mutex = threading.Lock()

def md5Encryption(string):
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()

def checkIfRegistered(username):
    dirname = os.path.dirname(__file__)
    try:
        mutex.acquire()
        for line in open("{}/accountfile.txt".format(dirname), "r").readlines():  # Read the lines
            # Split on the space, and store the results in a list of two strings
            login_info = line.split()
            if username == login_info[0]:
                return True
        return False
    except:
            print ("Error")
    finally:
        mutex.release()

def login(username, password):
    dirname = os.path.dirname(__file__)
    incPassword = md5Encryption(password)
    try:
        mutex.acquire()
        for line in open("{}/accountfile.txt".format(dirname), "r").readlines():  # Read the lines
            # Split on the space, and store the results in a list of two strings
            login_info = line.split()
            if username == login_info[0] and incPassword == login_info[1]:
                return True
        return False
    except:
            print ("Error")
    finally:
        mutex.release()
    


def connect(args=None):
    argsArray = args.split(",")
    username = argsArray[0]
    password = argsArray[1]
    if login(username, password):
        return pickle.dumps((True, "You are now logged in..."))
    else:
        return pickle.dumps((False, "username and/or password are incorrect"))


def register(args=None):
    dirname = os.path.dirname(__file__)
    argsArray = args.split(",")
    username = argsArray[0]
    password = argsArray[1]
    incPassword = md5Encryption(argsArray[1])
    if checkIfRegistered(username):
        return pickle.dumps((False, "There is already a user with that name"))
    else:
        try:
            mutex.acquire()
            file = open("{}/accountfile.txt".format(dirname), "a")
            file.write(username)
            file.write(" ")
            file.write(incPassword)
            file.write("\n")
            file.close()
        except:
            print ("Error")
        finally:
            mutex.release()
        if login(username, password):
            return pickle.dumps((True, "You are now logged in..."))
        else:
            return pickle.dumps((False, "error creating user"))


def time(args=None):
    return "TIME"


def name(args=None):
    return "NAME"


def exitFromServer(args=None):
    return "EXIT"


def printScreen(args=None):
    return "PRINT_SCREEN"


def activateProgram(args=None):
    return "ACTIVATE_PROGRAM"


def showFolder(args=None):
    return "SHOW_FOLDER"

def showActions(args=None):
    lst = list(serverActions.keys())
    str1 = "\n"
    return str1.join(filter(lambda lstItem: lstItem!="CONNECT" and lstItem!="REGISTER",lst))

serverActions = {"CONNECT": connect, "REGISTER": register, "TIME": time, 
                 "NAME": name, "EXIT": exitFromServer, 
                 "PRINT_SCREEN": printScreen,"ACTIVATE_PROGRAM": activateProgram, 
                 "SHOW_FOLDER": showFolder, "SHOW_ACTIONS":showActions}


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        print("New connection added: ", clientAddress)
        self.csocket.send("\n\nEnter 'Connect/Register;UserName,Password'")

    def run(self):
        # try:
        while True:
            data = self.csocket.recv(2048)
            dataArray = data.split(";")
            if len(dataArray) > 0:
                action = dataArray[0].upper()
                global serverActions
                if action in serverActions:
                    # might not need this check
                    if len(dataArray) > 1:
                        args = dataArray[1]
                        result = serverActions[action](args)
                    else:
                        result = serverActions[action]()
                    self.csocket.send(result)
                else:
                    self.csocket.send("no such action")
            else:
                self.csocket.send("no action given")
        # except:
        #     print ("Client at {} disconnected due to an error...".format(
        #         self.clientAddress))


def main():
    LOCALHOST = "127.0.0.1"
    PORT = 8083
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, PORT))
    print("\n\nServer started")
    print("Waiting for client request..")
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()


if __name__ == "__main__":
    main()
