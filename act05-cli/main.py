# import fastapi

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

def main():
    # Dummy code to provide a sample of the expected output
    print("""== == == == == == == == == == == == == == == == == == == == == == == == == == ==
    Please input command(newuser username password password, login
                        username password, put filename, get filename, view, or logout).
    If you want to quit the program just type quit.
    == == == == == == == == == == == == == == == == == == == == == == == == == == ==""")
    login = False
    username = ""
    while (1):
        command = input(">>")
        if(len(command.strip()) == 0):
            continue
        cmd_list = command.strip().split()
        if cmd_list[0] == "quit":
            break
        elif cmd_list[0] == "newuser":
            if(len(cmd_list) != 4):
                print("ERROR: Invalid command")
            elif(cmd_list[2] != cmd_list[3]):
                print("ERROR: Passwords do not match")
            else:
                # TODO Handle create user

                print("OK")
        elif cmd_list[0] == "login":
            if(len(cmd_list) != 3):
                print("ERROR: Invalid command")
            else:
                # TODO Handle login and authentication

                username = cmd_list[1]
                login = True
                print("OK")
                break
        else:
            print("Please login first")

    if(login):
        while (1):
            command = input(">>")
            if(len(command.strip()) == 0):
                continue
            cmd_list = command.strip().split()
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
                if len(cmd_list) != 2:
                    print("ERROR: Invalid command")
                else:
                    fileName = cmd_list[1].strip()
                    get(fileName, username)
            else:
                print("ERROR: Invalid command")
    print("== == == == == == == == == == == == Bye! == == == == == == == == == == == == ==")

def view(username):

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
    if(body["result"] == "Unable to get file data"):
        print(body["result"])
        return

    with open(fileName, "wb") as file:
        file.write(base64.b64decode(body["result"]))

    # Handle CLI
    print("OK")


#===============================================================================

if __name__ == "__main__":
    main()