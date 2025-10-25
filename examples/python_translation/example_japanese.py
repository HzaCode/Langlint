"""Data processing utility"""


def process_data(data):
    """Process data Argument: Number: Data to be processed Return value: Processed data"""
    # Verify the data
    if not data:
        return None
    
    # Transform data
    result = [x * 2 for x in data]
    return result


def validate_input(value):
    """Validate input value"""
    # Check if value is positive
    if value > 0:
        return True
    return False