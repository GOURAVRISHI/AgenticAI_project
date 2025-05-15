## Built & Deployed: A Simple Blog Generator Chatbot Using AWS Bedrock + Lambda + S3

import json
import boto3
import botocore.config
from datetime import datetime


### AWS BEDROCK CALL ### - You will get these details from AWS Bedrock model catalogue 

# {
#  "modelId": "meta.llama4-scout-17b-instruct-v1:0",
#  "contentType": "application/json",
#  "accept": "application/json",
#  "body": "{\"prompt\":\"this is where you place your input text\",\"max_gen_len\":512,\"temperature\":0.5,\"top_p\":0.9}"
# }

# Align these values as per your selected model - "max_gen_len" : 512, "temperature" : 0.5, "top_p" : 0.9

def content_generation(blogtopic:str)->str:
    prompt = f"""Write a 200 words blog post on {blogtopic}"""
    body = {
        "prompt": prompt,
        "max_gen_len" : 512,
        "temperature" : 0.5,
        "top_p" : 0.9
    }

    try:
        # We can change the region_name, read_timeout, and retires as per your requirement

        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(read_timeout = 300, retries = {'max_attempts':3})
        )
        # change or update the modelId as per your model
        response = bedrock.invoke_model(body=json.dumps(body), modelId="us.meta.llama4-scout-17b-instruct-v1:0")
        response_content = response.get("body").read()
        response_data = json.loads(response_content)
        #print(response_data)
        blog_details = response_data["generation"]
        return blog_details
    except Exception as e:
        print(e)
        return ""
    

### S3 UPLOADR FUNCTION ###

def s3_uploader(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body=generate_blog, Bucket=s3_bucket, Key=s3_key)
        print(f'File uploaded successfully to S3 bucket {s3_bucket}')
    except Exception as e:
        print(f'Error uploading file to S3 bucket: {e}')

### MAIN LAMBDA FUNCTION ###


def lambda_handler(event, context):
    event = json.loads(event['body'])
    blog_topic = event['blogTopic']

    generate_blog = content_generation(blogtopic=blog_topic)
    
    # change the s3_bucket with your s3 bucket name
    if generate_blog:
        currrent_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        s3_key = f"blogs/{currrent_time}.txt"
        s3_bucket = "bedrockknaagent"  
        s3_uploader(s3_key=s3_key, s3_bucket=s3_bucket, generate_blog=generate_blog)
    else:
        print("No blog generated")

    return {
        'statusCode': 200,
        'body': json.dumps('Blog is Generated Successfully!')
    }