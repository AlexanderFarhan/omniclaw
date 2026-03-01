#!/usr/bin/env bash
# Requirements: sudo apt install yubikey-personalization
set -e

echo "Setting up YubiKey Challenge-Response on Slot 2..."
echo "WARNING: This will overwrite any existing configuration on Slot 2!"
read -p "Press Enter to continue or Ctrl+C to abort..."

# Program slot 2 for HMAC-SHA1 challenge-response, generate a random secret key, and require touch
ykpersonalize -2 -ochal-resp -ochal-hmac -ohmac-lt64 -oserial-api-visible

echo "YubiKey is formatted for OmniClaw hardware authentication."
echo "You can now use core/security/yubikey_manager.py to derive keys."
