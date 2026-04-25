# 詳細設計書: BurntToast Notification Skill for Coding Agent

## 1. 目的
Coding Agent が Windows および WSL (Windows Subsystem for Linux) 環境下で、ユーザーに対して感情やイメージを伴うリッチなトースト通知を送信するための機能を定義する。PowerShell の `BurntToast` モジュールを基盤とし、Python スキルとして実装することで、エージェントとの対話フローに自然に組み込めるようにする。

## 2. システム構成・アーキテクチャ

### 2.1 全体図
```
[ Coding Agent (WSL or Windows) ]
        |
        v
[ BurntToastSkill (Python) ] <--- [ config.json (Emotion Templates) ]
        |
        | (subprocess.run)
        v
[ powershell.exe ]
        |
        | (Import-Module BurntToast; New-BurntToastNotification ...)
        v
[ Windows Action Center (Toast Notification) ]
```

### 2.2 実行環境の差異吸収
- **Windows 直接実行**: `powershell.exe` を直接呼び出し。
- **WSL 実行**: 
    - `/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe` を使用。
    - `wslpath -w` を用いて WSL パスを Windows 形式のパスに変換。
    - 画像ファイル等のリソースは Windows 側からアクセス可能なパスである必要がある。

## 3. コンポーネント設計

### 3.1 BurntToastSkill クラス (Python)
通知の生成と送信を司るメインクラス。

#### 主要メソッド
- `__init__(config_path: str)`: 設定ファイルの読み込みと初期化。
- `send(emotion, title, message, **kwargs)`: テンプレートに基づく汎用通知送信。
- `success(title, message, **kwargs)`: 成功通知 (テンプレート: success)。
- `error(title, message, **kwargs)`: エラー通知 (テンプレート: error)。
- `waiting(title, message, unique_id, value, status)`: 進捗バー付き通知。
- `confirm(title, message, on_yes, on_no)`: 2ボタン確認通知。
- `update_progress(unique_id, value, status)`: 既存の通知の進捗バーを更新。

### 3.2 データ構造

#### ToastRequest (Dataclass)
通知リクエストの内部表現。
- `emotion`: テンプレート名
- `title`: タイトル
- `message`: 本文
- `unique_id`: 通知の一意識別子（更新用）
- `progress_value`: 進捗率 (0.0 - 1.0)
- `progress_status`: 進捗ステータス文字列
- `hero_image`: ヒーロー画像のパス
- `custom_buttons`: `ToastButton` オブジェクトのリスト

#### ToastButton (Dataclass)
ボタンの定義。
- `label`: ボタンのテキスト
- `arguments`: クリック時に渡される引数
- `color`: ボタンの色 (Green, Red, Yellow等、BurntToastの仕様に準拠)

### 3.3 設定ファイル (burnt_toast_config.json)
感情ごとのデフォルト設定を保持する。

#### テンプレート項目
- `text_prefix`: タイトルに付与する絵文字
- `icon`: アイコン画像ファイル名
- `sound`: 通知音 (`ms-winsoundevent:*`)
- `button_color`: デフォルトのボタン色
- `urgent`: 緊急フラグ (`-Urgent`)
- `scenario`: 通知シナリオ (`IncomingCall`, `Urgent` 等)

## 4. シーケンス
1.  Agent が `toast_success("完了", "ビルドに成功しました")` を呼び出す。
2.  `BurntToastSkill` が `config.json` から `success` テンプレートを取得。
3.  タイトルを `✨ 完了` に整形。
4.  WSL 環境の場合、アイコンパスを Windows 形式に変換。
5.  `New-BurntToastNotification` コマンドライン文字列を構築。
6.  `powershell.exe -Command "..."` を実行。
7.  Windows 通知センターにトーストが表示される。

## 5. テスト計画 (T-Wada式TDD)

### 5.1 テスト方針
- `subprocess.run` を Mock し、生成された PowerShell コマンドが期待通りであることを検証する。
- 実際に通知を出すテストは、手動または統合テストとして分離する。

### 5.2 テストケース案
1.  **Red**: `success` 呼び出し時に、期待されるパラメータ（`-Text`, `-AppLogo`, `-Sound`）を含む PowerShell コマンドが生成されること。
2.  **Red**: WSL 環境をシミュレートし、パス変換が正しく行われたコマンドが生成されること。
3.  **Red**: `waiting` 呼び出し時に `-ProgressBar` パラメータが含まれること。
4.  **Red**: `confirm` 呼び出し時に 2 つの `-Button` オブジェクトが含まれること。
5.  **Green**: 各ケースをパスするように `BurntToastSkill` のロジックを実装。
6.  **Refactor**: コマンド構築ロジックの整理、パス変換の共通化。

## 6. セキュリティと制限事項
- `powershell.exe` の呼び出しには `-ExecutionPolicy Bypass` を使用し、スクリプト実行制限を回避する。
- ユーザー入力が PowerShell コマンドに直接埋め込まれるため、シングルクォートのパース等、OSコマンドインジェクションに対する適切なエスケープ処理を行う。
- 画像サイズは 3MB 未満、ローカルパス推奨（ネットワーク遅延回避）。
