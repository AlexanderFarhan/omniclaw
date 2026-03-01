import platform
import sys
import logging
from pathlib import Path

# Insert OmniClaw path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GenesisLocal")

AUTHORIZED_HARDWARE_NODE = "asus-tuf-hostname" 

def check_hardware_lock():
    current_node = platform.node()
    if current_node != AUTHORIZED_HARDWARE_NODE:
        logger.critical("Genesis Engine halted: Hardware signature mismatch.")
        sys.exit(1)

# Nightly self-refactor framework (Local-only constraint applied)
if __name__ == "__main__":
    check_hardware_lock()
    logger.info("Hardware validation passed. Starting nightly Genesis routine on authorized local hardware.")
