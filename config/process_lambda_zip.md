
Search
Write
Sign up

Sign in



How to Extract ZIP Files in an Amazon S3 Data Lake with AWS Lambda
Darren Roback
Darren Roback

·
Follow

6 min read
·
Apr 7, 2024
11


1



I recently came into a scenario where I needed to develop a mechanism that would automate the extraction of files within a ZIP archive stored in Amazon S3. While this mechanism will be part of a larger solution I was working on implementing, I wanted to ensure that the processing of ZIP archives could be done atomically for portability purposes, as I’ve encountered similar scenarios in the past.

On the surface, this may seem like a trivial task (that was my initial thought), however, I quickly discovered that I was going to encounter challenges.

Some questions I began to ask myself included:

How large are the ZIP files would I need to process?
How many ZIP files would I need to process at one time?
How often would this process need to execute?
How could I optimize this process to ensure I was not transferring large amounts of content back and forth to AWS?
How could I optimize this process to conserve compute resources (and save cost)?
Frankly, I didn’t know the answers to some of these questions, but the exercise of thinking through them made me realize I was going to need to develop a fairly optimized mechanism to process the ZIP archives.

I decided to investigate the feasibility of this solution using AWS Lambda, as it’s fairly common to use this serverless service to process files within a data lake. Using AWS Lambda to process objects within an S3 bucket in the same region would also help me to save on data transfer costs. And Lambda could certainly process a large volume of objects thanks to function concurrency, making it suitable for this project. But how could I optimize my code to ensure I wasn’t going to have to provision large Lambda functions? I quickly realized this was the main challenge, but decided it was worth diving into.

In this blog post I will provide an example solution for others encountering similar scenarios, with a focus on optimizing the codebase to run in a minimally-provisioned Lambda function.

Prerequisites
Before you proceed, ensure that within your environment you have:

An S3 bucket that can be used for testing.
Permissions to create a Lambda function.
Permissions to configure S3 Event Notifications.
Permissions to deploy CloudFormation templates.
Assumptions
Things to know about the solution in this blog post:

The examples provided are about deploying this solution in the AWS US East 1 (N. Virginia) AWS Region, however, you can deploy this solution in the Region of your choice.
Solution overview
The solution architecture and overall workflow are detailed in Figure 1 that follows.


Figure 1: Solution Overview
Figure 1 provides an overview of the components used in this solution, and for illustrative purposes I will step through them here.

End users upload ZIP files to the root of an Amazon S3 bucket.
S3 sends an event notification to AWS Lambda with the payload containing one (or more) ZIP files that have been uploaded to the root of the S3 bucket.
Lambda downloads the ZIP file to local ephemeral storage (/tmp).
Lambda extracts the contents of the ZIP archive into local ephemeral storage (/tmp).
Lambda uploads each file within the /tmp directory to the /unzipped folder in S3 and subsequently clears the contents of the /tmp directory to process the next ZIP file.
Ephemeral storage in Lambda
AWS Lambda has long offered 512MB of ephemeral storage (/tmp) for customers running code in this serverless service. And in March of 2022, AWS increased the maximum capacity of this from 512 MB to 10 GB, giving customers control over the amount of ephemeral storage provisioned for their functions.

This presents a great solution for this use case, as processing large ZIP files in memory would be costly. Many of us are aware of AWS pricing for Lambda based on provisioned memory, and those investigating ephemeral storage will note that is far cheaper (MB for MB) in comparison.

ZIP processor Lambda function
Below is an example Lambda function that can be used to automate the extraction of files from ZIP archives stored in S3. This function receives event notifications from S3 for all s3:ObjectCreated:* events within the / prefix, and having a .zip suffix. Lambda parses out the bucket and key values within the event message, and uses this information to download and process the ZIP archive.

This function first downloads the ZIP archive into ephemeral storage (/tmp) instead of reading the object into memory. The function then extracts all files within the archive to the /tmp directory. Finally, the function uses the upload_fileobj() method instead of put_object() to stream the file upload directly into S3, thereby avoiding reading it fully into memory. The upload_fileobj() method also supports multipart uploads, making it a strong choice for larger files.

This code is intended to serve as an example and should be tested in your environment.

# Import statements
import boto3
import zipfile 
from datetime import * 
import os
import logging
import sys
import traceback
import json

# Set logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create boto3 session
session = boto3.Session()

# Create S3 client object
s3_client = session.client('s3') 

# Create S3 resource
s3_resource = boto3.resource('s3')

# Set temp file path
tmp_file_path = '/tmp/file.zip'

# Set unzipped output path
unzip_path = 'unzipped/'

# Download file function
def download_file(bucket, key):
    
    # Create S3 resource object
    s3_object = s3_resource.Object(bucket, key)

    # Download file to /tmp
    try:
        logger.info("Downloading file to /tmp...")
        s3_object.download_file(tmp_file_path)
        logger.info("Download complete.")
    except Exception as e:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
        err_msg = json.dumps({
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        })
        logger.error(err_msg)
        
    # List zipped contents of /tmp
    logger.info("Zipped contents of /tmp directory:")
    for file in os.listdir("/tmp"):
        logger.info(os.path.join(f"/tmp{file}"))

# Unzip file function
def unzip_file(bucket, key): 

    # Create zipfile object
    zip = zipfile.ZipFile(tmp_file_path)
    
    # Extract zipped files to /tmp
    logger.info("Extracting files to /tmp...")
    zip.extractall('/tmp') 

    # List contents of /tmp
    logger.info("Extracted contents of /tmp directory:")
    for file in os.listdir("/tmp"):
        
        # List file paths
        logger.info(os.path.join(f"/tmp{file}"))
        
        # List file sizes
        logger.info(f"File size: {os.path.getsize(os.path.join('/tmp', file))} bytes")
   
    # Process each file within the zip 
    for filename in zip.namelist(): 

        # Set zip file info
        file_info = zip.getinfo(filename) 
        logger.info(f"Zip file info: {file_info}")  

        # Copy the files to the 'unzipped' S3 folder 
        logger.info(f"Uploading file {filename} to {bucket}/{unzip_path}{filename}") 
        
        # Upload file to S3
        with zip.open(filename) as f:
            try:
                response = s3_client.upload_fileobj(
                Fileobj=f, 
                Bucket=bucket,
                Key=f'{unzip_path}{filename}'
                )
            except Exception as e:
                exception_type, exception_value, exception_traceback = sys.exc_info()
                traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
                err_msg = json.dumps({
                    "errorType": exception_type.__name__,
                    "errorMessage": str(exception_value),
                    "stackTrace": traceback_string
                })
                logger.error(err_msg)
    
        # Delete the file from /tmp
        logger.info(f"Deleting file {filename} from /tmp...")
        os.remove(os.path.join('/tmp', filename))

    # Delete the zip file from /tmp
    logger.info("Deleting zip file from /tmp...")
    os.remove(tmp_file_path)

# Main Lambda function
def lambda_handler(event, context):

  # Process each object in the S3 event 
  for record in event['Records']:

    # Extract bucket and key
    bucket = record['s3']['bucket']['name'] 
    key = record['s3']['object']['key']

    # Logging
    logger.info(f"Received bucket: {bucket}")
    logger.info(f"Received key: {key}")

    # Call functions to download and unzip file
    try:
      download_file(bucket, key)  
      unzip_file(bucket, key)
    except Exception as e:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
        err_msg = json.dumps({
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        })
        logger.error(err_msg)
Testing the ZIP processor function
To test this solution, I created two ZIP files that each contained five .txt files of 250MB each with randomly generated characters. I uploaded these two ZIP files to S3 as shown below. Of note is how terrible the compression is.

[cloudshell-user@ip-1-2-3-4 ~]$ aws s3 ls s3://my-test-bucket

2024-04-07 22:23:20 1311120357 TestZipFile1.zip
2024-04-07 22:23:20 1311120359 TestZipFile2.zip
I’m using AWS Serverless Application Model to deploy my function, and found a sweet spot for my test scenario with the function properties below. Using this configuration, my Lambda function averaged a runtime of roughly 180 seconds.

AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  LambdaZipProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: LambdaZipProcessorFunction
      CodeUri: lambda-zip-processor/
      Handler: app.lambda_handler
      Runtime: python3.11
      Timeout: 600
      MemorySize: 512
      EphemeralStorage: 
        Size: 3072
      Policies:
      # Allow full access to Amazon S3
      - AmazonS3FullAccess
To confirm the successful processing of ZIP files stored in S3, I then listed the contents of the unzipped folder in my S3 bucket.

[cloudshell-user@ip-1-2-3-4 ~]$ aws s3 ls s3://my-test-bucket/unzipped/

2024-04-07 23:10:37  262144000 TestFile1.txt
2024-04-07 23:12:12  262144000 TestFile10.txt
2024-04-07 23:10:46  262144000 TestFile2.txt
2024-04-07 23:10:55  262144000 TestFile3.txt
2024-04-07 23:11:04  262144000 TestFile4.txt
2024-04-07 23:11:13  262144000 TestFile5.txt
2024-04-07 23:12:22  262144000 TestFile6.txt
2024-04-07 23:12:30  262144000 TestFile7.txt
2024-04-07 23:12:39  262144000 TestFile8.txt
2024-04-07 23:12:49  262144000 TestFile9.txt
Closing thoughts
Researching ways others have processed ZIP files in S3 led me to a lot of Python-based solutions that would read and process these archives in memory, potentially being a costly (if even feasible) solution running on AWS Lambda.

Using the recent enhancements in Lambda ephemeral storage along with the upload_fileobj() method to stream the extracted files from disk to S3 allowed me to lessen the provisioned memory of my Lambda function, helping me to save cost.

I encourage you to customize and test this solution within your environment and share your feedback in the comments below!



Be part of a better internet.
Get 20% off membership for a limited time.

Free
Distraction-free reading. No ads.

Organize your knowledge with lists and highlights.

Tell your story. Find your audience.

Sign up for free
Membership
Get 20% off
Read member-only stories

Support writers you read most

Earn money for your writing

Listen to audio narrations

Read offline with the Medium app

Try for $ 5 $ 4/month
AWS
AWS Lambda
S3
Python
11


1


Darren Roback
Written by Darren Roback
16 Followers
Sr. Solutions Architect @ AWS | 6x AWS Certified | 3x Microsoft Certified | IoT | GenAI | Cloud Security | Technology consultant, writer, and speaker

Follow

More from Darren Roback
How to Manage Email Unsubscribes in Amazon Pinpoint
Darren Roback
Darren Roback

How to Manage Email Unsubscribes in Amazon Pinpoint
Amazon Pinpoint is a flexible, scalable marketing communications service that connects you with customers over email, SMS, push…
Jan 19
5
2
Complying with Google and Yahoo Easy Unsubscribe Requirements in Amazon Pinpoint
Darren Roback
Darren Roback

Complying with Google and Yahoo Easy Unsubscribe Requirements in Amazon Pinpoint
Feb 15
21
3
See all from Darren Roback
Recommended from Medium
Golang character on an AWS Lambda rocket, carrying an S3 bucket. This scene captures the essence of AWS S3 and Lambda being utilized with Golang for processing large files.
Rodan Ramdam
Rodan Ramdam

in

wesionaryTEAM

Mastering Large File Processing with AWS S3, Lambda, and Go
In this article, we’ll dive into creating a scalable file processing system, specifically designed to handle large files using a…
Apr 9
441
Streamlined AWS S3 File Uploads with Tagging via Pre-signed URLs — A 3-Step Process — Code…
Peng Cao
Peng Cao

in

AWS Tip

Streamlined AWS S3 File Uploads with Tagging via Pre-signed URLs — A 3-Step Process — Code…
Uploading files to AWS S3 is crucial for many web applications, but it can be complex for developers and impact user experience…

May 13
7
Lists



Coding & Development
11 stories
·
714 saves



Predictive Modeling w/ Python
20 stories
·
1410 saves
Principal Component Analysis for ML
Time Series Analysis
deep learning cheatsheet for beginner
Practical Guides to Machine Learning
10 stories
·
1709 saves

AI-generated image of a cute tiny robot in the backdrop of ChatGPT’s logo

ChatGPT
21 stories
·
733 saves
Automatic text extraction from PDF files once uploaded to S3 bucket using AWS Textract, Lambda, SQS…
ben
ben

Automatic text extraction from PDF files once uploaded to S3 bucket using AWS Textract, Lambda, SQS…
This post will guide you through the step-by-step approach of automating text extraction from PDF files upon new uploads into an existing…

Feb 8
112
How To Upload Files To AWS S3 Using Serverless Lambda Functions
Uriel Bitton
Uriel Bitton

in

Success With AWS

How To Upload Files To AWS S3 Using Serverless Lambda Functions
The quickest and easiest way to run code on the cloud without creating or managing servers.

Mar 28
1
The resume that got a software engineer a $300,000 job at Google.
Alexander Nguyen
Alexander Nguyen

in

Level Up Coding

The resume that got a software engineer a $300,000 job at Google.
1-page. Well-formatted.

Jun 1
15.1K
234
All about Lambda!
Hasitha Dulanjana Palihenage Don
Hasitha Dulanjana Palihenage Don

All about Lambda!
lambda Function — Function definiton that will be initialized and called by the lambda service.

Jun 6
5
See more recommendations
Help

Status

About

Careers

Press

Blog

Privacy

Terms

Text to speech

Teams