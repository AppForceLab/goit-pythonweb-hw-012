from passlib.context import CryptContext

# Configure PassLib for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plaintext password matches a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Create a password hash from plaintext password
    """
    return pwd_context.hash(password) 