import datetime
import hashlib
import os
import pickle
import socket
import subprocess
import sys
import threading

try:
    from PIL import ImageGrab
except ImportError:
    sys.exit("""You need Pillow! install it by runnig pip install
				Pillow in the directory where pip.exe is""")

# creates a mutex for the server for the users file
mutex = threading.Lock()

# global vars
HOSTIP = None
PORT = 8083

"""
md5Encryption:

Encrypts the string to a md5 format string

args: string
"""


def md5Encryption(string):
    try:
        m = hashlib.md5()
        m.update(string)
        return m.hexdigest()
    except:
        print ("Error in 'md5Encryption'")


"""
checkIfRegistered:

Checks if a username is already in the file of users

args: username
"""


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
        print ("Error in 'checkIfRegistered'")
    finally:
        mutex.release()


"""
login:

checks if the username and password given are mathcing
a username and password in the file of users

args: username and password
"""


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
        print("Error in 'login'")
        return False
    finally:
        mutex.release()


"""
connect:

the user action to connect, it gets the username and
password from the client and calls the login method

args: username and password

returns a tuple with a boolean that repesents if the
	login worked and a message for the client to see
"""


def connect(client, args=None):
    try:
        argsArray = args.split(",")
        username = argsArray[0]
        password = argsArray[1]
        if login(username, password):
            client.name = username
            return pickle.dumps((True, "You are now logged in...\nto see all the avilable action enter 'SHOW_ACTIONS'\nTo activate an action, wirte ACTION_ACTION;arg,arg"))
        else:
            return pickle.dumps((False, "username and/or password are incorrect"))
    except:
        print("Error in 'connect'")


"""
register:

the user action to register, it gets the username and
password from the client, checks if there isnt a
username already, writes the new user in the users
file and calls the login method

args: username and password

returns a tuple with a boolean that repesents if the
	login worked and a message for the client to see
"""


def register(client, args=None):
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
            print("Error in 'register'")
            return pickle.dumps((False, "error creating user"))
        finally:
            mutex.release()
        if login(username, password):
            client.name = username
            return pickle.dumps((True, "You are now logged in...\nto see all the avilable action enter 'SHOW_ACTIONS'\nTo activate an action, wirte ACTION_ACTION;arg,arg"))
        else:
            return pickle.dumps((False, "error creating user"))


"""
time:

the user action to get the current time

args: None
"""


def time(client, args=None):
    try:
        tm = datetime.datetime.now()
        return "The current time is {}".format(tm)
    except:
        print("Error in 'time'")


"""
name:

the user action to get the user name

args: None
"""


def name(client, args=None):
    try:
        return client.name
    except:
        print("Error in 'name'")


"""
exitFromServer:

the user action to exsit from the client and
disconnect the connection

args: None
"""


def exitFromServer(client, args=None):
    try:
        client.csocket.send("Bye Bye")
        client.csocket.shutdown(0)
        client.csocket.close()
        return "Bye Bye"
    except:
        print("Error in 'exitFromServer'")


"""
printScreen:

the user action to activate a print screen of
the server and get the image that was saved

args: None
"""


def printScreen(client, args=None):
    try:
        # prints the screen
        im = ImageGrab.grab()
        # saves the image
        im.save("{}.png".format(client.name))
        with open("{}.png".format(client.name), "rb") as image:
                        # saves the image by reading the bytes of it and
                        # sending them to the client
            byte = image.read(16384)
            while len(byte) >= 16384:
                client.csocket.send(byte)
                byte = image.read(16384)
            # sends the rest of the bytes left
            if len(byte) > 0:
                client.csocket.send(byte)
            im.close()
            image.close()
			# removes the image saved at the server folder
            os.remove("{}.png".format(client.name))
            return "PRINT_IMAGE"
    except:
        return "Image not saved"


"""
activateProgram:

the user action to activate a program at the server
(postman,word,etc..) by receiving the full path
of the file to activate

args: full path of a file
"""


def activateProgram(client, args=None):
    try:
		# activates a program
        subprocess.call([args])
        return "program activated"
    except:
        return "failed to activate program"


"""
showFolder:

the user action to show the contents of a folder

args: full path of a file
"""


def showFolder(client, args=None):
    try:
        path = "."
        if args != None:
            path = args
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                root
                # shows the root that was given and then all
                # the files and dirs that it containes
                return root + " =>\n" + ", ".join(dirs+files)
        else:
            return "the given path is not directory"
    except:
        print("Error in 'showFolder'")


"""
showActions:

the user action to get all the possible actions of the server

args: None
"""


def showActions(client, args=None):
    try:
        lst = list(serverActions.keys())
        str1 = "\n"
		# shows all the actions except "connect" and "register"
        return str1.join(filter(lambda lstItem: lstItem != "CONNECT" and lstItem != "REGISTER", lst))
    except:
        print("Error in 'showActions'")


"""
A dictonary with all the server ui actions-
key:name of action, value: reference to the action method
"""
serverActions = {"CONNECT": connect, "REGISTER": register, "TIME": time,
                 "NAME": name, "EXIT": exitFromServer,
                 "PRINT_SCREEN": printScreen, "ACTIVATE_PROGRAM": activateProgram,
                 "SHOW_FOLDER": showFolder, "SHOW_ACTIONS": showActions}


"""
keep_connection_alive:

The keep alive method that sends on a different thread
a message every 5 seconds that the server is still alive
"""


def keep_connection_alive((clientsock)):
    isAlive = True
    try:
        # sends the message
        clientsock.send("Connection with client is alive")
    except:
		# clientsock.shutdown(0)
		# clientsock.close()
        print("Disconnected, connection with client is not alive'")
        isAlive = False
    if isAlive:
        # the timer that calls itself at the .Timer() callback parameter
        threading.Timer(5, keep_connection_alive,
                        (clientsock,)).start()


"""
connectionThread:

The keep_connection_alive thread method that connects to
the client and calls the keep_connection_alive method
"""


def connectionThread():
    try:
        # connects to the client
        global HOSTIP
        global PORT
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOSTIP, PORT+1))
        server.listen(1)
        clientsock, clientAddress = server.accept()
        print("\nNew keep_alive_trhead started: {}".format(clientAddress))
        # calls the keep_connection_alive method
        keep_connection_alive((clientsock))
    except:
        print("Error in 'connectionThread'")


"""
The Client thread class that represnts a connection to a client
"""
class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        self.name = ""
        # activates the keep_connection_alive thread
        threading._start_new_thread(connectionThread, ())
        print("New connection added: {}".format(clientAddress))
        self.csocket.send("\nEnter 'Connect/Register;UserName,Password'")

    def run(self):
        try:
            while True:
                data = self.csocket.recv(2048)
                # splits the received data by a ;
                # the first part is the name of the action
                # the second part is the args of the action
                dataArray = data.split(";")
                if len(dataArray) > 0:
                    action = dataArray[0].upper()
                    global serverActions
                    # checks if the action string from the client exists
                    if action in serverActions:
                        # if there are args, calls the action with the args
                        if len(dataArray) > 1:
                            args = dataArray[1]
                            # calls the action by getting its mehod
                            # reference from the dictonary
                            result = serverActions[action](self, args)
                        # else, calls the action without args
                        else:
                            # calls the action by getting its mehod
                            # reference from the dictonary
                            result = serverActions[action](self)
                        # if the result from the action is "bye bye", then
                        # it means that the connection is closed so it
                        # the instance of itself, otherwise, it send the
                        # result to the client
                        if result.lower() != "bye bye":
                            self.csocket.send(result)
                        else:
                            del self
                            return
                    else:
                        self.csocket.send("no such action")
                else:
                    self.csocket.send("no action given")
        except:
            self.csocket.shutdown(0)
            self.csocket.close()
            print ("Client at {} disconnected due to an error...".format(
                self.clientAddress))


"""
main:

The main method of the program, when the server starts,
this method get called
"""
def main():
    try:
        global HOSTIP
        global PORT
        # activates the server
        HOSTIP = socket.gethostbyname(socket.gethostname())
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", PORT))
        print("\n\nServer at {} started".format(HOSTIP))
        print("Waiting for client request..")
        while True:
            # getting client connection requests and start
            # a new thread for each client
            server.listen(1)
            clientsock, clientAddress = server.accept()
            newthread = ClientThread(clientAddress, clientsock)
            newthread.start()
    except:
        print("Error in 'main'")


if __name__ == "__main__":
    main()
