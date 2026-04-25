#!/bin/bash
# WSL 側から手軽に BurntToast を呼び出すラッパー
# 使用例: win-notify.sh success "完了" "タスク終了"

EMOTION="${1:-info}"
TITLE="${2:-Notification}"
MESSAGE="${3:-}"

# PYTHONPATH を設定してスキルを呼び出し
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

PYTHONPATH="$PROJECT_ROOT" python3 -c "
from skills.burnt_toast_skill import BurntToastSkill
s = BurntToastSkill('$PROJECT_ROOT/skills/burnt_toast_config.json')
s.send('$EMOTION', '$TITLE', '''$MESSAGE''')
"
