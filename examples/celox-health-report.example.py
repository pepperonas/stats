#!/usr/bin/env python3
"""
health-report — Automated server health report with PDF + email.

Collects system metrics, evaluates thresholds, generates a Markdown report,
converts to PDF (requires mrxdown or similar md-to-pdf tool), and sends
it via SMTP.

Setup:
  1. Copy this file and fill in your SMTP credentials
  2. Install dependencies: pip install psutil
  3. Make sure mrxdown (or your md-to-pdf tool) is available in PATH
  4. Schedule via cron or systemd timer

Example systemd timer (every 12 hours at 06:00 and 18:00):

  # /etc/systemd/system/health-report.service
  [Unit]
  Description=Server Health Report
  After=network-online.target

  [Service]
  Type=oneshot
  ExecStart=/usr/local/bin/health-report
  TimeoutStartSec=120

  # /etc/systemd/system/health-report.timer
  [Unit]
  Description=Run Health Report every 12 hours

  [Timer]
  OnCalendar=*-*-* 06,18:00:00
  Persistent=true

  [Install]
  WantedBy=timers.target

Then: systemctl enable --now health-report.timer
"""

import subprocess
import smtplib
import ssl
import time
import platform
import psutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path

# ──────────────────────────────────────────────
# CONFIGURE THESE
# ──────────────────────────────────────────────
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 465
SMTP_USER = "you@example.com"
SMTP_PASS = "your-app-password"          # use env var in production!
MAIL_TO = "recipient@example.com"
PDF_TOOL = "mrxdown"                      # md-to-pdf CLI command
REPORT_DIR = Path("/tmp")
# ──────────────────────────────────────────────

HOSTNAME = platform.node()

THRESHOLDS = {
    "cpu_warn": 80, "cpu_crit": 95,
    "steal_warn": 5, "steal_crit": 20,
    "ram_warn": 85, "ram_crit": 95,
    "swap_warn": 50, "swap_crit": 80,
    "disk_warn": 80, "disk_crit": 90,
    "load_warn_factor": 2, "load_crit_factor": 4,
}


def rate(value, warn, crit):
    if value >= crit:
        return "CRITICAL", "🔴"
    elif value >= warn:
        return "WARNING", "🟡"
    return "OK", "🟢"


def get_steal():
    try:
        with open("/proc/stat") as f:
            parts = f.readline().split()
        total = sum(int(x) for x in parts[1:])
        steal = int(parts[8])
        return (steal / total * 100) if total > 0 else 0
    except Exception:
        return 0


def get_sar_summary():
    lines = []
    try:
        result = subprocess.run(
            ["sar", "-u", "ALL"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data_lines = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 12 and parts[1] == "all" and parts[0][0].isdigit():
                    try:
                        t = parts[0]
                        usr = float(parts[2])
                        sys_ = float(parts[4])
                        steal = float(parts[6])
                        idle = float(parts[11])
                        data_lines.append((t, usr, sys_, steal, idle))
                    except (ValueError, IndexError):
                        continue
            if data_lines:
                steals = [d[3] for d in data_lines]
                cpus = [d[1] + d[2] for d in data_lines]
                lines.append("| Metric | Min | Max | Avg |")
                lines.append("|--------|-----|-----|-----|")
                lines.append(f"| CPU (usr+sys) | {min(cpus):.1f}% | {max(cpus):.1f}% | {sum(cpus)/len(cpus):.1f}% |")
                lines.append(f"| Steal | {min(steals):.1f}% | {max(steals):.1f}% | {sum(steals)/len(steals):.1f}% |")
                high_steal = [d for d in data_lines if d[3] > 5]
                if high_steal:
                    lines.append(f"\n**Steal > 5% in {len(high_steal)}/{len(data_lines)} intervals.**")
    except Exception as e:
        lines.append(f"SAR data unavailable: {e}")
    return "\n".join(lines) if lines else "No SAR data available."


def get_top_processes(n=10):
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
        try:
            info = p.info
            if info['cpu_percent'] is not None and info['cpu_percent'] > 0:
                procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    lines = ["| PID | Name | CPU% | MEM% | RSS |", "|-----|------|------|------|-----|"]
    for p in procs[:n]:
        rss = p['memory_info'].rss / 1024**2 if p['memory_info'] else 0
        lines.append(f"| {p['pid']} | {(p['name'] or '?')[:30]} | {p['cpu_percent']:.1f}% | {p['memory_percent']:.1f}% | {rss:.0f} MB |")
    return "\n".join(lines)


def get_docker_stats():
    try:
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format",
             "| {{.Name}} | {{.CPUPerc}} | {{.MemUsage}} | {{.MemPerc}} |"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = ["| Container | CPU% | Memory | MEM% |", "|-----------|------|--------|------|"]
            lines.extend(result.stdout.strip().splitlines())
            return "\n".join(lines)
    except Exception:
        pass
    return "No Docker containers running."


def build_report():
    now = datetime.now()

    psutil.cpu_percent()
    time.sleep(1)
    cpu_total = psutil.cpu_percent()
    cpu_per = psutil.cpu_percent(percpu=True)
    cpu_status, cpu_icon = rate(cpu_total, THRESHOLDS["cpu_warn"], THRESHOLDS["cpu_crit"])

    steal = get_steal()
    steal_status, steal_icon = rate(steal, THRESHOLDS["steal_warn"], THRESHOLDS["steal_crit"])

    load1, load5, load15 = psutil.getloadavg()
    ncpu = psutil.cpu_count()
    if load1 > ncpu * THRESHOLDS["load_crit_factor"]:
        load_status, load_icon = "CRITICAL", "🔴"
    elif load1 > ncpu * THRESHOLDS["load_warn_factor"]:
        load_status, load_icon = "WARNING", "🟡"
    else:
        load_status, load_icon = "OK", "🟢"

    mem = psutil.virtual_memory()
    mem_status, mem_icon = rate(mem.percent, THRESHOLDS["ram_warn"], THRESHOLDS["ram_crit"])

    swap = psutil.swap_memory()
    swap_status, swap_icon = rate(swap.percent, THRESHOLDS["swap_warn"], THRESHOLDS["swap_crit"])

    disk = psutil.disk_usage("/")
    disk_status, disk_icon = rate(disk.percent, THRESHOLDS["disk_warn"], THRESHOLDS["disk_crit"])

    boot = psutil.boot_time()
    uptime_s = time.time() - boot
    days = int(uptime_s // 86400)
    hours = int((uptime_s % 86400) // 3600)

    net = psutil.net_io_counters()

    checks = [
        ("CPU", cpu_status, cpu_icon, f"{cpu_total:.1f}%"),
        ("Steal", steal_status, steal_icon, f"{steal:.1f}%"),
        ("Load", load_status, load_icon, f"{load1:.2f} ({ncpu} CPUs)"),
        ("RAM", mem_status, mem_icon, f"{mem.percent:.1f}%"),
        ("Swap", swap_status, swap_icon, f"{swap.percent:.1f}%"),
        ("Disk /", disk_status, disk_icon, f"{disk.percent:.1f}%"),
    ]

    alerts = [f"- {icon} **{name}**: {val} ({status})"
              for name, status, icon, val in checks if status != "OK"]

    statuses = [c[1] for c in checks]
    if "CRITICAL" in statuses:
        overall, overall_icon = "CRITICAL", "🔴"
    elif "WARNING" in statuses:
        overall, overall_icon = "WARNING", "🟡"
    else:
        overall, overall_icon = "OK", "🟢"

    sar_summary = get_sar_summary()
    top_procs = get_top_processes()
    docker = get_docker_stats()

    md = f"""---
title: "Health Report — {HOSTNAME}"
subtitle: "Server Status ({now.strftime('%d.%m.%Y %H:%M')})"
date: "{now.strftime('%B %d, %Y %H:%M')}"
---

# Health Report — {HOSTNAME}

**Date:** {now.strftime('%Y-%m-%d %H:%M')}
**Uptime:** {days}d {hours}h
**OS:** {platform.system()} {platform.release()}
**CPUs:** {ncpu}

---

## Overall: {overall_icon} {overall}

| Area | Status | Value | Threshold (Warn / Crit) |
|------|--------|-------|-------------------------|
| CPU | {cpu_icon} {cpu_status} | {cpu_total:.1f}% | {THRESHOLDS['cpu_warn']}% / {THRESHOLDS['cpu_crit']}% |
| Steal | {steal_icon} {steal_status} | {steal:.1f}% | {THRESHOLDS['steal_warn']}% / {THRESHOLDS['steal_crit']}% |
| Load | {load_icon} {load_status} | {load1:.2f} / {load5:.2f} / {load15:.2f} | >{ncpu*THRESHOLDS['load_warn_factor']} / >{ncpu*THRESHOLDS['load_crit_factor']} |
| RAM | {mem_icon} {mem_status} | {mem.percent:.1f}% ({mem.used/1024**3:.1f}G / {mem.total/1024**3:.1f}G) | {THRESHOLDS['ram_warn']}% / {THRESHOLDS['ram_crit']}% |
| Swap | {swap_icon} {swap_status} | {swap.percent:.1f}% ({swap.used/1024**3:.1f}G / {swap.total/1024**3:.1f}G) | {THRESHOLDS['swap_warn']}% / {THRESHOLDS['swap_crit']}% |
| Disk / | {disk_icon} {disk_status} | {disk.percent:.1f}% ({disk.used/1024**3:.0f}G / {disk.total/1024**3:.0f}G) | {THRESHOLDS['disk_warn']}% / {THRESHOLDS['disk_crit']}% |

"""

    if alerts:
        md += "## Alerts\\n\\n" + "\\n".join(alerts) + "\\n\\n"

    md += f"""## CPU per Core

| Core | Usage |
|------|-------|
"""
    for i, p in enumerate(cpu_per):
        _, icon = rate(p, THRESHOLDS["cpu_warn"], THRESHOLDS["cpu_crit"])
        md += f"| Core {i} | {icon} {p:.1f}% |\\n"

    md += f"""
## SAR Trend (today)

{sar_summary}

## Network

| Metric | Value |
|--------|-------|
| TX total | {net.bytes_sent / 1024**3:.2f} GB |
| RX total | {net.bytes_recv / 1024**3:.2f} GB |

## Top Processes (by CPU)

{top_procs}

## Docker Containers

{docker}

---

*Auto-generated on {now.strftime('%Y-%m-%d %H:%M')} on {HOSTNAME}.*
"""

    return md, overall, overall_icon


def generate_pdf(markdown_text):
    md_path = REPORT_DIR / f"health-report-{HOSTNAME}.md"
    pdf_path = REPORT_DIR / f"health-report-{HOSTNAME}.pdf"
    md_path.write_text(markdown_text, encoding="utf-8")
    subprocess.run([PDF_TOOL, str(md_path)], capture_output=True, text=True, timeout=30, check=True)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not created: {pdf_path}")
    return pdf_path


def send_email(pdf_path, overall, overall_icon):
    now = datetime.now()
    prefix = {"CRITICAL": "[CRITICAL] ", "WARNING": "[WARNING] "}.get(overall, "")
    subject = f"{prefix}Health Report {HOSTNAME} — {now.strftime('%Y-%m-%d %H:%M')}"

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(
        f"{overall_icon} Server {HOSTNAME} — Status: {overall}\n\n"
        f"Automated health report from {now.strftime('%Y-%m-%d %H:%M')}.\nSee attached PDF.\n",
        "plain", "utf-8"
    ))

    with open(pdf_path, "rb") as f:
        pdf = MIMEApplication(f.read(), _subtype="pdf")
        pdf.add_header("Content-Disposition", "attachment",
                       filename=f"health-report-{HOSTNAME}-{now.strftime('%Y%m%d-%H%M')}.pdf")
        msg.attach(pdf)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print(f"[{now.isoformat()}] Email sent: {subject}")


def main():
    print(f"[{datetime.now().isoformat()}] Generating health report...")
    psutil.cpu_percent(percpu=True)
    for p in psutil.process_iter(['cpu_percent']):
        try:
            p.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    time.sleep(2)

    md, overall, overall_icon = build_report()
    pdf_path = generate_pdf(md)
    print(f"[{datetime.now().isoformat()}] PDF: {pdf_path}")
    send_email(pdf_path, overall, overall_icon)
    print(f"[{datetime.now().isoformat()}] Done.")


if __name__ == "__main__":
    main()
