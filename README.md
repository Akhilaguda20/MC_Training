# Basic CRUD API using Serverless Framework & AWS

Serverless CRUD application demonstrating infrastructure as code using the Serverless Framework with AWS services.

## Overview

This project implements a fully functional **User Management API** using Serverless Framework to automate deployment and management of:

- AWS Lambda functions (Python 3.9)
- API Gateway (REST API)
- DynamoDB table with on-demand billing
- IAM roles with least-privilege permissions

The API supports core CRUD operations:

- **Create** → POST /users  
- **Read** → GET /users/{id}  
- **Update** → PUT /users/{id}  
- **Delete** → DELETE /users/{id}  

---

## Architecture

Client → API Gateway → Lambda → DynamoDB

---

## DynamoDB Configuration

- **Table Name:** users  
- **Partition Key:** userId (String)  
- **Billing Mode:** Pay-per-request  

---

## IAM Roles & Permissions

IAM permissions are configured via `serverless.yml`.

### Function-specific IAM Roles 
Each Lambda gets only required permissions (least privilege).

| Function   | Permission          |
| ---------- | ------------------- |
| createUser | dynamodb:PutItem    |
| getUser    | dynamodb:GetItem    |
| updateUser | dynamodb:UpdateItem |
| deleteUser | dynamodb:DeleteItem |

---

## Key Learning

- Started with full access permissions
- Improved security by implementing **least privilege IAM roles**
- Learned how Serverless Framework simplifies deployment compared to manual setup

---

## Lambda Functions

### Create User
**POST /users**

- Generates UUID for each user
- Prevents duplicate records  

**Responses:**
- 201 → Created  
- 400 → Invalid input  
- 409 → Duplicate record  
- 500 → Server error  

---

### Get User
**GET /users/{id}**

- Fetches user details from DynamoDB  

---

### Update User
**PUT /users/{id}**

- Updates existing user data  

---

### Delete User
**DELETE /users/{id}**

- Deletes user record  

---

## Serverless Configuration

The `serverless.yml` file defines:

- Lambda functions
- API Gateway routes
- DynamoDB resource
- IAM role statements

---

## Deployment

### Install Serverless Framework
```bash
npm install -g serverless

- serverless deploy

## Testing

Tested using Postman

Verified:

CRUD operations working correctly

Proper status codes

Error handling

### Commands
- serverless deploy 
Deploys entire project to AWS
Creates/updates: Lambda functions, API Gateway, DynamoDB 
- serverless remove :Deletes everything created by  project
- serverless logs -f functionName : Shows logs of a specific Lambda function
- serverless invoke -f functionName : Runs your Lambda manually, useful for testing without API Gateway