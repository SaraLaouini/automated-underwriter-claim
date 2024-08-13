# automated_underwriter_claim

## Description

This repository presents a project that aims to streamline the underwriting process by leveraging LLMs. The system allows users to submit claims containing specific information, and the LLM is instructed to evaluate each claim, predicting the appropriate decision based on existing underwriting guidelines that outline relevant rules and regulations.

Additionally, the service can extract rules from these guideline documents, ensuring that the LLM's decision-making process remains up-to-date and compliant with the latest guidelines.

The project offers two key functionalities:

1. Structured Extraction of Rules from Guideline Documents: The LLM is used as a Data extraction service to extract rules from guideline documents.
2. Claim Approval or Denial Classification: The LLM acts as an agent, classifying claims for approval or denial based on the extracted rules.


# Setup

## AWS Environment

1. Set up the S3 bucket to store the PDF documents, the Claim and the Prompt template.
2. Set up two DynamoDB tables to store the extracted rules, and the prediction data.
3. Create an IAM role for the Lambda function with permissions to access S3, DynamoDB, and invoke Claude 3 AWS Lambda full access.
4. Create a folder to split the Lambda function into 4 files: init, main containing the functions to extract text from PDF, invoke LLM, and extract rules. The prompt file will handle the prompt stored in S3 as a text file, which will be fed to the model. The Lambda function file will hold the lambda-handler function to import all the functions.
5. Create a Lambda function in the AWS console, choosing the runtime: Python3.9.
6. Configure the function with appropriate memory and timeout settings, initially fixed at 60s but reduced to 45s, and attach the IAM role created in step.

### Used AWS Services

- **AWS Lambda**: Create Lambda functions that will handle the underwriting process and interact with other AWS services. first lambda function for rules extraction. The second lambda function for Claim processing handler.

- **Amazon Dynamodb**: Use DynamoDB to store claim information and rules.
 
- **Amazon S3**: Use S3 for storing documents and other related data.
 
- **Amazon API gateway**: Expose Lambda functions as HTTP endpoints so that clients can submit claims via a web interface or other applications.

## Python dependencies

The following libraraies are required as dependencies:

```bash
pip install pypdf json_repair
```

> Please make sure to use the Python 3.9 runtime.

# Functionnalities

The auto underwriting system is a solution designed to automate the insurance underwriting process with the help of LLMs. It will make decisions on whether to approve, decline, or adjust a user's insurance claim.

The claim refers to the user's data that will be processed within an API request. Once the system receives the claim in JSON format, it will be evaluated based on the insurance rules document stored in an S3 bucket.

To automate the process efficiently, I will use AWS Lambda functions, which provide a serverless computing environment. This allows the code to be executed without the need to provision or manage servers.

The process will be divided into two main parts:

1. Receive the user's claim in JSON format and retrieve the relevant insurance rules from the S3 bucket. It will then pass the claim data and rules to the LLM for evaluation.

2. Using the LLM Analyze the claim data against the insurance rules and make a decision on whether to approve, decline, or adjust the claim. This decision will be returned to the second Lambda function, which will then communicate the outcome to the DXC insurance platform.

## Part 1: Rules Extraction

the goal as mentioned above is to automate the process, uploading PDF documents containing rules to an S3 bucket, extracting text from these documents, invoking an external model to extract rules, and finally saving the extracted rules in DynamoDB. I'll achieve this using an AWS Lambda function, leveraging Boto3 SDK for S3 interaction, PyPDF for PDF text extraction, and integrating with Claude 3 and DynamoDB.

The functionnalities are combined in the main function of the folder:

1. **Read the PDF document and Extract Text**:

- I used the Boto3 SDK to download the uploaded PDF document from S3 within the Lambda function.
- I added a layer `pypdf-layer` to the lambda function using the cloudshell, that enable us to use the pypdf library.
- I used `PyPDF` to extract text from the downloaded PDF document.
- Ensuring that the Lambda function has the appropriate permissions to read objects from the S3 bucket.

1. **Invoke the LLM to Extract Rules**:

- Invoke the Claude 3 sonnet using bedrock by identify the service name the region name and the modelID from the API request.
- Pass the extracted text as input to the Claude 3 Lambda function.
- Return a encoded response from claude 3 body. I create a function to decode the model output using utf-8 and return only the desired content extracted that must be structured in a Json format
- I added a layer json-repair-layer to use the library `json_repair` to edit json form
- Ensuring that the Lambda function has permission to invoke bedrock

1. **Save Extracted Rules to DynamoDB table**:

- Using the Boto3 SDK within the Lambda function to interact with DynamoDB.
- Create an item in the DynamoDB table to store the extracted rules along with the additional metadata rule number and rule content to specify all rules with their context in separate rows.
- Ensuring that the Lambda function has the necessary permissions to write to the DynamoDB table.
The second file is the Prompt
The Prompt File contain the function to call the prompt from the S3 bucket since the prompt was saved in s3 as file.txt includes the detailed prompt.

**lambda function**

Manages the the Validation for:
- [x] Detect if the function was invoked via a Function URL
- [x] Handle OPTIONS request for CORS
- [x] Ensure the request method is POST
- [x] Calls all the previous function to returns a dictionary with a status code and the response body.

## Part 2: Claim processing Handler

The role of the second Lambda function is to automate the processing of insurance claims by integrating data retrieval, rules processing, LLM invocation, then I result storage into a DynamoDB table.
Here’s an explanation of how I build this Lambda Function, each responsibility and how it fits into the overall goal of the function:

These functionnalities are combined in the main function of the folder ''claim-processing'':

1.**Get rules from the DynamoDB table**: To get the rules stored from DynamoDB table using boto3 to interact with AWS services from within the Lambda function.

1. **Extract the content of rules function**: This function process the list of rules extracted to isolate and collect the content of each rule. Which can be more easily used as input for the next operation invoking the model.

2. **Invoke the LLM through Amazon Bedrock**: For predictions I call the LLM using Anthropic models available on Amazon Bedrock. You can use any bedrock Foundation model. The prompt template is formated and sent to the LLM via Amazon Bedrock and returns the generated response. specifying the `model_id` and `version`. To generate a response.

3. **Save LLM's decision to DynamoDB**: The last function stands for saving the predictions to DynamoDB as a history, with the claim and the rules used, the rules are saved in a json format as the last item.

The Prompt template contains the function to call the prompt from the S3 bucket since the prompt was saved in s3 as file.txt includes the detailed prompt instructions with the few shot technique.

# API endpoints

## Rules extraction

path: `auto-claim/extract-rules`

### Example request

```
{
  "httpMethod": "POST",
  "path": "auto-claim/extract-rules"
  "body": "{\"doc_s3_path\": \"s3://path/to/s3_bucket/document.pdf\"}"
}
```

### Example response

```
{
    "statusCode": 200,
    "body": "Rules extracted and saved to DynamoDB successfully!"
}
```

## Decision generation

path: `auto-claim/predict`
HTTP Method: `POST`

### Example request

```
{
 "requestContext": {
 "httpMethod": "POST"
 },
 "path": "auto-claim/predict",
 "body": "{\"Claim\": {\"ClaimID\": \"8\", \"PolicyNumber\": \"POL9012\", \"ClaimDate\": \"3/23/2024\", \"IncidentDate\": \"3/13/2024\", \"ReportedWithinPolicyTimeframe\": \"Yes\", \"IncidentType\": \"Vandalism\", \"EstimatedRepairCost\": \"15930\", \"ActualCashValue\": \"25571\", \"ClaimAmount\": \"9623\", \"PolicyCoverageLimit\": \"15000\", \"Deductible\": \"1500\", \"DriverAtFault\": \"Partial\", \"LegalActivityInvolved\": \"No\", \"EvidenceOfFraud\": \"Yes\", \"ClaimSeverity\": \"0.622971335\", \"TotalLoss\": \"FALSE\", \"PayableClaimAmount\": \"8123\", \"ClaimOutcome\": \"Fraud\", \"FaultPercentage\": \"32\", \"EvidenceStheces\": \"Witness Statement, Dashcam Footage, Police Report\", \"ExpertConsulted\": \"No\", \"LiabilityDisputed\": \"No\"}}"
}
```

**Request**:

> `POST` HTTP method Indicates that this is a POST request, which is typically used to submit data to be processed to a specified resource.
> 
> **Path**: The endpoint or path where the request is being sent. This suggests that the request is being handled by the Claimprocessing-Handler in the claimstage context.

**body**:

The body contains the actual data being sent with the request, in JSON format. It has a nested JSON object labeled "Claim", which includes various details about an insurance claim.

These parameters include various details related to an insurance claim, such as identifiers, dates, incident information, financial aspects, and claim evaluation attributes.

**Parameters**:

1. `ClaimID`: A unique identifier for the claim.
2. `PolicyNumber`: The number identifying the insurance policy under which the claim is made.
3. `ClaimDate`: The date when the claim was filed.
4. `IncidentDate`: The date when the incident (leading to the claim) occurred.
5. `ReportedWithinPolicyTimeframe`: Indicates whether the incident was reported within the timeframe allowed by the policy.
6. `IncidentType`: Describes the type of incident that led to the claim.
7. `EstimatedRepairCost`: The estimated cost to repair the damage caused by the incident.
8. `ActualCashValue`: The actual cash value of the damaged item or property.
9. `ClaimAmount`: The amount being claimed by the policyholder.
10. `PolicyCoverageLimit`: The maximum amount the policy will cover for this type of claim.
11. `Deductible`: The amount the policyholder is responsible for paying out-of-pocket before the insurance covers the rest.
12. `DriverAtFault`: Indicates the degree of fault attributed to the driver (if applicable).
13. `LegalActivityInvolved`: Indicates whether there is any legal activity associated with the claim.
14. `EvidenceOfFraud`: Indicates whether there is evidence suggesting that the claim might be fraudulent.
15. `ClaimSeverity`: A numerical value indicating the severity of the claim.
16. `TotalLoss`: Indicates whether the claim resulted in a total loss.
17. `PayableClaimAmount`: The amount the insurance company has determined it will pay out for the claim.
18. `ClaimOutcome`: The outcome or decision regarding the claim.
19. `FaultPercentage`: The percentage of fault assigned to the policyholder or claimant.
20. `EvidenceStheces`: Lists the stheces of evidence supporting the claim.
21. `ExpertConsulted`: Indicates whether an expert was consulted in the evaluation of the claim.
22. `LiabilityDisputed`: Indicates whether there is any dispute regarding liability for the incident.

### Example response

```
{
 "statusCode": 200,
 "body": {
 "prediction": "Denial",
 "Claim": {
 "ClaimID": "8",
 "PolicyNumber": "POL9012",
 "ClaimDate": "3/23/2024",
 "IncidentDate": "3/13/2024",
 "ReportedWithinPolicyTimeframe": "Yes",
 "IncidentType": "Vandalism",
 "EstimatedRepairCost": "15930",
 "ActualCashValue": "25571",
 "ClaimAmount": "9623",
 "PolicyCoverageLimit": "15000",
 "Deductible": "1500",
 "DriverAtFault": "Partial",
 "LegalActivityInvolved": "No",
 "EvidenceOfFraud": "Yes",
 "ClaimSeverity": "0.622971335",
 "TotalLoss": "FALSE",
 "PayableClaimAmount": "8123",
 "ClaimOutcome": "Fraud",
 "FaultPercentage": "32",
 "EvidenceStheces": "Witness Statement, Dashcam Footage, Police Report",
 "ExpertConsulted": "No",
 "LiabilityDisputed": "No"
 },
 "rules_ids": [
 "19, 12"
 ]
 }
}
```

this response is returned to the user, and simultanuously saved on the DynamoDB.

# Testing and Deployment

- I test the Lambda function with sample Insurance Rules PDF document to ensure that it performs as expected.
- Deploy the Lambda function to the desired AWS region for production use.

Here I create a Lambda function responsible for uploading PDF documents to S3, extracting text from the PDF, and the Claude 3 model to extract rules, and saving the extracted rules in DynamoDB table. I will move to the second lambda function that focuses on Claims Processing and Handle the response.

I deployed the function, I set an event that contain a random claim from a user.
The event data is a JSON object that represents the data structure expected by the Lambda function, I set the payload.
I test to verify if the function correctly processes the claim interacts with db involves the claude3 sonnet and saves the result in a DynamoDB.


## Deploying the service using an API Gateway:

**trigger**: I add a trigger to the Lambda function I used theAPI Gateway to deploy the function.

**Create an API Gateway**: In the AWS Management Console I searched API Gateway. I Click on "Create API" and I choose the REST API type. by Selecting "New API" and give a name to the API (Claim).

**Create a resource and Method**: Once the API is created, I define a resource and method to invoke the Lambda function:
I choose the `POST` HTTP method for invoking the Lambda function.

**Deploy the API**: After creating the resource and method, I deploy the API: I selected the method then I click on "Actions" and I choose "Deploy API". I create a New Stage. Once I Clicked on "Deploy" the API is deployed.

## API testing

Once the API is deployed, scrolling down an invoke URL shown. I use it to test the API in Postman.
Postman is a popular API (Application Programming Interface) development and testing tool. It provides an easy-to-use interface to interact with APIs.
Define the functionnalities, and convert them to API endpoints.
each API request need a URL endpoint, payload and event type.
validate requests, users should use the same sturucture defined from the README file. If the user uses a different payload for example, the response body will contain a 400 HTTP statusCode (which means an error).

**Todo:**

- [x] Add custom `OPTIONS` to handle CORS
- [x] Validation for allowed HTTP methods
- [x] Validate API method and path
- [x] Parse and validate body
- [x] Check for missing or incorrect fields
- [x] Check for any additional unexpected field.
- [x] Calls all the previous function to returns a dictionary with a status code and the response body.
