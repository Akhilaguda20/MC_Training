# Basic CRUD API using AWS SAM & CloudFormation

Serverless CRUD application demonstrating infrastructure as code principles using AWS SAM (Serverless Application Model) and CloudFormation.

##  Overview

This project implements a fully functional User Management API that automates the creation and deployment of:

-  AWS Lambda functions (Python 3.9)
-  API Gateway endpoints (REST API)
-  DynamoDB table with on-demand billing
-  IAM roles with least-privilege permissions

The API performs essential CRUD operations:
- **Create** → POST /users
- **Read** → GET /users/{id}
- **Update** → PUT /users/{id}
- **Delete** → DELETE /users/{id}

##  Architecture

Client → API Gateway → Lambda → DynamoDB

## DynamoDB congiguration
- **Table Name:** users
- **Partition Key:** userId (String)
- **Billing Mode:** Pay-per-request

## IAM Roles & Permissions
- IAM roles defined within SAM template
- Each Lambda function is assigned specific permissions

| Function   | Permission          |
| ---------- | ------------------- |
| createUser | dynamodb:PutItem    |
| getUser    | dynamodb:GetItem    |
| updateUser | dynamodb:UpdateItem |
| deleteUser | dynamodb:DeleteItem |


## Key Learning:
Initially explored full access approach, then implemented least privilege principle by assigning only required actions per Lambda.

## Lambda Functions
**Create User** POST /users
- Generates UUID for unique users
- Prevents duplicate records
**Responses:**
201 → Created

400 → Invalid input

409 → Duplicate record

500 → Server error

**Get User**

GET /users/{id}

Fetches user details from DynamoDB

**Update User**

PUT /users/{id}

Updates existing user data

**Delete User**

DELETE /users/{id}

Deletes user record

SAM Template

The template.yaml defines:

## Lambda functions

**API Gateway routes**

**DynamoDB table**

**IAM roles and policies**

## Deployment
- Build : sam build
- Deploy : sam deploy --guided
- Provide Inputs : Stack name, Region, Allow IAM Role creation, Confirm deployment

## Testing 
- Tested using Postman

Verified:

CRUD functionality

Status codes

Error handling