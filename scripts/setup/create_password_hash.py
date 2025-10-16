#!/usr/bin/env python3
"""
Create proper mosquitto password hash for authentication
Generates SHA512 salted hashes compatible with mosquitto_passwd
"""
import hashlib
import base64
import secrets
import sys

def create_mosquitto_hash(username, password):
    """Create mosquitto-compatible password hash"""
    # Generate random salt (12 bytes)
    salt = secrets.token_bytes(12)
    salt_b64 = base64.b64encode(salt).decode('ascii')

    # Create SHA512 hash with salt
    hash_input = password.encode('utf-8') + salt
    password_hash = hashlib.sha512(hash_input).digest()
    hash_b64 = base64.b64encode(password_hash).decode('ascii')

    # Format: username:$7$salt$hash (Mosquitto v2.0+ format)
    return f"{username}:$7${salt_b64}${hash_b64}"

def main():
    print("Mosquitto Password Hash Generator")
    print("=================================")

    # Create hashes for ATI user
    ati_hash = create_mosquitto_hash("ati_user", "ati_password_123")
    admin_hash = create_mosquitto_hash("admin", "admin_password_456")

    print("\nGenerated password hashes:")
    print(ati_hash)
    print(admin_hash)

    # Write to password file
    with open('render-config/passwd', 'w') as f:
        f.write(ati_hash + '\n')
        f.write(admin_hash + '\n')

    print("\nPassword file updated: render-config/passwd")
    print("\nCredentials for ATI:")
    print("Username: ati_user")
    print("Password: ati_password_123")
    print("\nCredentials for Admin:")
    print("Username: admin")
    print("Password: admin_password_456")

if __name__ == "__main__":
    main()