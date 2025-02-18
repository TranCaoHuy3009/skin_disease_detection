def validate_required_fields(fields_dict):
    """Validate that all required fields have values."""
    return all(value for value in fields_dict.values())

def validate_phone_number(phone):
    """Validate phone number format."""
    # Implement phone validation logic based on your requirements
    # This is a basic example - modify as needed
    return bool(phone and len(phone) >= 10)