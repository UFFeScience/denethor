## Lambda Functions Preparation

## Create the necessary IAM role
Create a JSON file named lambda_trust_policy. This policy allows the Lambda service to assume the role you are about to create.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```


Create the role named Lambda_S3_access_role using the trust policy file from the previous step.

```bash
aws iam create-role --role-name Lambda_S3_access_role --assume-role-policy-document ../scripts/iam/lambda_trust_policy.json
```


Attach an AWS-managed policy to the role to grant it read and write permissions for S3. We will use AmazonS3FullAccess.

```bash
aws iam attach-role-policy --role-name Lambda_S3_access_role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```



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

cp -R src/lambda/tree_constructor* .lambda/lambda_functions/tree_constructor/

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

cp -R src/lambda/subtree_constructor* .lambda/lambda_functions/subtree_constructor/

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

cp -R src/lambda/maf_database_creator* .lambda/lambda_functions/maf_database_creator/

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

cp -R src/lambda/maf_database_aggregator* .lambda/lambda_functions/maf_database_aggregator/

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
