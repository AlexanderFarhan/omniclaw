import subprocess
import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class YubiKeyManager:
    """Manages Challenge-Response via YubiKey for AES key derivation."""
    
    def __init__(self, slot=2):
        self.slot = slot
        
    def get_derived_key(self, challenge: bytes) -> bytes:
        """
        Sends a challenge to the YubiKey and derives an AES-GCM key from the response.
        Requires ykchalresp to be installed.
        """
        try:
            # ykchalresp -[slot] -x [hex_challenge]
            challenge_hex = challenge.hex()
            cmd = ["ykchalresp", f"-{self.slot}", "-x", challenge_hex]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            response_hex = result.stdout.strip()
            
            # Hash the response to ensure it's exactly 32 bytes for AES-256
            hasher = hashlib.sha256()
            hasher.update(bytes.fromhex(response_hex))
            return hasher.digest()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"YubiKey challenge failed. Is the key inserted? Error: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("ykchalresp command not found. Please install yubikey-personalization.")
