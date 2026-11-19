# Environment report — M001.3 (observed 2026-11-19)

Collected with PowerShell diagnostics. No environment variables containing
credentials, API keys or secrets were printed. No system settings were changed.

## Hardware and OS

| Check | Command | Result |
|---|---|---|
| CPU | `Get-CimInstance Win32_Processor` | AMD Ryzen 5 7520U with Radeon Graphics; 4 cores, 8 logical processors |
| Physical RAM | `Win32_OperatingSystem.TotalVisibleMemorySize` | 16,023,164 KB ≈ 15.28 GB |
| Available RAM | `Win32_PerfFormattedData_PerfOS_Memory.AvailableMBytes` | Sample 1: 2,285 MB (2.23 GB); Sample 2: 2,898 MB (2.83 GB) |
| Windows | `Win32_OperatingSystem` | Windows 11 Home Single Language, 10.0.26200, build 26200, 64-bit |
| GPU | `Win32_VideoController` | AMD Radeon(TM) Graphics, driver 32.0.21045.16010, AdapterRAM 536,870,912 bytes (shared). No NVIDIA device. |
| Disk C: | `Win32_LogicalDisk` | 475.3 GB total, 154.85 GB free |
| Port 8080 | `Get-NetTCPConnection -LocalPort 8080` | No listener |

## WSL2 and Docker

| Check | Result (exit code where relevant) |
|---|---|
| `wsl.exe --status` | Default distribution `docker-desktop`, default version 2 |
| `wsl.exe --list --verbose` | `docker-desktop` — **Stopped** |
| `.wslconfig` | Absent (no custom memory allocation) |
| `docker version` | Client 29.9.3, API 1.56, Go 1.26.10, context `desktop-linux`; server connection failed |
| Server error | `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine ... The system cannot find the file specified.` (exit 1) |
| `docker info` | Same connection failure (exit 1) |
| `docker images` | Same connection failure (exit 1) |
| `docker ps -a` | Same connection failure (exit 1) |
| `docker compose version` | v5.7.0 (client-side, works) |
| Docker Desktop process | No `Docker Desktop` / `com.docker.backend` process running |

## Runtimes

| Check | Result |
|---|---|
| Python | 3.13.5; `py --list` shows 3.13, Astral CPython 3.14.4 and 3.12.13 |
| venv | `python -m venv --help` exit 0; pip present at Python313\Scripts\pip.exe |
| Ollama | v0.40.16 at `C:\Users\pc\AppData\Local\Programs\Ollama\ollama.exe` |
| Ollama models | `gemma4:31b-cloud` (cloud, no local size), `gemma3:4b` (3.4 GB), `qwen3.5:4b` (3.3 GB) |

## Network (read-only probes)

| Target | Result |
|---|---|
| `https://superlinked.com/docs/quickstart` | HTTP 200 |
| `https://github.com/superlinked/sie` | HTTP 200 |
| `https://ghcr.io/v2/` | HTTP 405 to HEAD — expected for a registry endpoint; connectivity not proven for a blob pull |

## Conclusion

The Linux Docker engine is not running and available RAM is only 2.23–2.83 GB.
The resource gate in the main report therefore fails on memory and engine
readiness. No image pull or model download was attempted.
