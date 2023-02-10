# myDropbox
A simple file sharing application with authentication

### Getting Started
These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites
Python 3.7+

### Installation

In the cli application run the following command
```bash
pip install -r requirements.txt -t .
```

### Deployment
Create a lambda function and set up 4 gateway for the method
1 as the main route for the fucntion and 3
for the route /view, /get, /put zip and upload the server code.

### Built With
AWS Lambda
AWS S3
AWS DynamoDB
Python
