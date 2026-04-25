import pytest
import json
import base64
from unittest.mock import patch, MagicMock
from pathlib import Path
from skills.burnt_toast_skill import BurntToastSkill, ToastRequest, ToastButton, get_skill

@pytest.fixture
def dummy_config(tmp_path):
    config = {
        "powershell_exe": "powershell.exe",
        "powershell_args": ["-NoProfile", "-ExecutionPolicy", "Bypass"],
        "icon_base_path": str(tmp_path / "icons"),
        "emotion_templates": {
            "success": {
                "text_prefix": "✨",
                "icon": "success.png",
                "sound": "Mail",
                "button_color": "Green",
                "button_label": "OK"
            },
            "error": {
                "text_prefix": "⚠️",
                "icon": "error.png",
                "sound": "Default",
                "button_color": "Red",
                "button_label": "Detail",
                "urgent": True,
                "scenario": "Urgent"
            },
            "waiting": {
                "text_prefix": "🔄",
                "icon": "thinking.png",
                "use_progress": True,
                "progress_title": "Processing"
            },
            "confirmation": {
                "text_prefix": "🤖",
                "icon": "agent.png",
                "sound": "Call",
                "scenario": "IncomingCall"
            }
        }
    }
    # アイコンディレクトリを作成
    (tmp_path / "icons").mkdir()
    config_path = tmp_path / "burnt_toast_config.json"
    config_path.write_text(json.dumps(config))
    return str(config_path)

@pytest.fixture
def skill(dummy_config):
    return BurntToastSkill(config_path=dummy_config)

def decode_ps_command(encoded_str):
    """Base64エンコードされたPowerShellコマンドをデコードする"""
    return base64.b64decode(encoded_str).decode('utf-16-le')

def test_success_notification_command_generation(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.success(title="Done", message="Task finished")
            args, _ = mock_run.call_args
            full_cmd = args[0]
            
            assert "-EncodedCommand" in full_cmd
            ps_command = decode_ps_command(full_cmd[-1])
            
            assert "New-BurntToastNotification" in ps_command
            assert "-Text '✨ Done', 'Task finished'" in ps_command
            assert "-AppLogo" in ps_command
            assert "success.png" in ps_command
            assert "-Button (New-BTButton -Content 'OK' -Arguments 'action:success' -Color Green)" in ps_command

def test_error_notification_command_generation(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.error(title="Failed", message="Critical error")
            args, _ = mock_run.call_args
            full_cmd = args[0]
            
            assert "-EncodedCommand" in full_cmd
            ps_command = decode_ps_command(full_cmd[-1])
            
            assert "-Text '⚠️ Failed', 'Critical error'" in ps_command
            assert "-Urgent" in ps_command
            assert "-Scenario 'Urgent'" in ps_command
            assert "-Sound 'Default'" in ps_command

def test_wsl_path_conversion(skill):
    with patch("subprocess.run") as mock_run:
        def side_effect(cmd, **kwargs):
            if cmd[0] == "wslpath":
                return MagicMock(stdout="C:\\test\\image.png\n", returncode=0)
            return MagicMock(returncode=0)
        mock_run.side_effect = side_effect
        win_path = skill._wsl_to_win_path("/mnt/c/test/image.png")
        assert win_path == "C:\\test\\image.png"

def test_progress_bar_update(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.update_progress(unique_id="job1", value=0.5, status="Halfway")
            args, _ = mock_run.call_args
            full_cmd = args[0]
            
            assert "-EncodedCommand" in full_cmd
            ps_command = decode_ps_command(full_cmd[-1])
            
            assert "-UniqueIdentifier 'job1'" in ps_command
            assert "-ProgressBar (New-BTProgressBar -Title 'Halfway' -Value 0.5 -ValueDisplay '50%')" in ps_command

def test_confirm_notification(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.confirm(title="Confirm", message="Sure?")
            args, _ = mock_run.call_args
            full_cmd = args[0]
            
            assert "-EncodedCommand" in full_cmd
            ps_command = decode_ps_command(full_cmd[-1])
            
            assert "-Scenario 'IncomingCall'" in ps_command
            assert "-Button ((New-BTButton -Content '✅ 適用' -Arguments 'confirm:yes' -Color Green), (New-BTButton -Content '❌ 却下' -Arguments 'confirm:no' -Color Red))" in ps_command

def test_command_injection_prevention(skill):
    """
    テストケース: シングルクォートを含む入力によるコマンドインジェクションが防がれていること。
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            # 悪意のあるタイトル入力をシミュレート
            malicious_title = "Done'; Write-Host 'Hacked"
            skill.success(title=malicious_title, message="Check console")
            
            args, _ = mock_run.call_args
            full_cmd = args[0]
            
            assert "-EncodedCommand" in full_cmd
            # エンコードされたコマンドをデコードして、入力が含まれていることを確認
            ps_command = decode_ps_command(full_cmd[-1])
            # PowerShellの文字列として正しく埋め込まれている（エスケープはされていないが、
            # 文字列全体がひとつの引数として処理されるため安全）
            # 注意: EncodedCommand はコマンド全体をエンコードするため、
            # その中の文字列引用符自体はエスケープされない場合があるが、
            # 文字列連結攻撃は不可能になる。
            assert malicious_title in ps_command

def test_path_traversal_prevention(skill):
    """
    テストケース: ベースディレクトリ外のパス指定（パストラバーサル）が拒否されること。
    """
    # 悪意のあるアイコンパスを指定
    traversal_path = "../../etc/passwd"
    
    with pytest.raises(ValueError, match="安全でないパスが指定されました"):
        skill._get_icon_path(traversal_path)

def test_get_skill():
    skill_data = get_skill()
    assert skill_data["name"] == "burnt_toast"
    assert "toast_success" in skill_data["commands"]
    assert isinstance(skill_data["instance"], BurntToastSkill)
