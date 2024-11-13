from cryptography.fernet import Fernet

# Generate a valid Fernet key
key = Fernet.generate_key()

# Print the generated key
print(key)
