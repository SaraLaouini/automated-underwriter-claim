# Insurance Claim Processing Chatbot

## Overview

This project is a web-based chatbot designed to automate insurance claim processing using AWS services. The chatbot interacts with users to gather claim details, processes the claims using AWS Lambda and language models, and stores results in DynamoDB.

## Tools and Technologies

### AWS Services

- **AWS Lambda**: Serverless compute service used to execute backend code in response to events. Handles processing and validation of claims, invoking language models, and storing results in DynamoDB.
  
- **AWS Bedrock**: Provides access to various language models. Used for intelligent data processing and decision-making related to insurance claims.
  
- **Amazon DynamoDB**: NoSQL database service used to store insurance claim data and rules. Ensures fast and scalable data access.

- **Amazon S3**: Object storage service used to store the PDF file containing auto claim acceptance rules. Facilitates easy retrieval and processing of documents.

### Frontend Technologies

- **HTML**: Provides the structure of the chatbot interface. The `index.html` file sets up the chat layout, input fields, and message areas.

- **CSS**: Styles the chatbot interface. The `style.css` file ensures a user-friendly and visually appealing design.

- **JavaScript**: Manages client-side interactions. The `script.js` file handles user input, communication with AWS Lambda, and displays responses.

### Python

- **`lambda_function.py`**: Contains the main Lambda function handler. Processes incoming requests, validates claims, invokes language models, and stores results in DynamoDB.

- **`main.py`**: Provides utility functions for:
  - Extracting text from PDF files.
  - Invoking language models via AWS Bedrock.
  - Handling DynamoDB operations.
  - Reading files from S3.

## Project Components

### AWS Lambda Functions

- **`lambda_function.py`**: The core Lambda function that processes claims by interacting with language models and DynamoDB. It handles incoming requests and returns responses based on the processed data.

- **`main.py`**: Contains helper functions for:
  - Extracting and reading text from PDF files stored in S3.
  - Invoking language models from AWS Bedrock.
  - Performing operations with DynamoDB.

### Frontend

- **`index.html`**: Provides the structure of the chatbot interface, where users can interact with the system.

- **`style.css`**: Contains styling for the chatbot interface, ensuring a user-friendly and visually appealing design.

- **`script.js`**: Manages user interactions with the chatbot, including sending claim details to AWS Lambda and displaying responses.

## Getting Started

### Prerequisites

- AWS account with permissions for Lambda, S3, DynamoDB, and Bedrock.
- Basic knowledge of AWS services and web development.

### Setup

1. **Deploy AWS Lambda Functions:**
   - Deploy `lambda_function.py` and `main.py` to AWS Lambda.
   - Configure environment variables for the Lambda function (e.g., service names, model IDs, table names).

2. **S3 Bucket:**
   - Create an S3 bucket and upload the PDF file with auto claim acceptance rules.

3. **DynamoDB Table:**
   - Set up a DynamoDB table to store insurance claim data and rules.

4. **Frontend Deployment:**
   - Deploy the HTML, CSS, and JavaScript files to a web server.

### Usage

1. Open `index.html` in a web browser.
2. Enter a question or claim request.
3. The chatbot will prompt you to enter claim details if needed.
4. Submit the claim details.
5. The Lambda function processes the claim and returns a response.
6. The chatbot displays the result of the claim processing.

## Code Explanation

### `index.html`

Sets up the basic structure for the chatbot interface, including input fields and message display areas.

### `style.css`

Defines the visual design of the chatbot, including layout, colors, and typography.

### `script.js`

Handles:
- User input and message submission.
- Communication with the AWS Lambda function.
- Displaying responses from the Lambda function.

### AWS Lambda Functions

- **`lambda_function.py`**: Processes claims by calling language models and storing results in DynamoDB.
- **`main.py`**: Supports various utility functions, including reading PDF content and invoking language models.

