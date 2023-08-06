import base64
import hashlib

from argon2 import PasswordHasher
from cryptography.fernet import Fernet


def encrypt(password):
    ph = PasswordHasher()
    hash = ph.hash(password)
    db_hash = hash[31:]

    return db_hash


def decrypt(db_hash, password):
    base = "$argon2id$v=19$m=65536,t=3,p=4$"
    ph = PasswordHasher()
    try:
        ph.verify(base + db_hash, password)
        return True
    except:
        return False


def encrypt2(user, master, password):
    key = hashlib.pbkdf2_hmac(
        "sha256", master.encode(), user.encode(), iterations=10
    )
    key = base64.urlsafe_b64encode(key)
    fernet = Fernet(key)
    db_ready = fernet.encrypt(password.encode()).decode()
    return db_ready


def decrypt2(user, master, password):
    key = hashlib.pbkdf2_hmac(
        "sha256", master.encode(), user.encode(), iterations=10
    )
    key = base64.urlsafe_b64encode(key)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(password.encode()).decode()
    return decrypted


if __name__ == "__main__":
    hash = encrypt("senha")
    if decrypt(hash, "asdasdas"):
        print("sucesso")
    else:
        print("falha")
