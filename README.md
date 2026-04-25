# 🔔 BurntToast Notification Skill for Coding Agent

> **感情やイメージを伝える、リッチな Windows トースト通知スキル**  
> Windows 直接・WSL2 対応（WSL1 非対応）｜PowerShell BurntToast 連携

BurntToast Notification Skill は、Coding Agent がユーザーに対して「単なるテキスト通知」を超えて、**感情・状態・緊急性**を直感的に伝えるための Windows トースト通知スキルです。

---

## ✨ 特徴

- **🎭 感情ベースの通知**: 絵文字、アイコン、サウンドを組み合わせた直感的なフィードバック。
- **📊 プログレスバー対応**: 処理の進捗をリアルタイムに更新。
- **🔘 インタラクティブ**: 通知上のボタンからエージェントへのフィードバックが可能。
- **🌐 クロスプラットフォーム**: WSL2 から Windows へのパス変換と PowerShell 呼び出しに対応。

---

## 💻 セットアップ

### 1. Windows 側 (必須)
Windows の PowerShell で BurntToast モジュールをインストールします。

```powershell
Install-Module -Name BurntToast -Scope CurrentUser -Force
```

### 2. 環境要件
- **OS**: Windows 10/11
- **WSL**: **WSL2** (WSL1 はパス変換の仕様上サポートしていません)
- **Python**: 3.8+

---

## 🎯 使い方

詳細は [技術ガイド (docs/technical_guide.md)](./docs/technical_guide.md) を参照してください。

### Python スキルとして利用
```python
from skills.burnt_toast_skill import get_skill

# スキルの初期化
toast = get_skill("skills/burnt_toast_config.json")["instance"]

# 成功通知
toast.success("ビルド完了", "すべてのテストに合格しました。")
```

---

## 🧪 テスト
```bash
# 単体テスト (TDD)
PYTHONPATH=. pytest tests/test_burnt_toast_skill.py

# 実環境 E2E テスト
PYTHONPATH=. python3 tests/e2e_test.py
```

---

## 📚 ドキュメント
- [技術ガイド](./docs/technical_guide.md) - アーキテクチャと実装の詳細
- [API リファレンス](./docs/API_REFERENCE.md) - BurntToast モジュールの API 仕様
- [感情表現ガイド](./docs/emotions.md) - 感情テンプレートとカスタマイズ方法

---

## 📝 依存関係とライセンス

### 依存モジュール
本プロジェクトは [BurntToast](https://github.com/Windos/BurntToast) モジュールに依存しています。

**BurntToast** (MIT License)
- Copyright (c) 2015 Joshua King
- 本プロジェクトの核心機能（Windows トースト通知の生成と表示）を担当
- [BurntToast ライセンス](./docs/external/BurntToast/LICENSE) を参照

### 本プロジェクトのライセンス
本プロジェクトは **MIT License** で提供されます。
- [LICENSE](./LICENSE) を参照
- BurntToast モジュールのライセンス条件も遵守してください

---

## 🤝 貢献
バグ報告や機能要望は Issue を作成してください。

---

## 📬 コンタクト
- Issue: [GitHub Issues](https://github.com/utenadev/ai-toast/issues)
- 開発者: utenadev

---

Made with ❤️ by utenadev (2026)
