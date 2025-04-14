import secrets
import string

alphabet = (
    string.ascii_letters + string.digits
)  # All upper/lower-case letters and digits
key = "".join(secrets.choice(alphabet) for _ in range(32))
print(key)
