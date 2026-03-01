import platform
import sys
import logging
from pathlib import Path

# Insert OmniClaw path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LocalJanitor")

# The only machine allowed to run the evolution and refactoring logic.
# Update this to match your Asus TUF hostname or a specific MAC address hash.
AUTHORIZED_HARDWARE_NODE = "asus-tuf-hostname" 

def check_hardware_lock():
    """Ensures this sensitive automation only runs on authorized local hardware."""
    current_node = platform.node()
    if current_node != AUTHORIZED_HARDWARE_NODE:
        logger.critical(f"HARDWARE LOCKOUT: This agent is restricted to '{AUTHORIZED_HARDWARE_NODE}'. Current node: '{current_node}'")
        sys.exit(1)

class LocalCodeJanitor:
    def __init__(self):
        check_hardware_lock()
        logger.info("Hardware lock verified. Local Code Janitor initializing.")
        
    def run(self):
        logger.info("Running localized self-healing processes...")
        # Self-healing logic remains locally isolated

if __name__ == "__main__":
    agent = LocalCodeJanitor()
    agent.run()
