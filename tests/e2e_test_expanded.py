import time
import sys
import os
from skills.burnt_toast_skill import BurntToastSkill, ToastButton

def run_expanded_e2e_test():
    print("=== BurntToast Expanded E2E Test (Persistence Mode) ===\n")
    sys.path.append(os.getcwd())
    
    config_path = "skills/burnt_toast_config.json"
    skill = BurntToastSkill(config_path)
    
    # 全ての通知を Silent かつ Urgent (消えにくい) に設定
    common_opts = {"silent": True, "urgent": True}
    
    # パターン1: 成功通知 (Success)
    print("1. [Success] Sending standard notification...")
    skill.success(title="E2E: Success", message="✨ Should stay on screen until dismissed.", **common_opts)
    time.sleep(0.5)

    # パターン2: エラー通知 (Error)
    print("2. [Error] Sending urgent notification...")
    skill.error(title="E2E: Error", message="⚠️ Error state with persistence.", **common_opts)
    time.sleep(0.5)

    # パターン3: 確認通知 (Confirm)
    print("3. [Confirm] Sending notification with buttons...")
    skill.confirm(title="E2E: Confirm", message="Do you see 'Apply' and 'Dismiss' buttons?", **common_opts)
    time.sleep(0.5)

    # パターン4: 進捗バー
    print("4. [Progress] Sending progress bar...")
    progress_id = f"e2e_persist_progress_{int(time.time())}"
    skill.waiting(title="E2E: Progress", message="Processing data...", unique_id=progress_id, value=0.1, status="Initializing", **common_opts)
    
    for i in range(2, 6):
        time.sleep(0.8)
        val = i / 5.0
        print(f"   - Updating progress to {int(val*100)}%...")
        # 更新時も common_opts を適用
        skill.update_progress(unique_id=progress_id, value=val, status=f"ステップ {i}/5 実行中...", **common_opts)
    
    # パターン5: 日本語リッチテキスト
    print("\n5. [Japanese] Sending rich Japanese text...")
    skill.success(title="E2E: 日本語テスト", message="日本語が正しく、かつ画面に残り続けますか？", **common_opts)

    print("\n=== E2E Persistence Test Completed ===")
    print("All notifications were sent with -Silent and -Urgent.")
    print("They should remain in your notification area until you manually clear them.")

if __name__ == "__main__":
    run_expanded_e2e_test()
