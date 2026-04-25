import time
import subprocess
import sys
import os
from skills.burnt_toast_skill import BurntToastSkill

def verify_notification_in_history(title_fragment):
    """
    Windows Runtime API を使用して通知履歴をクエリする。
    AppID が指定されていない場合は、すべての履歴をスキャンする。
    """
    # PowerShellスクリプト: 通知履歴を取得し、XMLの中身をチェックする
    # 注意: Windows 10/11 のバージョンによっては履歴取得に制限がある場合があります
    check_script = f"""
    try {{
        $Type = [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
        $History = [Windows.UI.Notifications.ToastNotificationManager]::History.GetHistory()
        if ($History.Count -eq 0) {{
            return "EMPTY"
        }}
        $match = $History | Where-Object {{ $_.Content.GetXml() -like "*{title_fragment}*" }}
        if ($match) {{
            return "FOUND"
        }} else {{
            return "NOT_FOUND"
        }}
    }} catch {{
        return "ERROR: $($_.Exception.Message)"
    }}
    """
    
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; " + check_script],
        capture_output=True
    )
    try:
        return result.stdout.decode('utf-8').strip()
    except UnicodeDecodeError:
        return result.stdout.decode('cp932', errors='replace').strip()

def run_e2e_test():
    print("=== BurntToast E2E Test Starting ===")
    
    # プロジェクトルートをPYTHONPATHに追加
    sys.path.append(os.getcwd())
    
    # 1. スキルの初期化
    config_path = "skills/burnt_toast_config.json"
    if not os.path.exists(config_path):
        print(f"❌ Config not found at {config_path}")
        return

    skill = BurntToastSkill(config_path)
    
    # 2. テスト用の一意なタイトルを生成
    test_id = int(time.time())
    test_title = f"E2E_TEST_{test_id}"
    test_message = "This is a real notification sent from the E2E test script."
    
    print(f"🔔 Sending notification: {test_title}")
    
    # 3. 通知送信
    # 実際の環境では powershell.exe が必要
    success = skill.success(title=test_title, message=test_message)
    
    if not success:
        print("❌ Failed to execute PowerShell command.")
        print("   Make sure 'powershell.exe' is available in your PATH and 'BurntToast' module is installed in Windows.")
        return

    print("✅ PowerShell command sent successfully.")
    print("⏳ Waiting for Windows to process notification (3s)...")
    time.sleep(3)
    
    # 4. 履歴による検証
    print("🔍 Verifying notification in Windows History...")
    status = verify_notification_in_history(test_title)
    
    if status == "FOUND":
        print(f"🎊 SUCCESS! Notification '{test_title}' was found in Windows Notification History.")
    elif status == "NOT_FOUND":
        print("⚠️  Notification command was successful, but it's not in the history.")
        print("   Possible reasons: Notifications are disabled, Focus Assist is on, or it was dismissed immediately.")
    elif status == "EMPTY":
        print("ℹ️  Notification history is empty.")
    else:
        print(f"❓ Unexpected status: {status}")

    print("\n💡 Manual Verification:")
    print(f"   Please check your Windows Action Center (Win + N) for a notification with title: '✨ {test_title}'")

if __name__ == "__main__":
    run_e2e_test()
