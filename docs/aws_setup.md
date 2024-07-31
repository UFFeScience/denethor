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

It will be necessary to create one S3 bucket to store the input and output files of the Lambda functions.

```bash
aws s3api create-bucket --bucket denethor --region sa-east-1 --create-bucket-configuration LocationConstraint=sa-east-1

```

Verify that the bucket was created correctly:

```bash
aws s3api list-buckets
```

Copy the input data to the bucket:

```bash
aws s3 cp data/full_dataset s3://denethor/data/full_dataset --recursive
```

## Lambda Functions Preparation

### Create a base layer for the lambda function

___

Before creating the lambda functions, it is necessary to create a base layer for the function. To do this, you need to install the project dependencies in a directory called `python` and copy the ClustalW executable. Finally, compress the directory into a .zip file to be used in the layer creation.

```bash
rm -Rf .lambda/lambda_layers/lambda_layer
mkdir -p .lambda/lambda_layers/lambda_layer/python

python3 -m pip install --python-version 3.10 --only-binary=:all: --target .lambda/lambda_layers/lambda_layer/python -r requirements_aws.txt

cp -R resources/libs/clustalw-2.1-linux .lambda/lambda_layers/lambda_layer/python

cd .lambda/lambda_layers/lambda_layer

zip -r lambda_layer.zip python

aws lambda publish-layer-version --layer-name lambda_layer --zip-file fileb://lambda_layer.zip --compatible-runtimes python3.10 --region sa-east-1

cd ../../..
```

___

### Create the denthor layer

___

Create a directory called `python` and then copy the `denethor` lib. Finally, compress the directory into a .zip file to be used in creating the layer.

```bash
rm -Rf .lambda/lambda_layers/denethor_layer/
mkdir -p .lambda/lambda_layers/denethor_layer/python

cp -R src/denethor_utils .lambda/lambda_layers/denethor_layer/python

cd .lambda/lambda_layers/denethor_layer

zip -r denethor_layer.zip python

aws lambda publish-layer-version --layer-name denethor_layer --zip-file fileb://denethor_layer.zip --compatible-runtimes python3.10 --region sa-east-1

cd ../../..
```

___

### Tree Constructor Function

___

Lambda Function for the activity of constructing Phylogenetic Trees. Initially, it is necessary to create a .zip file containing the lambda function code and the project dependencies. Then we can create the lambda function in AWS. Replace `xxxxxxxxxxxxx` with your AWS account number:

```bash
rm -Rf .lambda/lambda_functions/tree_constructor/
mkdir -p .lambda/lambda_functions/tree_constructor/

cp -R src/lambda_functions/tree_constructor* .lambda/lambda_functions/tree_constructor/

cd .lambda/lambda_functions/tree_constructor/

zip tree_constructor.zip *

aws lambda create-function --function-name tree_constructor \
--zip-file fileb://tree_constructor.zip \
--handler tree_constructor.handler \
--runtime python3.10 \
--role arn:aws:iam::058264090960:role/service-role/Lambda_S3_access_role \
--timeout 15 \
--memory-size 128 \
--region sa-east-1 \
--layers "arn:aws:lambda:sa-east-1:058264090960:layer:lambda_layer:6" "arn:aws:lambda:sa-east-1:058264090960:layer:denethor_layer:2"

cd ../../..
```

___

### Subtree Constructor Function

___

This will be the Lambda Function for the subtree constructor activity. Initially, it is necessary to create a .zip file containing the lambda function code and the project dependencies. Then we can create the lambda function in AWS. Replace `xxxxxxxxxxxxx` with your AWS account number:

```bash
rm -Rf .lambda/lambda_functions/subtree_constructor/
mkdir -p .lambda/lambda_functions/subtree_constructor/

cp -R src/lambda_functions/subtree_constructor* .lambda/lambda_functions/subtree_constructor/

cd .lambda/lambda_functions/subtree_constructor/

zip subtree_constructor.zip *

aws lambda create-function --function-name subtree_constructor \
--zip-file fileb://subtree_constructor.zip \
--handler subtree_constructor.handler \
--runtime python3.10 \
--role arn:aws:iam::058264090960:role/service-role/Lambda_S3_access_role \
--timeout 30 \
--memory-size 256 \
--region sa-east-1 \
--layers "arn:aws:lambda:sa-east-1:058264090960:layer:lambda_layer:6" "arn:aws:lambda:sa-east-1:058264090960:layer:denethor_layer:2"

cd ../../..
```

Note that the timeout for the `subtree_mining` function has been set to 30 seconds and the memory size has been set to 256 MB. These values are necessary because this activity runs for a longer period than the previous one.
___

### MAF Database Creator Function

___

```bash
rm -Rf .lambda/lambda_functions/maf_database_creator/
mkdir -p .lambda/lambda_functions/maf_database_creator/

cp -R src/lambda_functions/maf_database_creator* .lambda/lambda_functions/maf_database_creator/

cd .lambda/lambda_functions/maf_database_creator/

zip maf_database_creator.zip *

aws lambda create-function --function-name maf_database_creator \
--zip-file fileb://maf_database_creator.zip \
--handler maf_database_creator.handler \
--runtime python3.10 \
--role arn:aws:iam::058264090960:role/service-role/Lambda_S3_access_role \
--timeout 30 \
--memory-size 256 \
--region sa-east-1 \
--layers "arn:aws:lambda:sa-east-1:058264090960:layer:lambda_layer:6" "arn:aws:lambda:sa-east-1:058264090960:layer:denethor_layer:2"

cd ../../..
```

___

### MAF Database Aggregator Function

___

```bash
rm -Rf .lambda/lambda_functions/maf_database_aggregator/
mkdir -p .lambda/lambda_functions/maf_database_aggregator/

cp -R src/lambda_functions/maf_database_aggregator* .lambda/lambda_functions/maf_database_aggregator/

cd .lambda/lambda_functions/maf_database_aggregator/

zip maf_database_aggregator.zip *

aws lambda create-function --function-name maf_database_aggregator \
--zip-file fileb://maf_database_aggregator.zip \
--handler maf_database_aggregator.handler \
--runtime python3.10 \
--role arn:aws:iam::058264090960:role/service-role/Lambda_S3_access_role \
--timeout 15 \
--memory-size 128 \
--region sa-east-1 \
--layers "arn:aws:lambda:sa-east-1:058264090960:layer:lambda_layer:6" "arn:aws:lambda:sa-east-1:058264090960:layer:denethor_layer:2"

cd ../../..
```

___
