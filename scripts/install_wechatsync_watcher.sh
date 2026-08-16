#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$(command -v python3 || true)"
PLIST="$HOME/Library/LaunchAgents/com.dupontmaster.wechatsync-publisher.plist"
LOG_DIR="$HOME/Library/Logs"
LABEL="com.dupontmaster.wechatsync-publisher"

if [[ -z "$PYTHON_BIN" ]]; then
  echo "未找到 python3，请先安装 Python 3。" >&2
  exit 1
fi

if [[ ! -f "$ROOT/.oss.env" ]]; then
  echo "缺少 $ROOT/.oss.env。请先按 .oss.env.example 填写阿里云 OSS 配置。" >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$HOME/Library/Application Support/DupontMaster"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PYTHON_BIN}</string>
    <string>${ROOT}/scripts/watch_wechatsync_downloads.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${ROOT}</string>
  <key>StartInterval</key>
  <integer>30</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/dupontmaster-wechatsync.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/dupontmaster-wechatsync-error.log</string>
</dict>
</plist>
PLIST

chmod 600 "$PLIST"

# Refresh an existing installation without requiring a reboot/login.
launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

echo "已安装 DupontMaster 文章同步助手发布桥。"
echo "监听目录：$HOME/Downloads"
echo "扫描频率：约 30 秒"
echo "日志：$LOG_DIR/dupontmaster-wechatsync.log"
echo "以后在文章同步助手中勾选『Markdown 压缩包』，下载完成后官网会自动处理并推送 GitHub。"
