import cv2
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

def derive_key(password):
    """Generate a 16-byte AES key from the password."""
    return hashlib.sha256(password.encode()).digest()[:16]

def decrypt_message(encrypted_message, password):
    """Decrypt the message using AES."""
    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_CBC, iv=b'1234567890123456')  # Fixed IV (same as encryption)
    decrypted = unpad(cipher.decrypt(encrypted_message), AES.block_size)
    return decrypted.decode()

def decode_message(image_path, password):
    """Extract and decrypt a hidden message from an image using AES + LSB steganography."""
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Could not read the image!")
        return None

    flat_img = img.flatten()

    # Extract message length from first 4 pixels
    length_bin = ''.join(str(flat_img[i] & 1) for i in range(32))
    message_length = int(length_bin, 2)

    # Extract encrypted message bits
    data_bin = ''.join(str(flat_img[32 + i] & 1) for i in range(message_length * 8))

    # Convert bits to bytes
    encrypted_message = bytes(int(data_bin[i:i+8], 2) for i in range(0, len(data_bin), 8))

    try:
        # Decrypt the message
        decrypted_message = decrypt_message(encrypted_message, password)
        return decrypted_message
    except Exception:
        print("Incorrect password or corrupted message!")
        return None  # Return None if decryption fails
