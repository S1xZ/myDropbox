# Main CLI program
import base64
import requests
import json
import os
import os.path
from dotenv import load_dotenv
load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT")
GET_URL = API_ENDPOINT + "/get"
VIEW_URL = API_ENDPOINT + "/view"
PUT_URL = API_ENDPOINT + "/put"
REGISTER_URL = API_ENDPOINT + "/register"
LOGIN_URL = API_ENDPOINT + "/login"
SHARE_URL = API_ENDPOINT + "/share"

def main():
    # Dummy code to provide a sample of the expected output
    print("""== == == == == == == == == == == == == == == == == == == == == == == == == == ==
    Please input command(newuser username password password, login
                        username password, put filename, get filename, view, or logout).
    If you want to quit the program just type quit.
    == == == == == == == == == == == == == == == == == == == == == == == == == == ==""")
    
    # User login status
    isLogin = False
    username = ""
    isAlive = True
    
    # Login loop
    while (isAlive):
        command = input(">>")
        if(len(command.strip()) == 0):
            continue
        cmd_list = command.strip().split()
        if(not isLogin):
            if cmd_list[0] == "quit":
                break
            elif cmd_list[0] == "newuser":
                if(len(cmd_list) != 4):
                    print("ERROR: Invalid command")
                elif(cmd_list[2] != cmd_list[3]):
                    print("ERROR: Passwords do not match")
                else:
                    # TODO Handle create user
                    register(cmd_list[1], cmd_list[2])
            elif cmd_list[0] == "login":
                if(len(cmd_list) != 3):
                    print("ERROR: Invalid command")
                else:
                    isLogin = login(cmd_list[1], cmd_list[2])
                    if(isLogin):
                        username = cmd_list[1]
            else:
                print("Please login first")
        else:
            # Command loop
            if cmd_list[0] == "quit":
                break
            elif cmd_list[0] == "view":
                view(username)
            elif cmd_list[0] == "put":
                if len(cmd_list) != 2:
                    print("ERROR: Invalid command")
                else:
                    fileName = cmd_list[1].strip()
                    put(fileName, username)
            elif cmd_list[0] == "get":
                if len(cmd_list) != 3:
                    print("ERROR: Invalid command")
                else:
                    fileName = cmd_list[1].strip()
                    get(fileName, cmd_list[2])
            elif cmd_list[0] == "share":
                if len(cmd_list) != 3:
                    print("ERROR: Invalid command")
                else:
                    fileName = cmd_list[1].strip()
                    share(fileName, username, cmd_list[2])
            elif cmd_list[0] == "logout":
                isLogin = False
                username = ""
                print("OK")
            else:
                print("ERROR: Invalid command")
    print("== == == == == == == == == == == == Bye! == == == == == == == == == == == == ==")

def view(username):
    """View files on server

    param: username: username of user

    return: None
    """

    # Handle sent request
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "username": username
        }
    )

    # Handle response
    response = requests.get(VIEW_URL, data=raw_data, headers=headers)
    body = json.loads(response.text)

    # Handle CLI
    result = body["result"].strip("[]").split(",")
    print("OK")
    if(result[0] == ""):
        print("No files found")
        return
    for i in result:
        print(i.strip())

#===============================================================================

def put(fileName, username):
    """Put file on server
    
    param: fileName: name of file to put
    param: username: username of user
    
    return: None
    """

    # Handle sent request
    fileExists = os.path.exists(fileName)

    if not fileExists:
        print("ERROR: File does not exist")
        return

    with open(fileName, "rb") as file:
        data = file.read()
        encoded_string = base64.b64encode(data).decode("utf-8")
    
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "fileData": encoded_string,
        "fileName": fileName,
        "username": username
        }
    )

    # Handle response
    response = requests.post(PUT_URL, data=raw_data, headers=headers)

    # Handle CLI
    print("OK")

#===============================================================================

def get(fileName, username):
    """Get file from server
    
    param: fileName: name of file to get
    param: username: username of user

    return: None
    """

    # Handle sent request
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "fileName": fileName,
        "username": username
        }
    )

    # Handle response
    response = requests.get(GET_URL, data=raw_data, headers=headers)
    body = json.loads(response.text)
    # Catch error

    if(response.status_code != 200):
        print(body["result"])
        return    

    with open(fileName, "wb") as file:
        file.write(base64.b64decode(body["result"]))

    # Handle CLI
    print("OK")

def register(username,password):
    """Create new user

    param: username: username of user
    param: password: password of user

    return: None
    """

    # Handle sent request
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "username": username,
        "password": password
        }
    )

    # Handle response
    
    response = requests.post(REGISTER_URL, data=raw_data, headers=headers)
    body = json.loads(response.text)

    # Handle CLI
    if(body["result"] == "OK"):
        print("OK")
        return True
    else:
        print(body["result"])
        return False

def login(username,password):
    """Login to server

    param: username: username of user
    param: password: password of user

    return: None
    """

    # Handle sent request
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "username": username,
        "password": password
        }
    )

    # Handle response
    response = requests.get(LOGIN_URL, data=raw_data, headers=headers)
    body = json.loads(response.text)

    # Handle CLI
    if(body["result"] == "OK"):
        print("OK")
        return True
    else:
        print(body["result"])
        return False

def share(fileName , sender_username, receiver_username):
    """Share file with another user

    param: fileName: name of file to share
    param: username: username of user

    return: None
    """

    # Handle sent request
    headers = {"content-type": "text/plain"}
    raw_data = json.dumps(
        {
        "fileName": fileName,
        "sender_username": sender_username,
        "receiver_username": receiver_username
        }
    )

    # Handle response
    response = requests.post(SHARE_URL, data=raw_data, headers=headers)
    body = json.loads(response.text)
    
    # Handle CLI
    if(body["result"] == "OK"):
        print("OK")
    else:
        print(body["result"])

#===============================================================================

if __name__ == "__main__":
    main()