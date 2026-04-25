# Implementation Plan - BurntToast Notification Feature

## Objective
Implement a rich notification system using the PowerShell `BurntToast` module, accessible from both Windows and WSL. The system will support emotional and image-based notifications and provide an AI skill for agent interaction.

## Key Files & Context
- `docs/spec.md`: Requirements and initial proposal.
- `docs/design.md`: Detailed design (to be created).
- `skills/burnt_toast_skill.py`: Core implementation of the notification skill.
- `skills/burnt_toast_config.json`: Configuration for emotion templates.
- `wrappers/win-notify.sh`: Bash wrapper for WSL.
- `tests/test_burnt_toast_skill.py`: TDD test cases.

## Proposed Strategy
1.  **Detailed Design**: Create `docs/design.md` based on `spec.md`. This will define the class structure, configuration schema, and WSL/Win interaction protocols.
2.  **TDD Preparation**: Define test cases in `tests/test_burnt_toast_skill.py` using `pytest`. We will mock the `subprocess.run` calls to verify the generated PowerShell commands.
3.  **Core Implementation**:
    -   Implement `BurntToastSkill` class in Python.
    -   Handle WSL path conversion (`wslpath`).
    -   Implement emotion template logic.
    -   Support progress bars and interactive buttons.
4.  **Configuration**: Create `burnt_toast_config.json` with standard emotion templates (success, error, warning, etc.).
5.  **WSL Integration**: Create the `win-notify.sh` wrapper.
6.  **Verification**: Run tests and perform manual verification in a Windows/WSL environment.

## Phase 1: Detailed Design
- Define the `ToastRequest` data structure.
- Define the `BurntToastSkill` class and its methods (`send`, `success`, `error`, `waiting`, `confirm`).
- Specify the JSON schema for `burnt_toast_config.json`.
- Document the sequence of calls for WSL -> PowerShell -> Toast.

## Phase 2: T-Wada style TDD
- Write tests that fail first (Red).
- Implement minimum code to pass (Green).
- Refactor.
- Focus on verifying the PowerShell command generation logic.

## Verification & Testing
- Unit tests for command generation and path conversion.
- Integration tests (manual) to verify actual toast display on Windows.
- Cross-platform check (WSL vs. Windows native).
