import os
import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from core.security.yubikey_manager import YubiKeyManager

class SecureConfigLoader:
    """Loads and decrypts sensitive configuration files using a hardware key."""
    
    def __init__(self, challenge_phrase: str = "omniclaw-secure-enclave"):
        self.challenge = challenge_phrase.encode()
        self.yk = YubiKeyManager()
        
    def decrypt_config(self, encrypted_file_path: Path) -> dict:
        """Decrypts a .json.aes or .yaml.aes file into a usable dictionary."""
        if not encrypted_file_path.exists():
            raise FileNotFoundError(f"Config file {encrypted_file_path} not found.")
            
        with open(encrypted_file_path, "rb") as f:
            data = f.read()
            
        nonce = data[:12]
        ciphertext = data[12:]
        
        # Require physical hardware key presence to derive the decryption key
        aes_key = self.yk.get_derived_key(self.challenge)
        aesgcm = AESGCM(aes_key)
        
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(plaintext.decode())
        except Exception as e:
            raise RuntimeError("Decryption failed. Invalid YubiKey or corrupted config.") from e
            
    def encrypt_config(self, plain_dict: dict, output_path: Path):
        """Encrypts a dictionary to a secure file using the hardware key."""
        aes_key = self.yk.get_derived_key(self.challenge)
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)
        plaintext = json.dumps(plain_dict).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        with open(output_path, "wb") as f:
            f.write(nonce + ciphertext)
