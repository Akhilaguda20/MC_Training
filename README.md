#  User Events Service (Serverless + AWS)

This project demonstrates an **event-driven serverless architecture** using AWS services and the Serverless Framework.

---

##  Overview

This application implements a **User Update Flow** using:

* AWS Lambda (Python 3.9)
* API Gateway (HTTP API)
* Amazon EventBridge (Custom Event Bus)
* Amazon SQS (Queue)
* Amazon DynamoDB
* IAM Roles & Policies

---

##  Architecture

```
HTTP API (PUT /user/{id})
        ↓
updateUser Lambda (Producer)
        ↓ (PutEvents)
EventBridge (Custom Bus: user-events-bus)
        ↓ (Rule filters event)
SQS Queue (UserEventsQueue)
        ↓
processUserUpdate Lambda (Consumer)
        ↓
DynamoDB (users_events table)
```

---



##  Project Structure

```
.
├── common/
│   ├── db.py
│   ├── response.py
│
├── update_user/
│   └── handler.py
│
├── process_user/
│   └── handler.py
│
├── serverless.yml
└── README.md
```

---



##  Environment Variables

| Variable       | Description                 |
| -------------- | --------------------------- |
| TABLE_NAME     | DynamoDB table name         |
| QUEUE_URL      | SQS queue URL               |
| EVENT_BUS_NAME | Custom EventBridge bus name |

---

##  How It Works

### 1. API Request

* User sends `PUT /user/{id}` request.

### 2. Event Publishing

* `updateUser` Lambda publishes event to EventBridge:

```json
{
  "source": "user.service",
  "detail-type": "UserUpdated",
  "detail": {
    "userId": "123"
  }
}
```

### 3. Event Routing

* EventBridge rule filters:

  * `source = user.service`
  * `detail-type = UserUpdated`
* Sends event to SQS queue.

### 4. Event Processing

* `processUserUpdate` Lambda consumes SQS messages.
* Updates DynamoDB record.

---

##  AWS Resources Created

* **Lambda Functions**

  * updateUser
  * processUserUpdate

* **EventBridge**

  * Custom Event Bus: user-events-bus
  * Rule: UserUpdatedEventRule

* **SQS**

  * Queue: UserEventsQueue

* **DynamoDB**

  * Table: users_events

---

##  IAM Permissions

* dynamodb:UpdateItem → Update user records
* events:PutEvents → Send events to EventBridge

---
