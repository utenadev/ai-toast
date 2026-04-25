#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurntToast 通知スキル
- 感情テンプレートに基づき Windows トースト通知を生成・送信
- WSL/Windows 両対応、powershell.exe 経由で実行
- 会話コンテキストから即時呼び出し可能
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Union
from dataclasses import dataclass, asdict


@dataclass
class ToastButton:
    """トースト通知に表示するボタンの定義"""
    label: str
    arguments: str
    color: Optional[str] = None  # Green, Red, Yellow 等

    def to_ps(self) -> str:
        """ボタンを生成するPowerShellコマンド片を構築"""
        color_part = f' -Color {self.color}' if self.color else ''
        return f"(New-BTButton -Content '{self.label}' -Arguments '{self.arguments}'{color_part})"


@dataclass
class ToastRequest:
    """通知リクエストのデータ構造"""
    emotion: str
    title: str
    message: str
    unique_id: Optional[str] = None
    progress_value: Optional[float] = None  # 0.0 ~ 1.0
    progress_status: Optional[str] = None
    hero_image: Optional[str] = None
    custom_buttons: Optional[List[ToastButton]] = None
    override_sound: Optional[str] = None
    attribution: str = "Coding Agent"


class BurntToastSkill:
    """BurntToast を使った感情伝達トーストの生成・送信スキル"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ps_exe = self.config.get("powershell_exe", "powershell.exe")
        self.ps_args = self.config.get("powershell_args", [])
        self.icon_base = Path(self.config.get("icon_base_path", ""))
        self.default_app_id = self.config.get("default_app_id")
        self.templates = self.config.get("emotion_templates", {})

    def _load_config(self, path: Optional[str]) -> dict:
        """設定ファイルを読み込む。存在しない場合はデフォルト値を返す"""
        if path and Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "powershell_exe": "powershell.exe",
            "powershell_args": ["-NoProfile", "-ExecutionPolicy", "Bypass"],
            "emotion_templates": {}
        }

    def _wsl_to_win_path(self, path: str) -> str:
        """WSL パスを Windows パスに変換（必要時）"""
        if not path.startswith('/mnt/'):
            return path
        try:
            result = subprocess.run(
                ['wslpath', '-w', path],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 変換失敗時はそのまま返す（Windows 側で処理）
            return path.replace('/mnt/c/', 'C:\\').replace('/', '\\')

    def _get_icon_path(self, icon_name: str) -> str:
        """アイコンのフルパスを取得し、必要に応じてWindows形式に変換する"""
        full_path = self.icon_base / icon_name if self.icon_base else Path(icon_name)
        win_path = self._wsl_to_win_path(str(full_path))
        if not win_path.startswith('/mnt/'):
            return win_path.replace('/', '\\')
        return win_path

    def _build_ps_command(self, req: ToastRequest, template: dict) -> str:
        """PowerShell コマンド文字列を構築"""
        prefix = template.get("text_prefix", "")
        title = f"{prefix} {req.title}".strip()
        
        # 基本パラメータ (Textは配列として渡す必要がある)
        params = [
            f"-Text '{title}', '{req.message}'",
            f"-Attribution '{req.attribution}'"
        ]

        # 画像設定
        icon = template.get("icon")
        if icon:
            icon_path = self._get_icon_path(icon)
            params.append(f"-AppLogo '{icon_path}'")
        
        if req.hero_image:
            hero_path = self._wsl_to_win_path(req.hero_image)
            params.append(f"-HeroImage '{hero_path}'")

        # 音声設定
        sound = req.override_sound or template.get("sound")
        if sound:
            # New-BurntToastNotification ではキーワードのみを指定する
            sound_keyword = sound.replace('ms-winsoundevent:', '')
            params.append(f"-Sound '{sound_keyword}'")
        elif template.get("silent"):
            params.append("-Silent")

        # 緊急・シナリオ
        if template.get("urgent"):
            params.append("-Urgent")
        scenario = template.get("scenario")
        if scenario:
            params.append(f"-Scenario '{scenario}'")

        # 進捗バー
        if template.get("use_progress") or req.progress_value is not None:
            value = req.progress_value if req.progress_value is not None else 0.0
            status = req.progress_status or template.get("progress_title", "処理中")
            display = f"{int(value * 100)}%"
            params.append(f"-ProgressBar (New-BTProgressBar -Title '{status}' -Value {value} -ValueDisplay '{display}')")

        # ユニークID（更新用）
        if req.unique_id:
            params.append(f"-UniqueIdentifier '{req.unique_id}'")

        # ボタン設定
        buttons = req.custom_buttons
        if not buttons and template.get("button_label"):
            btn = ToastButton(
                label=template["button_label"],
                arguments=f"action:{req.emotion}",
                color=template.get("button_color")
            )
            buttons = [btn]
        
        if buttons:
            btn_strs = [btn.to_ps() for btn in buttons]
            if len(btn_strs) == 1:
                params.append(f"-Button {btn_strs[0]}")
            else:
                joined = ", ".join(btn_strs)
                params.append(f"-Button ({joined})")

        # UTF-8出力を強制する設定を追加
        ps_cmd = f"$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Import-Module BurntToast -ErrorAction SilentlyContinue; New-BurntToastNotification {' '.join(params)}"
        return ps_cmd

    def notify(self, req: ToastRequest) -> bool:
        """トースト通知を送信"""
        template = self.templates.get(req.emotion, {})
        ps_command = self._build_ps_command(req, template)
        
        ps_exe = self.ps_exe  # デフォルトは "powershell.exe"
        
        # PATHで見つからない場合のフォールバック
        if not shutil.which(ps_exe):
            fallback = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
            if Path(fallback).exists():
                ps_exe = fallback

        full_cmd = [ps_exe] + self.ps_args + ["-Command", ps_command]
        
        try:
            # shell=True を指定せず、コマンドリストを渡す
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                timeout=10
            )
            
            # UTF-8で試行し、失敗したら CP932(Shift-JIS) でデコードを試みる
            try:
                stderr = result.stderr.decode('utf-8')
                stdout = result.stdout.decode('utf-8')
            except UnicodeDecodeError:
                stderr = result.stderr.decode('cp932', errors='replace')
                stdout = result.stdout.decode('cp932', errors='replace')

            if result.returncode != 0:
                print(f"[BurntToast] PowerShell Return Code: {result.returncode}")
                print(f"[BurntToast] Standard Error: {stderr}")
                print(f"[BurntToast] Standard Output: {stdout}")
            return result.returncode == 0
        except FileNotFoundError:
            print(f"[BurntToast] Error: '{ps_exe}' not found in PATH.")
            return False
        except Exception as e:
            print(f"[BurntToast] Exception: {e}")
            return False

    def send(self, emotion: str, title: str, message: str, **kwargs) -> bool:
        """最小引数で通知を送信（会話フロー向け）"""
        req = ToastRequest(emotion=emotion, title=title, message=message, **kwargs)
        return self.notify(req)
    
    def success(self, title: str, message: str, **kwargs) -> bool:
        """成功通知"""
        return self.send("success", title, message, **kwargs)
    
    def error(self, title: str, message: str, **kwargs) -> bool:
        """エラー通知"""
        return self.send("error", title, message, **kwargs)
    
    def warning(self, title: str, message: str, **kwargs) -> bool:
        """警告通知"""
        return self.send("warning", title, message, **kwargs)
    
    def waiting(self, title: str, message: str, 
                unique_id: str, value: float = None, status: str = None, **kwargs) -> bool:
        """進捗通知（更新可能）"""
        req = ToastRequest(
            emotion="waiting", title=title, message=message,
            unique_id=unique_id, progress_value=value, progress_status=status, **kwargs
        )
        return self.notify(req)
    
    def confirm(self, title: str, message: str, 
                on_yes: str = "confirm:yes", on_no: str = "confirm:no", **kwargs) -> bool:
        """確認ダイアログ風トースト"""
        buttons = [
            ToastButton("✅ 適用", on_yes, "Green"),
            ToastButton("❌ 却下", on_no, "Red")
        ]
        req = ToastRequest(
            emotion="confirmation", title=title, message=message,
            custom_buttons=buttons, **kwargs
        )
        return self.notify(req)
    
    def update_progress(self, unique_id: str, value: float, status: Optional[str] = None) -> bool:
        """進捗バーを更新（同一ユニークIDで上書き）"""
        req = ToastRequest(
            emotion="waiting", title="", message="",
            unique_id=unique_id, progress_value=value, progress_status=status
        )
        return self.notify(req)


# ========== Skill 登録用エントリーポイント ==========

def get_skill(config_path: Optional[str] = None):
    """nanobot / Agent フレームワーク向け skill 取得関数"""
    skill = BurntToastSkill(config_path)
    
    # 会話中に呼び出せるコマンド名を登録
    commands = {
        "notify": skill.send,
        "toast_success": skill.success,
        "toast_error": skill.error,
        "toast_warning": skill.warning,
        "toast_waiting": skill.waiting,
        "toast_confirm": skill.confirm,
        "toast_update": skill.update_progress,
    }
    
    return {
        "name": "burnt_toast",
        "description": "感情・イメージを伝える Windows トースト通知を送信するスキル",
        "commands": commands,
        "instance": skill
    }
