# T-Wada Style TDD Plan: BurntToast Notification Skill

## 1. TDD Cycle: RED (Initial Test Cases)
We will start by writing tests that verify the PowerShell command generation. Since we are in a testing environment (likely Linux/WSL), we will mock `subprocess.run` to check the arguments.

### `tests/test_burnt_toast_skill.py` (Draft)

```python
import pytest
from unittest.mock import patch, MagicMock
from skills.burnt_toast_skill import BurntToastSkill, ToastRequest, ToastButton

@pytest.fixture
def skill():
    # Setup with a dummy config
    return BurntToastSkill(config_path="skills/burnt_toast_config.json")

def test_success_notification_command_generation(skill):
    """
    Test Case 1: success() generates a command with correct title, message, and icon.
    (RED: Skill.success is not yet implemented)
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        skill.success(title="Done", message="Task finished")
        
        # Verify subprocess.run was called with powershell.exe and correct command
        args, kwargs = mock_run.call_args
        ps_command = args[0][-1] # Assuming command is the last arg
        
        assert "New-BurntToastNotification" in ps_command
        assert "-Text '✨ Done'" in ps_command
        assert "-Text 'Task finished'" in ps_command
        assert "-AppLogo" in ps_command
        assert "success.png" in ps_command

def test_wsl_path_conversion(skill):
    """
    Test Case 2: WSL path is correctly converted to Windows path.
    (RED: Path conversion logic is not yet implemented)
    """
    with patch("subprocess.run") as mock_run:
        # Mock wslpath response
        def side_effect(cmd, **kwargs):
            if cmd[0] == "wslpath":
                return MagicMock(stdout="C:\\test\\image.png\n", returncode=0)
            return MagicMock(returncode=0)
        
        mock_run.side_effect = side_effect
        
        # This should trigger path conversion if internal logic detects WSL
        win_path = skill._wsl_to_win_path("/mnt/c/test/image.png")
        assert win_path == "C:\\test\\image.png"

def test_progress_bar_update(skill):
    """
    Test Case 3: update_progress() generates a command with -ProgressBar and -UniqueIdentifier.
    (RED: update_progress is not yet implemented)
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        skill.update_progress(unique_id="job1", value=0.5, status="Halfway")
        
        args, kwargs = mock_run.call_args
        ps_command = args[0][-1]
        
        assert "-UniqueIdentifier 'job1'" in ps_command
        assert "-ProgressBar" in ps_command
        assert "-Value 0.5" in ps_command
        assert "Halfway" in ps_command
```

## 2. Next Steps: GREEN
1.  Implement the minimum code in `skills/burnt_toast_skill.py` to make these tests pass.
2.  Handle the `Import-Module BurntToast` dependency check.
3.  Ensure robust escaping for PowerShell strings.

## 3. Refactoring
- Abstract the PowerShell command builder into a separate private method.
- Improve error handling for missing `powershell.exe` or `wslpath`.
