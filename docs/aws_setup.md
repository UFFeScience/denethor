# AWS Environment Setup

For the execution of the commands below, we assume that the user already has an AWS account and is in possession of the `AWS Access Key ID` and `AWS Secret Access Key`. Otherwise, it will be necessary to create an AWS account and obtain the access credentials.

## Configure access via AWS CLI on the local machine

To configure access via AWS CLI on the local machine, it is necessary to download the application zip and unzip it:

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
# aws-cli/2.13.37 Python/3.11.6 Linux/6.2.0-36-generic exe/x86_64.ubuntu.22 prompt/off
# aws-cli/2.14.5 Python/3.11.6 Windows/10 exe/AMD64 prompt/off
```

```bash
aws configure
```

Expected output:

```bash
AWS Access Key ID: ...............
AWS Secret Access Key: ...........................
Default region name: sa-east-1
Default output format: json
```

## Create S3 Buckets

It will be necessary to create three S3 buckets for the execution of the workflow on AWS Lambda:

1. A bucket to store the input files;
2. A bucket to store the output files from the phylogenetic tree construction stage;
3. A bucket to store the output files from the subtree mining stage.

For this, execute the following commands in the terminal:

```bash
aws s3api create-bucket --bucket denethor --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

aws s3api create-bucket --bucket denethor-input --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

aws s3api create-bucket --bucket denethor-tree --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

aws s3api create-bucket --bucket denethor-subtree --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1
```

To verify that the buckets were created correctly:

```bash
aws s3api list-buckets
```

aws s3 cp data/full_dataset s3://denethor/data/full_dataset --recursive

## Lambda Functions Preparation

### Create a base layer for the lambda function

___

Before creating the lambda functions, it is necessary to create a base layer for the function. To do this, you need to create a directory called `package` and then install the project dependencies and copy the ClustalW executable. Finally, compress the directory into a .zip file to be used in creating the layer.

```bash
cd lambda_functions

mkdir package

python -m pip install --target package/python -r requirements.txt

cp -R ./lib/clustalw-2.1-linux-x86_64-libcppstatic package/python

```

Linux:

```bash
zip -r lambda_layer.zip ./package
```

Windows:

```bash
"C:\Program Files\7-Zip\7z.exe" a -tzip lambda_layer.zip package
```

Creating the base layer in AWS should indicate the interpreter that will be used (Python 3.12) and the *zip file* (previously created) that contains the project dependencies.

```bash
aws lambda publish-layer-version --layer-name lambda_layer --zip-file fileb://lambda_layer.zip --compatible-runtimes python3.12 --region sa-east-1
```

___

### Tree Constructor Function

___

This will be the Lambda Function for the activity of constructing Phylogenetic Trees. Initially, it is necessary to create a .zip file containing the lambda function code and the project dependencies.

```bash
cd lambda_functions/src 
```

Linux:

```bash
zip tree_constructor.zip tree_constructor_core.py tree_constructor.py utils/file_utils.py
```

Windows:

```bash
"C:\Program Files\7-Zip\7z.exe" a -tzip tree_constructor.zip tree_constructor_core.py tree_constructor.py utils/file_utils.py
```

Then we can create the lambda function in AWS. Replace `xxxxxxxxxxxxx` with your AWS account number:

```bash
aws lambda create-function --function-name tree_constructor \
--zip-file fileb://tree_constructor.zip \
--handler tree_constructor.handler \
--runtime python3.12 \
--role arn:aws:iam::xxxxxxxxxxxxx:role/service-role/Lambda_S3_access_role \
--timeout 15 \
--memory-size 128 \
--region sa-east-1 \
--layers arn:aws:lambda:sa-east-1:xxxxxxxxxxxxx:layer:lambda_layer:1
```

___

### Subtree Constructor Function

___

This will be the Lambda Function for the subtree constructor activity. Initially, it is necessary to create a .zip file containing the lambda function code and the project dependencies.

```bash
cd lambda_functions/src 
```

Linux:

```bash
zip subtree_constructor.zip subtree_mining_core.py subtree_constructor.py utils/file_utils.py
```

Windows:

```bash
"C:\Program Files\7-Zip\7z.exe" a -tzip subtree_constructor.zip subtree_mining_core.py subtree_constructor.py utils/file_utils.py
```

Then we can create the lambda function in AWS. Replace `xxxxxxxxxxxxx` with your AWS account number:

```bash
aws lambda create-function --function-name subtree_constructor \
--zip-file fileb://subtree_constructor.zip \
--handler subtree_constructor.handler \
--runtime python3.12 \
--role arn:aws:iam::xxxxxxxxxxxxx:role/service-role/Lambda_S3_access_role \
--timeout 900 \
--memory-size 256 \
--region sa-east-1 \
--layers arn:aws:lambda:sa-east-1:xxxxxxxxxxxxx:layer:lambda_layer:1
```

Note that the timeout for the `subtree_mining` function has been set to 900 seconds (15 minutes) and the memory size has been set to 256 MB. These values are necessary because this activity runs for a longer period than the previous one, as it performs comparisons between subtrees.
___