import boto3
import json
import os
import base64
import io



def lambda_handler(event, context):
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
                "body": json.dumps({"result": "Unable to get file data"})
            }

    elif event['path'] == "/default/activity05/put":
        result = upload_file(body["fileData"],body["fileName"],body["username"])
        # If the method is not valid, return an error
        if (result == False):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": "Unable to Upload file"})
            }
    elif event['path'] == "/default/activity05/view":
        result = list_s3_files_with_prefix(body["username"])
        # If the method is not valid, return an error
        if (result == False):
            return {
                "statusCode": 400,
                "body": json.dumps({"result": "Unable to view file data"})

            }

    return {
        "statusCode": 200,
        "body": json.dumps({"result": str(result)})
    }


def list_s3_files_with_prefix(prefix):
    """List all files in an S3 bucket with the given prefix

    :param prefix: Prefix to filter files by
    :return: List of files with the given prefix

    """

    # Create an S3 client
    s3 = boto3.client("s3")

    # Call S3 to list all objects in the bucket with the given prefix
    result = s3.list_objects_v2(
    Bucket=os.environ['BUCKET_NAME'], Prefix=f"{prefix}/")

    # Extract the contents of the response
    contents = result.get("Contents", [])
    file_list = []
    for content in contents:
        file_name = content["Key"].replace(prefix+"/", "", 1)
        file_size = content["Size"]
        last_modified = content["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
        file_list.append(
            f"{file_name} {file_size} {last_modified}")

    return json.dumps(file_list)


def upload_file(fileData, fileName, username):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param username: Username to upload to

    return: True if file was uploaded, else False
    """

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

    return True


def download_from_s3(file_name, username):
    """Download a file from an S3 bucket

    :param file_name: File to download to
    :param bucket: Bucket to download from
    :param s3_file_name: S3 file name. If not specified then file_name is used
    :return: True if file was downloaded, else False

    """

    # Create an S3 client
    s3 = boto3.client("s3")
    
    
    try:
        # Download the file
        obj = s3.get_object(Bucket = os.environ['BUCKET_NAME'], Key = username + "/" + file_name)
        file = obj["Body"].read()
        encoded_string = base64.b64encode(file).decode("utf-8")
        
    except Exception as e:
        print(f"Something went wrong: {e}")
        return False

    return encoded_string
