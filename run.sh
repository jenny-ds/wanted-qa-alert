#!/bin/bash
# crontab에서 실행되는 래퍼 스크립트
# 환경변수를 .env 파일에서 로드하고 main.py를 실행합니다

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
LOG_FILE="$SCRIPT_DIR/alert.log"

if [ ! -f "$ENV_FILE" ]; then
  echo "$(date): .env 파일이 없습니다 — $ENV_FILE" >> "$LOG_FILE"
  exit 1
fi

# .env 로드
set -a
source "$ENV_FILE"
set +a

cd "$SCRIPT_DIR"
echo "$(date): 실행 시작" >> "$LOG_FILE"
/opt/homebrew/bin/python3.12 main.py >> "$LOG_FILE" 2>&1
echo "$(date): 실행 완료 (exit $?)" >> "$LOG_FILE"
