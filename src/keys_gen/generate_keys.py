import sys
import json
import base64
import hashlib
import secrets

# Constants
BLOCK_SIZE = 64       # Block size for HMAC (SHA256 uses 64 bytes)
KEY_SIZE = 64         # Secret key length (64 bytes)
KEK_SIZE = 32         # KEK total length (32 bytes → two 16-byte halves)

# === Utility functions ===

def pad_key(secret: bytes) -> bytes:
    """Ensure key is 64 bytes by right-padding with zeros."""
    return secret.ljust(BLOCK_SIZE, b'\x00')[:BLOCK_SIZE]

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))

def base64_encode(b: bytes) -> str:
    return base64.b64encode(b).decode()

# === Step 1: Generate Challenge Key ===
def generate_challenge_key(length: int = 32) -> bytes:
    return secrets.token_bytes(length)

# === Step 2: Generate Secret ===
def generate_secret(length: int = KEY_SIZE) -> bytes:
    return secrets.token_bytes(length)

# === Step 3: Generate KEK Seed halves ===
def generate_kek_seed_pair(length: int = KEK_SIZE) -> tuple[bytes, bytes]:
    full_kek = secrets.token_bytes(length)
    return full_kek[:length//2], full_kek[length//2:]

# === Step 4: Generate HMAC(ipad/opad + challenge) ===
def derive_ipad_opad(secret: bytes) -> tuple[bytes, bytes]:
    padded = pad_key(secret)
    ipad = xor_bytes(padded, b'\x36' * BLOCK_SIZE)
    opad = xor_bytes(padded, b'\x5c' * BLOCK_SIZE)
    return ipad, opad

def hmac_sha256(ipad: bytes, opad: bytes, message: bytes) -> bytes:
    inner = hashlib.sha256(ipad + message).digest()
    return hashlib.sha256(opad + inner).digest()

# === Step 5: Encrypt Secret (project_ipad/project_opad) with KEK using ARC4 ===
def encrypt_secret(secret: bytes, kek: bytes) -> tuple[bytes, bytes]:
    """Simulate RC4-like encryption of project_ipad and project_opad."""
    from Crypto.Cipher import ARC4
    key_padded = pad_key(secret)
    project_ipad = xor_bytes(key_padded, b'\x36' * BLOCK_SIZE)
    project_opad = xor_bytes(key_padded, b'\x5c' * BLOCK_SIZE)

    rc4 = ARC4.new(kek)
    encrypted_ipad = rc4.encrypt(project_ipad)

    rc4 = ARC4.new(kek)
    encrypted_opad = rc4.encrypt(project_opad)

    return encrypted_ipad, encrypted_opad

# === Main Generator Logic ===

def main():
    challenge = generate_challenge_key()
    secret = generate_secret()
    kek1, kek2 = generate_kek_seed_pair()
    full_kek = kek1 + kek2

    ipad, opad = derive_ipad_opad(secret)
    response = hmac_sha256(ipad, opad, challenge)
    encrypted_ipad, encrypted_opad = encrypt_secret(secret, full_kek)

    output = {
        "challenge": base64_encode(challenge),
        "secret": base64_encode(secret),
        "kek_seed_half1": base64_encode(kek1),
        "kek_seed_half2": base64_encode(kek2),
        "encrypted_ipad": base64_encode(encrypted_ipad),
        "encrypted_opad": base64_encode(encrypted_opad),
        "response": base64_encode(response),
    }

    output_path = sys.argv[1] if len(sys.argv) > 1 else "generated_keys.json"

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Keys generated and saved to '{output_path}'")

if __name__ == "__main__":
    main()
