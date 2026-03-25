# Repository Domains

This repository intentionally keeps four operational domains in a single codebase.

## 1) Denethor (provenance and instance generation from real executions)
- Purpose: capture execution metrics/provenance and generate real instance files.
- Main paths:
- `src/denethor/`
- `src/run_workflow_on_aws_lambda.py`
- `src/run_workflow_on_aws_ec2_or_local.py`
- `src/instance_modeling/generate_instance_file_from_weid.py`
- SQL basis: `scripts/sql/instance_generator/`

## 2) Workflow scientific example (Lambda/Local/VM)
- Purpose: executable scientific workflow used as workload and metric source.
- Main paths:
- `src/lambda/`
- `conf/workflow_steps.json`
- `conf/workflow_steps_ec2.json`

## 3) file_metrics utility
- Purpose: small utility for file transfer time measurements (upload/download).
- Main path:
- `src/file_metrics/`

## 4) Synthetic instance generator and validation
- Purpose: generate synthetic instances, parse instance files, validate consistency, and support cost analysis.
- Main paths:
- `src/instance_modeling/synthetic/`
- `src/instance_modeling/instance_io.py`
- `src/instance_modeling/validate_instance_file.py`
- `src/instance_modeling/instance_cost_analysis.py`

## Why all in one repository?
Operationally, these four domains depend on each other in the same execution and data lifecycle:
workflow execution -> metrics/provenance capture -> instance generation -> synthetic/real validation and analysis.
