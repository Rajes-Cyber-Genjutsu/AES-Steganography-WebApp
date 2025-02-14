import cv2
import os
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

def derive_key(password):
    """Generate a 16-byte AES key from the password."""
    return hashlib.sha256(password.encode()).digest()[:16]

def encrypt_message(message, password):
    """Encrypt the message using AES."""
    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_CBC, iv=b'1234567890123456')  # Fixed IV for simplicity
    encrypted = cipher.encrypt(pad(message.encode(), AES.block_size))
    return encrypted

def convert_to_png(image_path):
    """Convert JPG to PNG if necessary and return the new path."""
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("Error: Image not found!")
        return None

    if image_path.lower().endswith('.png'):
        return image_path  # Already PNG, no need to convert

    new_path = os.path.splitext(image_path)[0] + ".png"
    cv2.imwrite(new_path, img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    print(f"🔄 Converted {image_path} to PNG: {new_path}")
    return new_path

def encode_message(image_path, output_path, message, password):
    """Embed a message into an image using AES + LSB steganography."""
    image_path = convert_to_png(image_path)  # Convert to PNG before encoding
    if image_path is None:
        print("Error: Image conversion failed!")
        return

    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found!")
        return

    encrypted_msg = encrypt_message(message, password)
    message_length = len(encrypted_msg)

    h, w, c = img.shape
    max_bytes = (h * w * 3) // 8

    if message_length > max_bytes:
        print("Error: Message too long for this image!")
        return

    # Convert message length into 4 bytes and embed in the first pixels
    length_bin = format(message_length, '032b')  
    data_bin = ''.join(format(byte, '08b') for byte in encrypted_msg)  

    # Flatten image array for easy bitwise operations
    flat_img = img.flatten().astype(np.int16)  # ✅ Use int16 to avoid overflow issues

    # Embed message length in the first 4 pixels
    for i in range(32):
        flat_img[i] = np.clip((flat_img[i] & ~1) | int(length_bin[i]), 0, 255)  # ✅ Clip values

    # Embed encrypted message data
    for i in range(len(data_bin)):
        flat_img[32 + i] = np.clip((flat_img[32 + i] & ~1) | int(data_bin[i]), 0, 255)  # ✅ Clip values

    # Convert back to uint8 and reshape
    img = flat_img.astype(np.uint8).reshape(h, w, c)
    cv2.imwrite(output_path, img)
    print(f"✅ Message encoded successfully in: {output_path}")
