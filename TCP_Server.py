import hashlib
import os
import pickle
import socket
import threading
import datetime
from PIL import ImageGrab

# TODO: add show all available actions
# TODO: add try catch to all actions
# TODO: add comments
# TODO: from PIL import ImageGrab

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
    encPassword = md5Encryption(password)
    try:
        mutex.acquire()
        for line in open("{}/accountfile.txt".format(dirname), "r").readlines():  # Read the lines
            # Split on the space, and store the results in a list of two strings
            login_info = line.split()
            if username == login_info[0] and encPassword == login_info[1]:
                return True
        return False
    except:
            print ("Error")
    finally:
        mutex.release()
    

def connect(client,args=None):
    argsArray = args.split(",")
    username = argsArray[0]
    password = argsArray[1]
    if login(username, password):
        client.name = username
        return pickle.dumps((True, "You are now logged in..."))
    else:
        return pickle.dumps((False, "username and/or password are incorrect"))


def register(client,args=None):
    dirname = os.path.dirname(__file__)
    argsArray = args.split(",")
    username = argsArray[0]
    password = argsArray[1]
    encPassword = md5Encryption(argsArray[1])
    if checkIfRegistered(username):
        return pickle.dumps((False, "There is already a user with that name"))
    else:
        try:
            mutex.acquire()
            file = open("{}/accountfile.txt".format(dirname), "a")
            file.write(username)
            file.write(" ")
            file.write(encPassword)
            file.write("\n")
            file.close()
        except:
            print ("Error")
        finally:
            mutex.release()
        if login(username, password):
            client.name = username
            return pickle.dumps((True, "You are now logged in..."))
        else:
            return pickle.dumps((False, "error creating user"))


def time(client,args=None):
    tm = datetime.datetime.now()
    return "The current time is {}".format(tm)


def name(client,args=None):
    return "Your name: {}".format(client.name)


def exitFromServer(client,args=None):
    client.csocket.send("Bye Bye")
    client.csocket.shutdown(0)
    client.csocket.close()
    return "Bye Bye"


def printScreen(client,args=None):
    im = ImageGrab.grab()
    im.save("{}.png".format(client.name))
    with open("{}.png".format(client.name), "rb") as image:
        f = image.read()
        b = bytearray(f)
        im.close()
        image.close()
        os.remove("{}.png".format(client.name))
        
        return b


def activateProgram(client,args=None):
    return "ACTIVATE_PROGRAM"


def showFolder(client,args=None):
    return "SHOW_FOLDER"

def showActions(client,args=None):
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
        self.name=""
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
                        result = serverActions[action](self,args)
                    else:
                        result = serverActions[action](self)
                    if result.lower() != "bye bye":
                        self.csocket.send(result)
                    else:
                        del self
                        return
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
