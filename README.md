## Setup

This project uses `uv` for dependency management and virtual environments.

1. Install uv (if you do not have it):
	- macOS/Linux: https://docs.astral.sh/uv/
	- Windows: https://docs.astral.sh/uv/

2. Create the virtual environment and install dependencies:

```bash
uv venv
uv sync
```

3. Activate the environment (optional if you use `uv run`):

```bash
source .venv/bin/activate
```

## Run

```bash
uv run python main.py
```

## Network Configuration

Before running the app, update your machine's IPv4 address to match the OSA network. Use:

- OSA IPv4 address: `192.168.54.1`
- Subnet mask: `255.255.255.0` (prefix length `/24`)

### Steps (Windows)

1. Open "Settings" -> "Network & Internet" -> your network adapter -> "IP assignment" -> "Edit".
2. Select "Manual", enable IPv4, and set:
	- IP address: `192.168.54.1`
	- Subnet mask: `255.255.255.0`
	- Gateway: leave blank unless your setup requires one
3. Save and verify with:

```powershell
ipconfig
```

### Steps (Linux)

1. Identify the network interface (e.g., `eth0`, `enp0s3`):

```bash
ip addr
```

2. Set the IPv4 address:

```bash
sudo ip addr flush dev <interface>
sudo ip addr add 192.168.54.1/24 dev <interface>
```

3. Verify:

```bash
ip addr show <interface>
```

### Steps (macOS)

1. Identify the network service name (e.g., `Wi-Fi`, `Ethernet`):

```bash
networksetup -listallnetworkservices
```

2. Set the IPv4 address:

```bash
sudo networksetup -setmanual "<service>" 192.168.54.1 255.255.255.0
```

3. Verify:

```bash
ipconfig getifaddr <interface>
```
