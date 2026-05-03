# stats

<div align="center">

**Beautiful terminal server dashboard with real-time charts.**

[![PyPI version](https://img.shields.io/pypi/v/stats-dashboard?color=blue&label=PyPI)](https://pypi.org/project/stats-dashboard/)
[![Python](https://img.shields.io/pypi/pyversions/stats-dashboard?logo=python&logoColor=white)](https://pypi.org/project/stats-dashboard/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTQgNGgxNnYxMkg0eiIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48cGF0aCBkPSJNMSAyMGgyMiIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48L3N2Zz4=)](https://github.com/pepperonas/stats)

[![Linux](https://img.shields.io/badge/Linux-supported-success?logo=linux&logoColor=white)](https://github.com/pepperonas/stats)
[![macOS](https://img.shields.io/badge/macOS-supported-success?logo=apple&logoColor=white)](https://github.com/pepperonas/stats)
[![Windows](https://img.shields.io/badge/Windows-supported-success?logo=windows&logoColor=white)](https://github.com/pepperonas/stats)

[![psutil](https://img.shields.io/badge/psutil-%E2%89%A55.9-orange?logo=python&logoColor=white)](https://github.com/giampaolo/psutil)
[![rich](https://img.shields.io/badge/rich-%E2%89%A513.0-purple?logo=python&logoColor=white)](https://github.com/Textualize/rich)
[![plotext](https://img.shields.io/badge/plotext-%E2%89%A55.2-blue?logo=python&logoColor=white)](https://github.com/piccolomo/plotext)

[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/pepperonas/stats/pulls)
[![GitHub stars](https://img.shields.io/github/stars/pepperonas/stats?style=social)](https://github.com/pepperonas/stats)
[![GitHub issues](https://img.shields.io/github/issues/pepperonas/stats)](https://github.com/pepperonas/stats/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/pepperonas/stats)](https://github.com/pepperonas/stats/commits)

</div>

---

A single-command system dashboard that renders CPU, memory, disk, network, top processes, and live history charts directly in your terminal. No browser, no GUI, no config needed.

```
┌──────────── CPU ─────────────┐ ┌────────── Memory ───────────┐
│   Core 0 ████████░░░░ 42.3%  │ │ RAM used █████████░░░ 56.2% │
│   Core 1 ██████████░░ 81.0%  │ │          8.8G / 15.6G       │
│   Core 2 ███░░░░░░░░░ 12.7%  │ │     Swap ██░░░░░░░░░  8.4% │
│   Core 3 █████████░░░ 71.5%  │ │          0.3G / 4.0G        │
│    Total ███████░░░░░ 51.9%  │ └─────────────────────────────┘
│    Steal ░░░░░░░░░░░░  0.0%  │
└──────────────────────────────┘
┌─────── CPU History (60s) ────┐ ┌──── Network History (60s) ───┐
│ ⡇⠀⡀⠀⢀⡀⠀⣰⣀⠀⡀⠀⢀⣀⣰⡀⠀⣀⠀⡀⣀⣰ │ │ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀ │
│ ⡇⣸⡇⡸⠘⡆⢸⠁⠈⣇⡇⠀⡜⠁⠈⠹⡄⡸⠱⣼⠃⠈⡆ │ │ ⠀⠀⣰⡀⠀⣴⠀⠀⣰⠹⡆⠀⣷⠀⠀⣠⡀⡞⠈⣇ │
│ ⣇⠇⢹⠇⠀⢹⡎⠀⠀⠸⡇⢰⠃⠀⠀⠀⢻⠇⠀⠀⠀⠀⡇ │ │ ⣴⡀⡏⢧⢠⠏⡆⣠⠃⠀⢳⡼⠘⡆⢠⠏⢱⠇⠀⠸⡄ │
│ ⠈⠀⠀⠀⠀⠀⠁⠀⠀⠀⠁⠈⠀⠀⠀⠀⠈⠀⠀⠀⠀⠈ │ │ ⠈⢧⠃⠈⢾⠀⢱⠏⠀⠀⠀⠁⠀⢹⡞⠀⠀⠀⠀⠀⠀ │
└──────────────────────────────┘ └──────────────────────────────┘
┌────────────── Top Processes ─────────────────────────────────┐
│   PID   Name                  CPU%    MEM%      RSS          │
│  1234   node server.js        89.2     3.1     498M          │
│  5678   python scraper.py     45.1     2.4     384M          │
│   890   postgres              12.3     1.8     289M          │
└──────────────────────────────────────────────────────────────┘
```

## Features

- **CPU** — per-core usage bars + total + steal time (Linux)
- **Memory** — RAM & swap with used/total/available
- **Disk** — partition usage bars + read/write throughput
- **Network** — TX/RX throughput + total transferred + connections
- **Top Processes** — sorted by CPU, with color-coded thresholds
- **Live Charts** — CPU & network history as terminal line graphs (last 60s)
- **Cross-Platform** — Linux, macOS, Windows
- **Zero Config** — just install and run

## Installation

### pip (recommended)

```bash
pip install stats-dashboard
```

### pipx (isolated install)

```bash
pipx install stats-dashboard
```

### From source

```bash
git clone https://github.com/pepperonas/stats.git
cd stats
pip install .
```

## Usage

```bash
# Single snapshot
stats

# Live dashboard (updates every second, Ctrl+C to exit)
stats --live

# Live with custom interval
stats --live --interval 3

# Short flags
stats -l -i 2
```

### Options

| Flag | Description |
|------|-------------|
| `-l`, `--live` | Live updating dashboard |
| `-i N`, `--interval N` | Update interval in seconds (default: 1) |
| `-V`, `--version` | Show version |
| `-h`, `--help` | Show help |

## Platform Support

| Feature | Linux | macOS | Windows |
|---------|:-----:|:-----:|:-------:|
| CPU per-core | Yes | Yes | Yes |
| CPU steal time | Yes | — | — |
| Memory & swap | Yes | Yes | Yes |
| Disk usage | Yes | Yes | Yes |
| Disk I/O speed | Yes | Yes | Yes |
| Network throughput | Yes | Yes | Yes |
| Connection count | Yes | Yes | Requires admin |
| Top processes | Yes | Yes | Yes |
| Live charts | Yes | Yes | Yes |
| Load average | Yes | Yes | Yes* |

\* Windows `getloadavg()` requires Python 3.12+

## Requirements

- Python 3.9+
- [psutil](https://github.com/giampaolo/psutil) — cross-platform system metrics
- [rich](https://github.com/Textualize/rich) — terminal formatting
- [plotext](https://github.com/piccolomo/plotext) — terminal plots

## Screenshots

### Snapshot Mode (`stats`)

```
 STATS DASHBOARD   2026-05-03 08:13:36  v1.0.0

 celox (Linux)    Load: 1.94 / 4.95 / 6.52  (4 CPUs)    Up: 2d 9h 50m    Procs: 286

╭──────────────── CPU ────────────────╮ ╭─────────────── Memory ───────────────╮
│       Core 0 ██████████████████░░░░ │ │     RAM used █████████████████░░░░░░ │
│              44.4%                  │ │              35.6%                   │
│       Core 1 ██████████████████████ │ │              5.6G / 15.6G           │
│              100.0%                 │ │                                      │
│       Core 2 ███████████████████░░░ │ │         Swap █████████████░░░░░░░░░░ │
│              68.7%                  │ │              32.7%                   │
│       Core 3 ████████████░░░░░░░░░░ │ │              1.3G / 4.0G            │
│              35.0%                  │ ╰──────────────────────────────────────╯
│        Total ████████████████░░░░░░ │
│              62.3%                  │
│        Steal ░░░░░░░░░░░░░░░░░░░░░░ │
│              0.0%                   │
╰─────────────────────────────────────╯
```

### Live Mode (`stats -l`)

Live mode renders real-time CPU and network history as line charts, auto-updating every second. Press `Ctrl+C` to exit.

## How It Works

`stats` uses [psutil](https://github.com/giampaolo/psutil) to collect system metrics, [rich](https://github.com/Textualize/rich) for terminal rendering with colored panels and tables, and [plotext](https://github.com/piccolomo/plotext) for live line charts. On Linux, CPU steal time is read directly from `/proc/stat`.

## License

[MIT](LICENSE) — Martin Pfeffer

## Author

**Martin Pfeffer**

- Website: [celox.io](https://celox.io)
- GitHub: [@pepperonas](https://github.com/pepperonas)
