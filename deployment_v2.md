# OmniClaw v4.1 — Deployment Guide

## Prerequisites

| Component | Desktop (Asus TUF) | Mobile (Poco X3 / Termux) |
|---|---|---|
| **Python** | 3.9+ | via `pkg install python` |
| **Git** | ✓ | via `pkg install git` |
| **ZeroMQ** | `pip install pyzmq` | `pip install pyzmq` |
| **Crypto** | `pip install pycryptodome` | `pip install pycryptodome` |
| **Watchdog** | `pip install watchdog` | `pip install watchdog` |
| **LLM** | Ollama or OpenAI API | Ollama (if resources allow) |
| **eBPF** | `libbpf`, `bpftool`, kernel 5.8+ | ❌ Not supported |
| **Termux:API** | ❌ | `pkg install termux-api` |
| **PM2** | `npm install -g pm2` | Optional |
| **MCP** | `pip install fastmcp` | Optional |

---

## 1. Configuration

### Environment Variables (P2P)

```bash
export NODE_ID="mobile"          # or "desktop"
export PORT="5555"
export PEERS="100.64.1.2:5555"   # Tailscale IP of peer
export AES_KEY="base64encoded32byteskey=="  # Pre-shared key
```

### Config Files

| Module | Config File | Location |
|---|---|---|
| Evolution Agent | `config.yaml` | `modules/evolution/` |
| Scholar | `scholar_config.json` | `modules/scholar/` |
| Scout Agent | `scout_config.yaml` | Project root |
| Hive Sync | `hive_config.yaml` | Project root |
| IPS Agent | `config.example.yaml` → `security.ips` | Project root |

---

## 2. Module Startup

### Desktop (Asus TUF)

```bash
# 1. P2P Node
NODE_ID=desktop PORT=5555 python p2p/p2p_network.py &

# 2. Evolution Agent (self-healing)
python modules/evolution/evolution_agent.py &

# 3. IPS Agent (requires root for live blocking)
sudo python -c "from core.security.ips_agent import IPSAgent; IPSAgent().start()"

# 4. Shadow Shell Honeypot (requires root for iptables)
sudo python modules/security/shadow_shell.py &
sudo python modules/security/iptables_helper.py &

# 5. Startup Autopilot (PM2 monitor)
python modules/startup/saas_manager.py &

# 6. Scholar (daily briefings at 07:00)
python modules/scholar/exam_intelligence.py &

# 7. Scout Agent (on-demand)
python core/scout_agent.py example.com

### 7. Core Services

**Desktop Mode Only:**
- Genesis Evolution Agent: Monitors telemetry and suggests optimizations.

**Mobile Mode Only:**
- Termux Camera: Periodic photo capture and LLM analysis (`modules/vision/termux_camera.py`).
- Plant Monitor: Specific crop/plant monitoring workflow (`modules/sensors/plant_monitor.py`).

# 8. MCP Server (for IDE integration)
python connectors/mcp_host.py &
```

### Mobile (Poco X3 / Termux)

```bash
# 1. P2P Node
NODE_ID=mobile PORT=5555 python p2p/p2p_network.py &

# 2. Plant Monitor (uses Termux camera)
python modules/sensors/plant_monitor.py &

# 3. Evolution Agent (lightweight)
python modules/evolution/evolution_agent.py &

# 4. Scholar (briefings)
python modules/scholar/exam_intelligence.py &
```

---

## 3. Resource Awareness

All modules import `resource_check()` from `core/resource_utils.py`:

```python
from core.resource_utils import resource_check

if resource_check(is_mobile=True):
    # Proceed with heavy operation
```

**Mobile thresholds** (tune in `resource_utils.py`):
- Battery < 20% → abort
- CPU > 70% → abort
- Memory > 80% → abort

Desktop always returns `True`.

---

## 4. Kill Switch

```python
from core.kill_switch import check_kill_switch, activate, deactivate

# Before any autonomous action:
check_kill_switch()  # raises RuntimeError if active

# Toggle via MCP or code:
activate()    # halt everything
deactivate()  # resume
```

The kill switch can also be toggled via the MCP server tool `toggle_kill_switch`.

---

## 5. eBPF Programs

### IPS Monitor

```bash
cd kernel_bridge
make ips        # Builds monitor.bpf.o
sudo make install
```

### Honeypot XDP

```bash
cd modules/security
clang -O2 -target bpf -c honeypot.cpp -o honeypot.bpf.o
sudo ip link set dev eth0 xdp obj honeypot.bpf.o sec xdp
```

---

## 6. MCP Server

Runs on port 8000. External IDEs connect via WebSocket.

**Resources:** `system://cpu`, `system://memory`, `plant://latest_health`, `exam://next_deadline`, `security://kill_switch`

**Tools:** `send_telegram_message`, `trigger_plant_capture`, `toggle_kill_switch`, `get_pm2_status`

---

## 🔒 Secure Enclave & Hardware Authentication (Optional)

OmniClaw supports isolating sensitive operational capabilities and forcing hardware authentication to unlock the framework.

1. **Prerequisites**: You must have `yubikey-personalization` installed and a YubiKey present.
    ```bash
    # Ubuntu/Debian
    sudo apt install yubikey-personalization
    
    # Termux
    pkg install yubikey-personalization
    ```
2. **Setup YubiKey**: Run the setup script to format Slot 2 for HMAC-SHA1 Challenge-Response.
    ```bash
    chmod +x scripts/setup_yubikey.sh
    ./scripts/setup_yubikey.sh
    ```
3. **Hardware Lock**: In `modules/evolution/local_code_janitor.py` and `genesis_local.py`, modify `AUTHORIZED_HARDWARE_NODE` to exactly match the result of `hostname` on your isolated secure machine, guaranteeing evolution logic never leaks.

---

## 7. Directory Structure

```
OmniClaw/
├── core/
│   ├── resource_utils.py        # Resource-awareness helper
│   ├── kill_switch.py           # Global kill flag
│   ├── security/                # IPS Agent, SecurityLayer
│   ├── evolution_agent.py       # Core-level evolution agent
│   ├── hive_sync.py             # Core-level hive sync
│   └── scout_agent.py           # Core-level scout agent
├── connectors/
│   └── mcp_host.py              # MCP server (fastmcp)
├── modules/
│   ├── evolution/               # Self-healing code janitor
│   │   ├── evolution_agent.py
│   │   ├── sandbox.py
│   │   └── config.yaml
│   ├── security/                # eBPF honeypot + shadow shell
│   │   ├── honeypot.cpp
│   │   ├── shadow_shell.py
│   │   └── iptables_helper.py
│   ├── scholar/                 # Exam War-Room
│   │   ├── exam_intelligence.py
│   │   └── scholar_config.json
│   ├── startup/                 # DevOps autopilot
│   │   └── saas_manager.py
│   └── sensors/                 # Bio-guardian
│       └── plant_monitor.py
├── p2p/
│   ├── crypto.py                # AES-256 helpers
│   └── peers.json               # Known peer list
├── kernel_bridge/               # eBPF + C++ bridge
├── logs/
├── tests/
└── deployment_v2.md
```

---

## 8. Security Notes

- Keep the AES key **secret**. Distribute via env vars or secure vault.
- eBPF programs require **root**. Run in controlled environments.
- The scout agent **never exploits** — advisory only.
- Shadow shell logs are in `logs/honeypot/`.
- Kill switch halts **all** autonomous shell execution.

---

## 9. Troubleshooting

| Issue | Solution |
|---|---|
| Module crashes | `evolution_agent` will detect and attempt self-heal |
| P2P connection fails | Check Tailscale connectivity, verify `PEERS` env var |
| eBPF load fails | Ensure kernel 5.8+, `libbpf` installed, running as root |
| LLM timeout | Verify Ollama is running: `ollama list` |
| PM2 not found | Install: `npm install -g pm2` |
| Kill switch stuck | Call `core.kill_switch.deactivate()` or MCP tool |
