from config import AUTH_CREDENTIALS

def verify_credentials(username: str, password: str) -> bool:
    """
    Verify user credentials against the configured admin account.
    
    Args:
        username (str): The username to verify
        password (str): The password to verify
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    return (
        username == AUTH_CREDENTIALS["username"] and 
        password == AUTH_CREDENTIALS["password"]
    )