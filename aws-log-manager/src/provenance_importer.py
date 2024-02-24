import aws_log_retriever as retriever
import aws_log_analyzer as analyzer

def import_provenance_from_aws(params):
    print('Importing provenance from AWS')

    retriever.retrieve_logs_from_aws(params)

    analyzer.analyze_logs(params)