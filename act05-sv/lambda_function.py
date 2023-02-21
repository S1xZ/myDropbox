import boto3
from boto3.dynamodb.conditions import Key
import json
import os
import base64
import io


def lambda_handler(event, context):
    
    # print(body)
    
    body = json.loads(event["body"])
    # Initialize the result
    result = "ok"

    # Call the appropriate function based on the method
    if event['path'] == "/default/activity05/get":
        result = download_from_s3(body["fileName"], body["username"])
        # If the method is not valid, return an error
        if (result == False):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})
            }

    elif event['path'] == "/default/activity05/put":
        result = upload_file(body["fileData"],body["fileName"],body["username"])
        # If the method is not valid, return an error
        if (result != "OK"):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})
            }
    elif event['path'] == "/default/activity05/view":
        result = list_s3_files_with_prefix(body["username"])
        # If the method is not valid, return an error
        if (result != "OK"):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})

            }
    elif event['path'] == "/default/activity05/register":
        result = register_user(body["username"],body["password"])
        # If the method is not valid, return an error
        if (result != "OK"):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})

            }
    elif event['path'] == "/default/activity05/login":
        result = login_from_dynamodb(body["username"],body["password"])
        # If the method is not valid, return an error
        if (result != "OK"):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})

            }
    elif event['path'] == "/default/activity05/share":
        result = share(body["fileName"],body["sender_username"],body["receiver_username"])
        # If the method is not valid, return an error
        if (result != "OK"):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": str(result)})

            }
            
    return {
        "statusCode": 200,
        "body": json.dumps({"result": str(result)})
    }


def list_s3_files_with_prefix(username):
    """List all files in an S3 bucket with the given prefix

    :param prefix: Prefix to filter files by
    :return: List of files with the given prefix

    """
    
    dynamodb = boto3.resource('dynamodb')
    
    # Store the username filename and source in a DynamoDB table
    table = dynamodb.Table('myDropboxShare')
    
    # Call S3 to list all objects in the bucket with the given prefix
    response = table.query(
    KeyConditionExpression=Key('username').eq(username)
    )
    
    if 'Items' not in response:
        return json.dumps([])
    
    items = response['Items']
    
    # Create an S3 client
    s3 = boto3.client("s3")
    
    file_list = []
    
    for k in items:
        source = k['from']
        file_name = k['filename']
        content = s3.head_object(Bucket = os.environ['BUCKET_NAME'], Key = source + "/" + file_name)
        file_size = content["ContentLength"]
        last_modified = content["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
        file_list.append(
            f"{file_name} {file_size} {last_modified} {source}")
    
    return json.dumps(file_list)


def upload_file(fileData, fileName, username):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param username: Username to upload to

    return: True if file was uploaded, else False
    """
    
    dynamodb = boto3.resource('dynamodb')
    
    # Store the username filename and source in a DynamoDB table
    table = dynamodb.Table('myDropboxShare')
    
    try:
        response = table.put_item(
        Item={
            'username': username,
            'filename': fileName,
            'from': username
        },
        ConditionExpression='attribute_not_exists(username)'
    )
    except Exception as e:
        return f"Something went wrong: {e}"
        
    # Create an S3 client
    s3 = boto3.client('s3')
    

    
    data = base64.b64decode(fileData + '====')
    # file = open(data, 'rb')

    try:
        # Upload the file
        s3.put_object(
             Body=data, Bucket=os.environ['BUCKET_NAME'], Key = username + "/" + fileName)

    except Exception as e:
        print(f"Something went wrong: {e}")
        return False

    return "OK"


def download_from_s3(file_name, username):
    """Download a file from an S3 bucket

    :param file_name: File to download to
    :param bucket: Bucket to download from
    :param s3_file_name: S3 file name. If not specified then file_name is used
    :return: True if file was downloaded, else False

    """
    
    
    dynamodb = boto3.resource('dynamodb')
    
    # Store the username filename and source in a DynamoDB table
    table = dynamodb.Table('myDropboxShare')
    
    try:
        response = table.get_item(
        Key={
            'username': username,
            'filename': file_name,
        },
    )
    except Exception as e:
        return f"Something went wrong: {e}"
    
    source = response['Item']['from']
    
    # Create an S3 client
    s3 = boto3.client("s3")
    
    
    try:
        # Download the file
        obj = s3.get_object(Bucket = os.environ['BUCKET_NAME'], Key = source + "/" + file_name)
        file = obj["Body"].read()
        encoded_string = base64.b64encode(file).decode("utf-8")
        
    except Exception as e:
        print(f"Something went wrong: {e}")
        return False

    return encoded_string

def register_user(username, password):
    
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('myDropboxUsers')
    
    try:
        response = table.put_item(
        Item={
            'username': username,
            'password': password
        },
        ConditionExpression='attribute_not_exists(username)'
    )
    except Exception as e:
        return f"Failed to register user {username}. User already exists."
    
    # Check if the operation was successful
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return "OK"
        

def login_from_dynamodb(username, password):
    """
    This function checks if the provided username and password match an existing user in a DynamoDB table.
    
    :param username: a string representing the username of the user attempting to log in.
    :param password: a string representing the password of the user attempting to log in.
    :return: returns True if the username and password match an existing user, otherwise returns an error message as a string.
    """
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('myDropboxUsers')
    
    try:
        response = table.get_item(Key={'username': username})
    except Exception as e:
        return e.response['Error']['Message']
    
    if 'Item' not in response:
        return "Username not found"
    
    user = response['Item']
    
    if password != user['password']:
        return "Incorrect password"
    
    return "OK"
    
def share(file_name, sender_username, receiver_username):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('myDropboxUsers')
    
    try:
        response = table.get_item(Key={'username': receiver_username})
    except Exception as e:
        return f"Something went wrong: {e}"
    
    if 'Item' not in response:
        return "Username not found"
        
    table = dynamodb.Table('myDropboxShare')
    
    try:
        response = table.get_item(Key={
            'username': sender_username,
            'filename': file_name
        })
    except Exception as e:
        return f"Something went wrong: {e}"
    
    if 'Item' not in response:
        return "File not found"
    
    try:
        response = table.put_item(
        Item={
            'username': receiver_username,
            'filename': file_name,
            'from' : sender_username
        },
    )
    except Exception as e:
        return f"Something went wrong: {e}"
    
    return "OK"