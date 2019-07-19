import hashlib
import string
import random


def create_session(username, password):
    alphabet = "".join([string.ascii_letters + string.digits])
    salt = "".join([random.choice(alphabet) for _ in range(16)])
    sid = f"{salt}{username}{password}"
    sid_hash = hashlib.sha256(sid.encode()).hexdigest()
    return f"{salt}.{sid_hash}"


def verify_session(sid: str, users):
    salt, sid_hash = sid.split(".", 1)
    for username, password in users:
        sid = f"{salt}{username}{password}"
        expected_sid_hash = hashlib.sha256(sid.encode()).hexdigest()
        if sid_hash == expected_sid_hash:
            return username
