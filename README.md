# 🔔 BurntToast Notification Skill for Coding Agent

> **感情やイメージを伝える、リッチな Windows トースト通知スキル**  
> Windows 直接・WSL 両対応｜PowerShell BurntToast 連携｜会話型エージェント向け

BurntToast Notification Skill は、Coding Agent がユーザーに対して「単なるテキスト通知」を超えて、**感情・状態・緊急性**を直感的に伝えるための Windows トースト通知スキルです。

---

## ✨ 特徴

- **🎭 感情ベースの通知**: 絵文字、アイコン、サウンドを組み合わせた直感的なフィードバック。
- **📊 プログレスバー対応**: 重い処理の進捗を 0-100% でリアルタイム更新。
- **🔘 インタラクティブ**: 「適用」「詳細」などのボタンを配置し、通知から次のアクションへ。
- **🌐 クロスプラットフォーム**: WSL から Windows へのパス変換（wslpath）と PowerShell 呼び出しを完結。

---

## 💻 セットアップ

### 1. Windows 側 (必須)
Windows の PowerShell で BurntToast モジュールをインストールします。

```powershell
Install-Module -Name BurntToast -Scope CurrentUser -Force
```

### 2. インストール
本リポジトリをエージェントのスキルディレクトリに配置します。

```bash
git clone <this-repo> ai-toast
cd ai-toast
```

---

## 🎯 クイックスタート

### Python からの使用例
```python
from skills.burnt_toast_skill import get_skill

# スキルの初期化
toast = get_skill("skills/burnt_toast_config.json")["instance"]

# 成功通知
toast.success("ビルド完了", "すべてのテストに合格しました。")

# 確認通知
toast.confirm("デプロイ確認", "本番環境に反映しますか？")
```

### WSL シェルからの使用例
```bash
./wrappers/win-notify.sh success "🎉 完了" "タスクが終了しました"
```

---

## 📚 詳細ドキュメント

より詳細な情報については、以下のドキュメントを参照してください。

- [**⚙️ 仕組みとアーキテクチャ (docs/mechanism.md)**](./docs/mechanism.md)  
  WSL連携、パス変換、文字コード対策、PowerShell コマンド構築の技術的詳細。
- [**🎭 感情表現ガイド (docs/emotions.md)**](./docs/emotions.md)  
  感情テンプレート、視覚・聴覚効果のマッピング、カスタマイズ方法。

---

## 🧪 テスト
```bash
# 単体テスト (TDD)
PYTHONPATH=. pytest tests/test_burnt_toast_skill.py

# 実環境 E2E テスト
PYTHONPATH=. python3 tests/e2e_test.py
```
