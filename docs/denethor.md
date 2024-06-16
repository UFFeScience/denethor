# Denethor System

`Denethor` is composed of a set of tools and scripts that allow the execution of workflows in cloud computing environments. It enables the control of workflow execution and the collection of execution and provenance statistics.

## `workflow_executor.py`

The `workflow_executor.py` is a script composed of a series of steps and functions that orchestrates the execution of the project. It relies on both parameters defined in the `json` configuration files and runtime parameters to perform the execution of each step.

### `workflow_steps.json`

The `workflow_steps.json` file contains the workflow steps to be executed, represented by the `steps` list. Each object within `steps` contains:

- `name`: The name of the step.
- `module`: The Python module that contains the function to be executed in this step.
- `handler`: The name of the function to be executed in this step.
- `active`: A boolean indicating whether the step is active or not. If `active` is `False`, the step will be ignored during the workflow execution.
- `params`: An object that contains specific parameters required for the step execution.

The parameters vary depending on the step, but may include:

- `bucket`: The name of the AWS S3 bucket for file upload/download.
- `key`: The key of the file to be accessed in the AWS S3 bucket.
- `function_name`: The name of the AWS Lambda function to be invoked.
- `input_bucket`: The name of the AWS S3 bucket from which input files will be read.
- `input_key`: The key of the input file to be read from the AWS S3 bucket, if applicable.
- `output_bucket`: The name of the AWS S3 bucket where output files will be written.
- `output_key`: The key of the output file to be written to the AWS S3 bucket, if applicable.
- `execution_strategy`: The execution strategy for the AWS Lambda function. It can be *for_each_input* or *for_all_inputs*.

### `workflow_conf.json`

The `workflow_conf.json` file contains information about the workflow, the activities that compose it, and the statistics to be collected. The file consists of a main `workflow` object that contains:

- `workflow_name`: The name of the workflow.
- `workflow_description`: The description of the workflow.
- `input_files`: An object that contains information about the input files for the workflow.
  - `json_file`: The path to the input JSON file.
  - `limit`: The maximum number of input files to be processed.
- `activities`: A list of activities that compose the workflow. Each activity is an object that contains:
  - `activity_name`: The name of the activity.
  - `activity_description`: The description of the activity.
  - `provider_name`: The name of the service provider where the activity will be executed.
  - `custom_statistics`: An object that contains the custom statistics to be collected for the activity. Each statistic contains:
    - `searchKey`: The key to be searched in the logs to collect the statistic.
    - `fieldName`: The name of the field in the database where the statistic will be stored.
    - `dataType`: The data type of the statistic.
    - `description`: *(optional)* The description of the statistic.
    - `separator`: *(optional)* The separator to be used when parsing the logs for that search key.
- `default_separator`: The default separator to be used when parsing the logs, if a specific one is not provided in the statistic definition.
- `general_statistics`: An object that contains the general statistics to be collected for the workflow. The attributes are similar to those of the custom statistics described above, but they are collected for the entire workflow, not just for individual activities.

### `provider_conf.json`

The `provider_conf.json` file contains information about the service providers used to execute activities in a workflow. This information is used to determine the resources that will be allocated for each executed activity. Each provider is represented by an object within the `providers` array:

- `provider_name`: The name of the service provider. In the provided example, the providers are different versions of AWS Lambda, differentiated by the maximum allowed execution time (in seconds).
- `provider_ram`: The amount of RAM allocated in the service provider, in megabytes.
- `provider_timeout`: The maximum allowed execution time for the activity (lambda function) in the service provider, in seconds.
- `provider_cpu`: The number of CPU units allocated in the service provider.
- `provider_storage_mb`: The amount of storage allocated in the service provider, in megabytes.

## Steps for Workflow Execution and Statistics Extraction

As defined in the `workflow_steps.json` file, the workflow consists of 7 steps:

1. **Upload files to AWS S3**: This step performs the upload of files to the specified AWS S3 bucket. The "key" parameter is not specified, indicating that the files will be uploaded directly to the root of the bucket.

2. **Invoke function execution (tree_constructor)**: This step invokes the "tree_constructor" AWS Lambda function. The function reads files from the input bucket and writes the output to the output bucket. The execution strategy is "for_each_input", causing the function to be invoked separately for each input file.

3. **Monitor function execution (tree_constructor)**: This step monitors the execution of the "tree_constructor" AWS Lambda function. By using the generated request IDs from the previous step, it is possible to monitor the status of each function call.

4. **Invoke function execution (subtree_mining)**: This step invokes the "subtree_mining" AWS Lambda function. The function reads files from the input bucket and writes the output to the output bucket. The execution strategy is "for_all_inputs", causing the function to be invoked only once for the entire set of input files.

5. **Monitor function execution (subtree_mining)**: This step monitors the execution of the "subtree_mining" AWS Lambda function. By using the generated request IDs from the previous step, it is possible to monitor the status of each function call.

6. **Download produced files from AWS S3**: This step performs the download of files produced from the specified AWS S3 bucket. The files are downloaded to the path indicated in "downloadPath".

7. **Import Provenance from AWS CloudWatch Logs**: This step imports provenance data and other execution statistics from the function logs stored in AWS CloudWatch. The logs are saved in separate files for each function ("tree_constructor" and "subtree_mining") in the path indicated in "logPath". Additionally, the collected statistics are saved in a relational database, allowing for analysis and visualization of the data.
