import boto3
import json
import os
import logging
import re
from botocore.exceptions import ClientError, ReadTimeoutError
from Prediction.main import extract_text_from_pdf, invoke_llm, extract_rules, save_rules_to_db
from Prediction.main import read_file_from_s3, get_rules_from_db, extract_rules_contents, invoke_claude_3_sonnet, save_response_to_dynamodb
from json_repair import repair_json

logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logging.info(f"Received event: {json.dumps(event)}")

    try:
        if 'body' not in event:
            logging.error("Body is null")
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Invalid payload"})
            }

        if isinstance(event['body'], str):
            body = json.loads(event['body'])
        elif isinstance(event['body'], dict):
            body = event['body']
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "Unexpected body format"})
            }

        logging.info(f"Parsed body: {body}")

        responses = {}

        if 'Claim' in body:
            responses['claim_response'] = process_claim(body['Claim'])

        return {
            'statusCode': 200,
            'body': json.dumps(responses)
        }

    except Exception as e:
        logging.error(f"Error processing request: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }

def process_claim(Claim):
    errors = validate_claim(Claim)

    if errors:
        return {
            'statusCode': 400,
            'body': json.dumps({'errors': errors})
        }

    R_number_content_list = get_rules_from_db(os.environ.get("table_name"))
    Rules_contents = extract_rules_contents(R_number_content_list)

    bucket_name = os.environ.get("bucket_name")
    file_key = os.environ.get("file_key")
    variables = {
        'Rules_contents': Rules_contents,
        'R_number_content_list': R_number_content_list,
        'Claim': Claim
    }

    file_content = read_file_from_s3(bucket_name, file_key)
    prompt = file_content.format(**variables)

    prediction = None
    retry_count = 3
    for attempt in range(retry_count):
        try:
            prediction = invoke_claude_3_sonnet(prompt)
            break
        except ReadTimeoutError as e:
            logging.warning(f"Read timeout on attempt {attempt + 1}/{retry_count}: {e}")
            if attempt == retry_count - 1:
                raise

    result = re.search(r'<prediction>(.*?)</prediction>', prediction['content'][0]['text'], re.DOTALL)
    pred = result.group(1) if result else None

    rules_used_match = re.search(r'<rules_used>(.*?)</rules_used>', prediction['content'][0]['text'], re.DOTALL)
    rules_used_str = rules_used_match.group(1) if rules_used_match else '[]'

    logging.info(f"Extracted rules_used string: {rules_used_str}")

    try:
        repaired_rules_used_str = repair_json(rules_used_str)
        rules_used_list = json.loads(repaired_rules_used_str)
    except Exception as e:
        logging.error(f"Error parsing rules_used: {e}")
        rules_used_list = []

    response_body = {
        'prediction': pred,
        'Claim': Claim,
        'rules_used': rules_used_list
    }

    logging.info(f"Response body to be saved: {json.dumps(response_body, indent=2)}")

    save_response_to_dynamodb('ClaimResults', 'ClaimID', response_body)

    return {
        'statusCode': 200,
        'body': json.dumps(response_body)
    }

def validate_claim(Claim):
    errors = []
    required_fields = {
        "ClaimID": str,
        "PolicyNumber": str,
        "ClaimDate": str,
        "IncidentDate": str,
        "ReportedWithinPolicyTimeframe": str,
        "IncidentType": str,
        "EstimatedRepairCost": str,
        "ActualCashValue": str,
        "ClaimAmount": str,
        "PolicyCoverageLimit": str,
        "Deductible": str,
        "DriverAtFault": str,
        "LegalActivityInvolved": str,
        "EvidenceOfFraud": str,
        "ClaimSeverity": str,
        "TotalLoss": str,
        "PayableClaimAmount": str,
        "ClaimOutcome": str,
        "FaultPercentage": str,
        "EvidenceSources": str,
        "ExpertConsulted": str,
        "LiabilityDisputed": str
    }
    for field, expected_type in required_fields.items():
        if field not in Claim:
            errors.append(f"Missing field: {field}")
        elif not isinstance(Claim[field], expected_type):
            errors.append(f"Incorrect type for field {field}: expected {expected_type.__name__}, got {type(Claim[field]).__name__}")
    for field in Claim.keys():
        if field not in required_fields:
            errors.append(f"Unexpected field: {field}")
    return errors if errors else None
