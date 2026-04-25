import pytest
import json
import base64
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
from skills.burnt_toast_skill import BurntToastSkill, BurntToastBackend, ToastRequest, ToastButton, get_skill

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
            # 配列記法 @( ) になっていることを確認
            assert "-Text @('✨ Done', 'Task finished')" in ps_command

def test_wsl_path_conversion(skill):
    backend = skill.backend
    with patch("subprocess.run") as mock_run:
        def side_effect(cmd, **kwargs):
            if cmd[0] == "wslpath":
                return MagicMock(stdout="C:\\test\\image.png\n", returncode=0)
            return MagicMock(returncode=0)
        mock_run.side_effect = side_effect
        win_path = backend._wsl_to_win_path("/mnt/c/test/image.png")
        assert win_path == "C:\\test\\image.png"

def test_command_injection_prevention(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            # シングルクォートを含む入力を指定
            malicious_title = "Done'; Write-Host 'Hacked"
            skill.success(title=malicious_title, message="Check console")
            args, _ = mock_run.call_args
            full_cmd = args[0]
            assert "-EncodedCommand" in full_cmd
            ps_command = decode_ps_command(full_cmd[-1])
            # シングルクォートが '' にエスケープされていることを確認
            escaped_title = malicious_title.replace("'", "''")
            assert escaped_title in ps_command
            # エスケープされていない生のリテラルが含まれていないことを確認
            assert malicious_title not in ps_command

def test_path_traversal_prevention(skill):
    backend = skill.backend
    traversal_path = "../../etc/passwd"
    with pytest.raises(ValueError, match="安全でないパスが指定されました"):
        backend._get_icon_path(traversal_path)

def test_broken_config_loading(tmp_path):
    broken_json = tmp_path / "broken.json"
    broken_json.write_text("{ invalid json }")
    skill = BurntToastSkill(config_path=str(broken_json))
    assert skill.backend.ps_exe == BurntToastBackend.DEFAULT_PS_EXE
    assert skill.templates == {}

def test_timeout_handling(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="powershell", timeout=10)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            result = skill.success(title="Test", message="Wait")
            assert result is False

def test_powershell_not_found(skill):
    with patch("shutil.which", return_value=None):
        with patch("skills.burnt_toast_skill.Path.exists", return_value=False):
            result = skill.success(title="Test", message="Missing PS")
            assert result is False

def test_special_characters_handling(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            special_text = "こんにちは 🤖 世界 🌍"
            skill.success(title="和文", message=special_text)
            args, _ = mock_run.call_args
            ps_command = decode_ps_command(args[0][-1])
            assert special_text in ps_command

def test_empty_input_handling(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.success(title="", message="")
            args, _ = mock_run.call_args
            ps_command = decode_ps_command(args[0][-1])
            assert "New-BurntToastNotification" in ps_command

def test_get_skill():
    skill_data = get_skill()
    assert skill_data["name"] == "burnt_toast"
    assert "toast_success" in skill_data["commands"]
    assert isinstance(skill_data["instance"], BurntToastSkill)
