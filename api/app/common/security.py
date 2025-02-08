from passlib.hash import bcrypt


def verify_password(plain_password, hashed_password) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return bcrypt.hash(password)
