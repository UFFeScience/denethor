from enum import Enum

class BaseEnum(Enum):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False
    
    def __str__(self):
        return str(self.value)
    
class AWSLogRetrievalParameters(BaseEnum):
    LOG_RETRIEVAL_DELAY_MS = 10 * 1000

# Environment in which the activity is executed
class ExecutionProviderEnum(BaseEnum):
    AWS_LAMBDA = 'aws_lambda'
    AWS_EC2 = 'aws_ec2'
    LOCAL = 'local'

# Memory configuration for the activity
class MemoryConfigurationEnum(BaseEnum):
    MEMORY_128MB = 128
    MEMORY_256MB = 256
    MEMORY_512MB = 512
    MEMORY_1024MB = 1024
    MEMORY_2048MB = 2048

# Strategy for executing the activity
class ExecutionStrategyEnum(BaseEnum):
    FOR_EACH_INPUT = "for_each_input"
    FOR_ALL_INPUTS = "for_all_inputs"
