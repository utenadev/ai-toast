import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from skills.burnt_toast_skill import BurntToastSkill, ToastRequest, ToastButton, get_skill

@pytest.fixture
def dummy_config(tmp_path):
    config = {
        "powershell_exe": "powershell.exe",
        "powershell_args": ["-NoProfile", "-ExecutionPolicy", "Bypass"],
        "icon_base_path": "C:\\agents\\icons",
        "emotion_templates": {
            "success": {
                "text_prefix": "✨",
                "icon": "success.png",
                "sound": "Notification.Mail",
                "button_color": "Green",
                "button_label": "OK"
            },
            "error": {
                "text_prefix": "⚠️",
                "icon": "error.png",
                "sound": "Notification.Fault",
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
    config_path = tmp_path / "burnt_toast_config.json"
    config_path.write_text(json.dumps(config))
    return str(config_path)

@pytest.fixture
def skill(dummy_config):
    return BurntToastSkill(config_path=dummy_config)

def test_success_notification_command_generation(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.success(title="Done", message="Task finished")
            args, _ = mock_run.call_args
            ps_command = args[0][-1]
            assert "New-BurntToastNotification" in ps_command
            assert "-Text '✨ Done'" in ps_command
            assert "-AppLogo 'C:\\agents\\icons\\success.png'" in ps_command
            assert "-Button (New-BTButton -Content 'OK' -Arguments 'action:success' -Color Green)" in ps_command

def test_error_notification_command_generation(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.error(title="Failed", message="Critical error")
            args, _ = mock_run.call_args
            ps_command = args[0][-1]
            assert "-Text '⚠️ Failed'" in ps_command
            assert "-Urgent" in ps_command
            assert "-Scenario 'Urgent'" in ps_command
            assert "-Sound 'ms-winsoundevent:Notification.Fault'" in ps_command

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
            ps_command = args[0][-1]
            assert "-UniqueIdentifier 'job1'" in ps_command
            assert "-ProgressBar (New-BTProgressBar -Title 'Halfway' -Value 0.5 -ValueDisplay '50%')" in ps_command

def test_confirm_notification(skill):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        with patch("shutil.which", return_value="/usr/bin/powershell.exe"):
            skill.confirm(title="Confirm", message="Sure?")
            args, _ = mock_run.call_args
            ps_command = args[0][-1]
            assert "-Scenario 'IncomingCall'" in ps_command
            assert "-Button ((New-BTButton -Content '✅ 適用' -Arguments 'confirm:yes' -Color Green), (New-BTButton -Content '❌ 却下' -Arguments 'confirm:no' -Color Red))" in ps_command

def test_get_skill():
    skill_data = get_skill()
    assert skill_data["name"] == "burnt_toast"
    assert "toast_success" in skill_data["commands"]
    assert isinstance(skill_data["instance"], BurntToastSkill)
