from datetime import datetime, timezone
import re
import uuid

# Define a regex pattern to match only valid characters in file names or directories
def sanitize(filename):
    return re.sub(r'[^a-zA-Z0-9_\-\./]', '_', filename).replace("LATEST", '')

# Create datetime objects (in UTC) from the timestamps in milliseconds
def to_datetime(time: float):
    if time:
        return datetime.fromtimestamp((time / 1000.0), tz=timezone.utc)
    return None

def parse_int(value: str) -> int:
    if value is None:
        return None
    match = re.search(r"\d+", value)
    value_int = int(match.group()) if match else None
    return value_int

def parse_float(value: str) -> float:
    if value is None:
        return None
    match = re.search(r"\d+\.?\d*", value)
    value_float = float(match.group()) if match else None
    return value_float

def generate_request_id():
    return 'uuid_' + str(uuid.uuid4()).replace('-', '_')