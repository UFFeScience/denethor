import aws_log_retriever as retriever
import aws_log_interpreter as interpreter

def import_provenance_from_aws(params):
    print('Importing provenance from AWS')

    retriever.retrieve_logs_from_aws(params)

    interpreter.analyze_logs(params)