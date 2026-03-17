# Lambda Functions - CRUD Operations

This directory contains AWS Lambda functions that implement CRUD (Create, Read, Update, Delete) operations for user management.

## Overview

These Lambda functions are part of the **AG_MCTRAINING-424** , which demonstrates a basic serverless CRUD API using AWS services.

## Architecture

### AWS Services Used
- **DynamoDB**: NoSQL database for storing user records
- **Lambda**: Serverless compute for executing CRUD operations
- **IAM**: Identity and Access Management for function permissions
- **API Gateway**: HTTP API for exposing Lambda functions

### Database Setup
- **Table Name**: `users`
- **Partition Key**: `userId` (string)

### IAM Configuration
- **Role**: `lambda-dynamodb-access-role`
- **Policy**: `AmazonDynamoDBFullAccess`

## Lambda Functions

### 1. createUser (POST /users)
Creates a new user record in the DynamoDB table.

**Features**:
- Auto-generates UUID to prevent duplicate insertions
- Validates email format and required fields
- Returns appropriate HTTP status codes

**Status Codes**:
- `201`: User created successfully
- `400`: Bad request (invalid email or missing fields)
- `409`: Conflict (duplicate user ID)
- `500`: Internal server error

### 2. getUser (GET /users/{id})
Retrieves a specific user's details from the table by user ID.

**Status Codes**:
- `200`: Success
- `404`: User not found
- `500`: Internal server error

### 3. updateUser (PUT /users/{id})
Updates an existing user record in the table.

**Status Codes**:
- `200`: User updated successfully
- `400`: Bad request (invalid data)
- `404`: User not found
- `500`: Internal server error

### 4. deleteUser (DELETE /users/{id})
Deletes a specific user record from the table.

**Status Codes**:
- `200`: User deleted successfully
- `404`: User not found
- `500`: Internal server error

## API Gateway

- **API Name**: `crud-users-api`
- **Type**: HTTP API
- **Routes**: All Lambda functions integrated with corresponding HTTP methods and paths

## Testing

All CRUD operations have been tested using **Postman** to verify:
- Correct HTTP status codes
- Proper data handling
- Error scenarios

## Directory Structure

```
lambdas/
├── createUser/
│   └── handler.py
├── getUser/
│   └── handler.py
├── updateUser/
│   └── handler.py
├── deleteUser/
│   └── handler.py
└── README.md
```

