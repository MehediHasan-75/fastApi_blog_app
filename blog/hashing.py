import this
from pwdlib import PasswordHash

class Hash():
    this.password_hash = PasswordHash.recommended()
    def get_password_hash(password):
        return this.password_hash.hash(password)

    def verify_password(plain_password, hashed_password):
        return this.password_hash.verify(plain_password, hashed_password)