# 📚 BurntToast APIリファレンス

本ドキュメントは、ai-toastスキルで使用しているBurntToastモジュールのAPIリファレンスです。

## 📋 目次

- [概要](#-概要)
- [主なコマンド](#-主なコマンド)
- [パラメータリファレンス](#-パラメータリファレンス)
- [使用例](#-使用例)
- [外部リファレンス](#-外部リファレンス)

## 📖 概要

BurntToastは、Windows 10/11向けのリッチなトースト通知をPowerShellから制御するためのモジュールです。
ai-toastスキルは、このモジュールをバックエンドとして使用しています。

## 🔧 主なコマンド

### New-BurntToastNotification

トースト通知を作成および表示します。

**基本構文:**
```powershell
New-BurntToastNotification -Text "タイトル", "本文"
```

**主なパラメータ:**

| パラメータ | 型 | 説明 | 必須 |
|-----------|-----|------|------|
| Text | String[] | 最大3つのテキスト（最初がタイトル） | ✅ |
| AppLogo | String | アプリケーションロゴのパス | ❌ |
| HeroImage | String | プロミネントな画像のパス | ❌ |
| Attribution | String | 属性テキスト | ❌ |
| Sound | String | 再生するサウンド | ❌ |
| Silent | Switch | 無音モード | ❌ |
| Button | IToastButton[] | カスタムアクションボタン | ❌ |
| ProgressBar | AdaptiveProgressBar[] | 進捗バー | ❌ |
| UniqueIdentifier | String | 通知のグループ化ID | ❌ |
| Urgent | Switch | 重要通知（Focus Assist突破） | ❌ |
| ExpirationTime | DateTime | Action Centerからの削除時間 | ❌ |

**詳細:** [New-BurntToastNotification](./external/BurntToast/Help/New-BurntToastNotification.md)

### New-BTButton

トースト通知にボタンを追加します。

**基本構文:**
```powershell
$button = New-BTButton -Content "ボタンテキスト" -Arguments "引数"
New-BurntToastNotification -Text "タイトル" -Button $button
```

**主なパラメータ:**

| パラメータ | 型 | 説明 | 必須 |
|-----------|-----|------|------|
| Content | String | ボタンに表示するテキスト | ✅ |
| Arguments | String | ボタン押下時の引数 | ✅ |
| Color | String | ボタンの色（Green, Red, Yellow） | ❌ |

**詳細:** [New-BTButton](./external/BurntToast/Help/New-BTButton.md)

### New-BTProgressBar

進捗バーを追加します。

**基本構文:**
```powershell
$progress = New-BTProgressBar -Title "処理中" -Value 0.5 -Status "50%完了"
New-BurntToastNotification -Text "タイトル" -ProgressBar $progress
```

**主なパラメータ:**

| パラメータ | 型 | 説明 | 必須 |
|-----------|-----|------|------|
| Title | String | 進捗バーのタイトル | ✅ |
| Value | Double | 進捗値（0.0〜1.0） | ✅ |
| Status | String | 状態テキスト | ❌ |

**詳細:** [New-BTProgressBar](./external/BurntToast/Help/New-BTProgressBar.md)

## 📝 パラメータリファレンス

### サウンドオプション

利用可能なサウンドイベント：
- `Default`
- `Mail`
- `Reminder`
- `SMS`
- `Alarm`
- `Call`
- `Loop.Call`
- `Loop.Alarm`
- `Loop.Reminder`
- `Silent`

### ボタンカラー

利用可能なボタンカラー：
- `Green`
- `Red`
- `Yellow`

### シナリオ

利用可能なシナリオ：
- `Default`
- `Urgent`（重要通知）
- `IncomingCall`（着信風レイアト）

## 💡 使用例

### 基本的な通知

```powershell
New-BurntToastNotification -Text "Hello", "World"
```

### ボタン付き通知

```powershell
$button = New-BTButton -Content "開く" -Arguments "file://C:/path/to/file.txt"
New-BurntToastNotification -Text "ファイル準備完了", "ファイルを開きますか？" -Button $button
```

### 進捗バー付き通知

```powershell
$progress = New-BTProgressBar -Title "処理中" -Value 0.75 -Status "75%完了"
New-BurntToastNotification -Text "処理中...", "しばらくお待ちください" -ProgressBar $progress
```

### 重要通知（Focus Assist突破）

```powershell
New-BurntToastNotification -Text "緊急", "システムエラーが発生しました" -Urgent
```

### 無音通知

```powershell
New-BurntToastNotification -Text "情報", "バックグラウンドで処理中" -Silent
```

## 🔗 外部リファレンス

### BurntToast公式ドキュメント

- [New-BurntToastNotification](./external/BurntToast/Help/New-BurntToastNotification.md)
- [New-BTButton](./external/BurntToast/Help/New-BTButton.md)
- [New-BTProgressBar](./external/BurntToast/Help/New-BTProgressBar.md)
- [New-BTAudio](./external/BurntToast/Help/New-BTAudio.md)
- [New-BTHeader](./external/BurntToast/Help/New-BTHeader.md)

### 関連リソース

- [BurntToast GitHubリポジトリ](https://github.com/Windos/BurntToast)
- [Windows Toast Notification API](https://docs.microsoft.com/en-us/windows/uwp/design/shell/tiles-and-notifications/toast-notifications)

## 📊 ai-toastスキルとの対応関係

ai-toastスキルのメソッドとBurntToastパラメータの対応関係：

| ai-toastメソッド | BurntToastパラメータ | 説明 |
|------------------|---------------------|------|
| `success()` | `-Sound Mail` | 成功通知 |
| `error()` | `-Sound Default -Urgent` | エラー通知 |
| `warning()` | `-Sound Reminder` | 警告通知 |
| `waiting()` | `-ProgressBar` | 進捗通知 |
| `confirm()` | `-Scenario IncomingCall` | 確認通知 |
| `update_progress()` | `-UniqueIdentifier` | 進捗更新 |

## 🎯 ベストプラクティス

1. **重要通知にはUrgentフラグを使用**: Focus Assistを突破し、ユーザーに必ず表示されます
2. **進捗バーはUniqueIdentifierと組み合わせる**: 同じIDで更新することで、通知をスタックせずに更新できます
3. **ボタンは最大5つまで**: Windowsの制限により、5つ以上のボタンは表示されません
4. **画像サイズに注意**: HeroImageは3MB以下、AppLogoは適切なサイズにします
5. **エンコーディングはUTF-8**: 日本語を含むテキストはUTF-8で処理します

## 🔍 トラブルシューティング

### 通知が表示されない場合

1. Windowsの通知設定を確認
2. Focus Assist（おやすみモード）が無効であることを確認
3. Urgentフラグを使用してみる
4. PowerShellの実行ポリシーを確認

### 文字化けが発生する場合

1. PowerShellのエンコーディング設定を確認
2. `$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8`を追加
3. ai-toastスキルのエンコーディング処理を確認

## 📝 更新履歴

- 2026/04/25: 初版作成
- BurntToast v0.8.5に基づく

以上がBurntToastモジュールのAPIリファレンスです。詳細な情報は外部リファレンスを参照してください。