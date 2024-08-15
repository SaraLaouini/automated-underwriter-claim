import boto3
import json
import os
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from json_repair import repair_json


s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def extract_text_from_pdf(pdf_content):
    try:
        pdf_reader = PdfReader(BytesIO(pdf_content))
        return "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def invoke_llm(text, prompt):
    bedrock_runtime_client = boto3.client(service_name=os.environ.get('service_name'), region_name=os.environ.get('region_name'))
    response = bedrock_runtime_client.invoke_model(
        modelId=os.environ.get('model_id'),
        body=json.dumps(
            {
                "anthropic_version": os.environ.get('anthropic_version'),
                "max_tokens": int(os.environ.get('max_tokens')),
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt + text}],
                    }
                ],
            }
        ),
    )
    return response

def extract_rules(response):
    body = response['body'].read().decode('utf-8')
    body_json = json.loads(body)
    rules_text = body_json['content'][0]['text']
    try:
        rules_text = repair_json(rules_text)
        rules = json.loads(rules_text)
    except Exception as e:
        print(f"Error extracting rules: {e}")
        rules = {}
    return rules

def save_rules_to_db(rules, file_key):
    table_name = os.environ.get('table_name')
    table = dynamodb.Table(table_name)
    update_datetime = datetime.now().isoformat()

    rule_number = 1

    try:
        for section in rules['sections']:
            section_title = section.get('title', 'Unknown Title')
            for subsection in section.get('subsections', []):
                subsection_title = subsection.get('title', 'Unknown Subsection Title')
                for guideline in subsection.get('guidelines', []):
                    rule = guideline.get('rule', 'No Rule')
                    table.put_item(Item={
                        'RuleNumber': str(rule_number),
                        'RuleContent': rule,
                        'Section': section_title,
                        'Subsection': subsection_title,
                        'DocumentName': file_key,
                        'update_datetime': update_datetime
                    })
                    rule_number += 1
    except Exception as e:
        print(f"Error saving rules to DB: {e}")

def get_rules_from_db(table_name):
    rules = []

    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        for item in response['Items']:
            rulenumber = item.get("RuleNumber")
            rulecontent = item.get("RuleContent")
            documentname = item.get("DocumentName")
            if rulenumber is not None and rulecontent is not None and documentname is not None:
                rule = {"id": rulenumber, "content": rulecontent, "DocumentName": documentname}
                rules.append(rule)
    except Exception as e:
        print(f"Error retrieving items content from DynamoDB: {e}")
    return rules

def extract_rules_contents(rules):
    rule_contents = []
    for rule in rules:
        content = rule.get("content")
        if content is not None:
            rule_contents.append(content)
    return rule_contents

def read_file_from_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read().decode('utf-8')
    except s3.exceptions.NoSuchKey:
        print(f"Error: The specified key does not exist in the bucket {bucket}. Key: {key}")
        return None
    except Exception as e:
        print(f"Error reading the S3 file: {e}")
        return None

def invoke_claude_3_sonnet(prompt):
    bedrock_runtime_client = boto3.client(service_name=os.environ.get("service_name"), region_name=os.environ.get("region_name"))
    model_id = os.environ.get("model_id")
    response = bedrock_runtime_client.invoke_model(
        modelId=model_id,
        body=json.dumps(
            {
                "anthropic_version": os.environ.get("anthropic_version"),
                "max_tokens": int(os.environ.get("max_tokens")),
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
            }
        ),
    )
    result = json.loads(response.get('body').read())
    return result

def save_response_to_dynamodb(table_name, partition_key, data):
    table = dynamodb.Table(table_name)
    item = {
        partition_key: data['Claim']['ClaimID'],
        'PolicyNumber': data['Claim']['PolicyNumber'],
        'ClaimDate': data['Claim']['ClaimDate'],
        'IncidentDate': data['Claim']['IncidentDate'],
        'ReportedWithinPolicyTimeframe': data['Claim']['ReportedWithinPolicyTimeframe'],
        'IncidentType': data['Claim']['IncidentType'],
        'EstimatedRepairCost': data['Claim']['EstimatedRepairCost'],
        'ActualCashValue': data['Claim']['ActualCashValue'],
        'ClaimAmount': data['Claim']['ClaimAmount'],
        'PolicyCoverageLimit': data['Claim']['PolicyCoverageLimit'],
        'Deductible': data['Claim']['Deductible'],
        'DriverAtFault': data['Claim']['DriverAtFault'],
        'LegalActivityInvolved': data['Claim']['LegalActivityInvolved'],
        'EvidenceOfFraud': data['Claim']['EvidenceOfFraud'],
        'ClaimSeverity': data['Claim']['ClaimSeverity'],
        'TotalLoss': data['Claim']['TotalLoss'],
        'PayableClaimAmount': data['Claim']['PayableClaimAmount'],
        'ClaimOutcome': data['Claim']['ClaimOutcome'],
        'FaultPercentage': data['Claim']['FaultPercentage'],
        'EvidenceSources': data['Claim']['EvidenceSources'],
        'ExpertConsulted': data['Claim']['ExpertConsulted'],
        'LiabilityDisputed': data['Claim']['LiabilityDisputed'],
        'Prediction': data['prediction'],
        'RulesUsed': data['rules_used'] 
    }

    try:
        table.put_item(Item=item)
        print(f"Successfully saved Claim {data['Claim']['ClaimID']} to DynamoDB.")
    except Exception as e:
        print(f"Error saving Claim {data['Claim']['ClaimID']} to DynamoDB: {e}")