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