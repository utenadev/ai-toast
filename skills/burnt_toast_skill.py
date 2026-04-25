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
import base64
import logging
from pathlib import Path
from typing import Optional, List, Dict, Union
from dataclasses import dataclass, asdict

# ロギングの設定
logger = logging.getLogger(__name__)

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

    # 定数定義
    DEFAULT_PS_EXE = "powershell.exe"
    DEFAULT_PS_ARGS = ["-NoProfile", "-ExecutionPolicy", "Bypass"]
    WIN_PS_PATH = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    DEFAULT_TIMEOUT = 10  # 秒
    UTF8_ENCODING = "utf-8"
    CP932_ENCODING = "cp932"

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ps_exe = self.config.get("powershell_exe", self.DEFAULT_PS_EXE)
        self.ps_args = self.config.get("powershell_args", self.DEFAULT_PS_ARGS)
        self.icon_base = Path(self.config.get("icon_base_path", ""))
        self.default_app_id = self.config.get("default_app_id")
        self.templates = self.config.get("emotion_templates", {})
        self.timeout = self.config.get("timeout", self.DEFAULT_TIMEOUT)

    def _load_config(self, path: Optional[str]) -> dict:
        """設定ファイルを読み込む。存在しない場合や不正な場合はデフォルト値を返す"""
        if not path:
            return {}
            
        config_path = Path(path)
        if not config_path.exists():
            logger.warning(f"設定ファイルが見つかりません: {path}")
            return {}

        try:
            with open(config_path, 'r', encoding=self.UTF8_ENCODING) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"設定ファイルの形式が不正です ({path}): {e}")
            return {}
        except Exception as e:
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました ({path}): {e}")
            return {}

    def _wsl_to_win_path(self, path: str) -> str:
        """WSL パスを Windows パスに変換（必要時）"""
        if not path.startswith('/mnt/'):
            return path
        try:
            result = subprocess.run(
                ['wslpath', '-w', path],
                capture_output=True, 
                text=True, 
                check=True,
                timeout=5
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            # 変換失敗時は手動置換によるフォールバック（Windows 側で処理）
            return path.replace('/mnt/c/', 'C:\\').replace('/', '\\')

    def _get_icon_path(self, icon_name: str) -> str:
        """アイコンのフルパスを取得し、必要に応じてWindows形式に変換する。パストラバーサルを防止する。"""
        # ベースパスが設定されている場合、その外に出ないかチェックする
        if self.icon_base and self.icon_base.as_posix() not in (".", ""):
            try:
                base_resolved = self.icon_base.resolve()
                requested_path = (base_resolved / icon_name).resolve()
                # requested_path が base_resolved の配下であることを確認
                requested_path.relative_to(base_resolved)
                full_path = requested_path
            except ValueError:
                logger.error(f"パストラバーサルの可能性を検知しました: {icon_name}")
                raise ValueError(f"安全でないパスが指定されました: {icon_name}")
        else:
            full_path = Path(icon_name)

        win_path = self._wsl_to_win_path(str(full_path))
        # Windowsパスとしてバックスラッシュに統一
        if not win_path.startswith('/mnt/'):
            return win_path.replace('/', '\\')
        return win_path

    def _encode_command(self, command: str) -> str:
        """PowerShellの -EncodedCommand 用に文字列をBase64エンコードする"""
        # PowerShellは UTF-16LE エンコーディングを期待する
        utf16_cmd = command.encode('utf-16-le')
        return base64.b64encode(utf16_cmd).decode('ascii')

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
            try:
                icon_path = self._get_icon_path(icon)
                params.append(f"-AppLogo '{icon_path}'")
            except ValueError as e:
                logger.warning(str(e))
        
        if req.hero_image:
            hero_path = self._wsl_to_win_path(req.hero_image)
            # ヒーロー画像もWindowsパス形式に正規化
            if not hero_path.startswith('/mnt/'):
                hero_path = hero_path.replace('/', '\\')
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
        
        ps_exe = self.ps_exe

        # PATHで見つからない場合のフォールバック
        if not shutil.which(ps_exe):
            if Path(self.WIN_PS_PATH).exists():
                ps_exe = self.WIN_PS_PATH
            else:
                logger.error(f"PowerShell実行ファイルが見つかりません: {ps_exe}")
                return False

        # コマンドインジェクション対策として -EncodedCommand を使用する

        encoded_cmd = self._encode_command(ps_command)
        full_cmd = [ps_exe] + self.ps_args + ["-EncodedCommand", encoded_cmd]
        
        try:
            # shell=False を指定し、コマンドインジェクションを防止
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                timeout=self.timeout,
                shell=False
            )
            
            # デコード処理
            stderr = ""
            stdout = ""
            try:
                stderr = result.stderr.decode(self.UTF8_ENCODING)
                stdout = result.stdout.decode(self.UTF8_ENCODING)
            except UnicodeDecodeError:
                stderr = result.stderr.decode(self.CP932_ENCODING, errors='replace')
                stdout = result.stdout.decode(self.CP932_ENCODING, errors='replace')

            if result.returncode != 0:
                logger.error(f"PowerShell実行エラー (Return Code: {result.returncode})")
                if stderr: logger.error(f"stderr: {stderr.strip()}")
                if stdout: logger.info(f"stdout: {stdout.strip()}")
            return result.returncode == 0

        except FileNotFoundError:
            logger.error(f"PowerShell実行ファイルが見つかりません: '{ps_exe}'")
            return False
        except subprocess.TimeoutExpired:
            logger.error(f"PowerShellの実行がタイムアウトしました ({self.timeout}s)")
            return False
        except Exception as e:
            logger.exception(f"通知送信中に予期せぬエラーが発生しました: {e}")
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
