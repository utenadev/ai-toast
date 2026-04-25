# 🎭 感情表現ガイド

本ドキュメントでは、ai-toastスキルの感情表現機能について解説します。

## 📋 目次

- [概要](#-概要)
- [標準感情テンプレート](#-標準感情テンプレート)
- [カスタマイズ方法](#-カスタマイズ方法)
- [感情マッピング](#-感情マッピング)
- [使用例](#-使用例)

## 📖 概要

ai-toastスキルは、エージェントの状態や感情を視覚・聴覚を通じて直感的に伝えるための仕組みを提供します。

感情表現は以下の4つの要素で構成されます：

1. **視覚的要素**: 絵文字、アイコン、画像
2. **聴覚的要素**: サウンド、警告音
3. **シナリオ**: 表示挙動、優先度
4. **インタラクション**: ボタン、進捗バー

## 🎭 標準感情テンプレート

デフォルトでは `skills/burnt_toast_config.json` にて以下の6つの感情テンプレートが定義されています。

### 成功 (Success)
```json
{
  "text_prefix": "✨",
  "icon": "success.png",
  "sound": "Mail",
  "button_color": "Green",
  "button_label": "確認",
  "urgent": false,
  "scenario": null
}
```

**特徴:**
- 緑アイコンと軽快な音で安心感を与える
- 成功時、完了時に使用
- 例: ビルド成功、テスト合格

### エラー (Error)
```json
{
  "text_prefix": "⚠️",
  "icon": "error.png",
  "sound": "Default",
  "button_color": "Red",
  "button_label": "詳細",
  "urgent": true,
  "scenario": "Urgent"
}
```

**特徴:**
- 赤アイコンと警告音で注意を促す
- UrgentフラグでFocus Assistを突破
- 例: 実行エラー、例外発生

### 警告 (Warning)
```json
{
  "text_prefix": "🔶",
  "icon": "warning.png",
  "sound": "Reminder",
  "button_color": "Yellow",
  "button_label": "了解",
  "urgent": false,
  "scenario": null
}
```

**特徴:**
- 黄アイコンとリマインダー音で注意を促す
- 緊急ではないが確認が必要な場合
- 例: ディスク容量警告、タイムアウト警告

### 待機中 (Waiting)
```json
{
  "text_prefix": "🔄",
  "icon": "thinking.png",
  "sound": null,
  "use_progress": true,
  "progress_title": "処理中",
  "urgent": false,
  "silent": true
}
```

**特徴:**
- 青アイコンと進捗バーで安心感を提供
- 無音モードで静かに処理状況を伝える
- 例: 長時間処理、バックグラウンドタスク

### 確認 (Confirmation)
```json
{
  "text_prefix": "🤖",
  "icon": "agent.png",
  "sound": "Call",
  "scenario": "IncomingCall",
  "urgent": true
}
```

**特徴:**
- 着信風デザインでユーザーの判断を待つ
- 緑/赤ボタンで明確な選択肢を提供
- 例: 設定変更の確認、重要な判断

### 情報 (Info)
```json
{
  "text_prefix": "💡",
  "icon": "info.png",
  "sound": "Default",
  "urgent": false,
  "scenario": null
}
```

**特徴:**
- 青アイコンと標準音で情報を伝える
- 一般的なお知らせに使用
- 例: 状態更新、情報提供

## ⚙️ カスタマイズ方法

新しい感情や特定のプロジェクト向けの通知スタイルを追加するには、`burnt_toast_config.json` を編集します。

### カスタム感情の追加例

```json
{
  "emotion_templates": {
    "celebration": {
      "text_prefix": "🎊",
      "icon": "celebrate.png",
      "sound": "Alarm",
      "scenario": "Urgent",
      "buttons": [
        {"label": "🎉 共有", "args": "share:celebrate", "color": "Green"}
      ]
    }
  }
}
```

**使用例:**
```python
toast.send("celebration", "おめでとう！", "目標達成しました🎯")
```

### 利用可能なサウンド

Windows の標準サウンドイベント名を指定可能です：
- `Default`, `IM`, `Mail`, `Reminder`, `SMS`
- `Alarm`, `Call` (1〜10)
- `Loop.Call`, `Loop.Alarm`, `Loop.Reminder`
- `Silent` (無音)

### 視覚的効果のカスタマイズ

1. **Hero Image**: 大きな画像を通知上部に表示
2. **AppLogo**: アイコンを左側に表示
3. **ProgressBar**: 進捗バーで処理状況を視覚化
4. **Buttons**: カスタムアクションボタンを配置

## 📊 感情マッピング

| 感情 | 絵文字 | 視覚的特徴 | 音声 | 使用シーン |
|------|-------|-----------|------|-----------|
| Success | ✨ | 緑アイコン | Mail | 成功・完了 |
| Error | ⚠️ | 赤アイコン | Default | 失敗・例外 |
| Warning | 🔶 | 黄アイコン | Reminder | 注意・警告 |
| Waiting | 🔄 | 青アイコン | Silent | 処理中・待機 |
| Confirm | 🤖 | 紫アイコン | Call | ユーザー確認 |
| Info | 💡 | 青アイコン | Default | 情報提供 |

## 💡 使用例

### 成功通知
```python
toast.success("ビルド完了✨", "すべてのテストに合格しました")
```

### エラー通知
```python
toast.error("実行エラー⚠️", "構文チェックに失敗しました")
```

### 進捗通知
```python
# 初期通知
toast.waiting("処理中🔄", "データ変換中...", unique_id="task_001", value=0.0)

# 進捗更新
toast.update_progress("task_001", value=0.5, status="50%完了")

# 完了通知
toast.success("完了✨", "処理が終了しました", unique_id="task_001")
```

### 確認通知
```python
toast.confirm("設定保存🤖", "変更を適用しますか？")
```

## 🎨 高度なカスタマイズ

### カスタムボタンの追加
```python
buttons = [
    ToastButton("👁️ 表示", "action:view", "Green"),
    ToastButton("📤 共有", "action:share", "Yellow"),
    ToastButton("🗑️ 破棄", "action:delete", "Red")
]
toast.send("info", "レポート生成", "グラフを含むレポートが完成しました", 
           custom_buttons=buttons, hero_image="report_preview.png")
```

### 進捗バーのカスタマイズ
```python
# 進捗バーのタイトルと状態をカスタマイズ
toast.waiting("処理中", "モデル学習中...", 
              unique_id="ml_train", 
              value=0.3, 
              status="Epoch 3/10", 
              progress_title="モデル学習")
```

## 🔧 エージェントへの指示

エージェントがこのスキルを使う際のガイドライン：

1. **成功時**: `success` メソッドを使い、✨ などの明るい表現をタイトルに含めてください
2. **待機時**: `waiting` を使い、進捗バーを更新することで、ユーザーが「ハングした」と誤解するのを防いでください
3. **確認時**: `confirm` を使い、ユーザーに「適用」か「却下」かの明確な選択肢を提示してください
4. **エラー時**: `error` を使い、⚠️ などの警告表現をタイトルに含めてください

## 📝 ベストプラクティス

1. **一貫性のある表現**: 同じ種類の通知には同じ感情を使用
2. **過剰な通知を避ける**: 重要なイベントのみに使用
3. **ユーザーの状況を考慮**: 緊急時にはUrgentフラグを使用
4. **進捗バーの適切な使用**: 長時間処理には必ず進捗バーを表示
5. **ボタンの明確なラベル**: ユーザーが直感的に理解できるラベルを使用

## 🔍 トラブルシューティング

### 通知が表示されない
1. Windowsの通知設定を確認
2. Focus Assist（おやすみモード）が無効であることを確認
3. Urgentフラグを使用してみる
4. PowerShellの実行ポリシーを確認

### 感情が適切に表示されない
1. 設定ファイルのパスを確認
2. アイコンファイルが存在することを確認
3. 設定ファイルのJSON構文を確認

## 📚 関連ドキュメント

- [技術ガイド](./technical_guide.md) - アーキテクチャと実装の詳細
- [APIリファレンス](./API_REFERENCE.md) - BurntToastモジュールのAPI仕様

## 📝 更新履歴

- 2026/04/25: 初版作成
- 感情テンプレートの追加とカスタマイズ方法の説明

以上が感情表現ガイドです。詳細な情報は関連ドキュメントを参照してください。