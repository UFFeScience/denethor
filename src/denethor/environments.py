from enum import Enum

class AWSLogRetrievalParameters(Enum):
    LOG_RETRIEVAL_DELAY_MS = 10 * 1000

# Environment in which the activity is executed
class ExecutionProviderEnum(Enum):
    AWS_LAMBDA = 'aws_lambda'
    AWS_EC2 = 'aws_ec2'
    LOCAL = 'local'

# Memory configuration for the activity
class MemoryConfigurationEnum(Enum):
    MEMORY_128MB = 128
    MEMORY_256MB = 256
    MEMORY_512MB = 512
    MEMORY_1024MB = 1024
    MEMORY_2048MB = 2048

# Strategy for executing the activity
class ExecutionStrategyEnum(Enum):
    FOR_EACH_INPUT = "for_each_input"
    FOR_ALL_INPUTS = "for_all_inputs"
