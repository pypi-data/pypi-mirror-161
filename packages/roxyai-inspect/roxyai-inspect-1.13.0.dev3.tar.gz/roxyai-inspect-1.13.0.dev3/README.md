# Roxy AI Inspect-Sever

検査サーバのモジュールです。

---

---
## 開発環境の構築方法
---

以下の順番でPython仮想環境を構築します。

### 1. 検査サーバ用のVSCワークスペースを開く

```
code .vscode\roxyai-inspect.code-workspace
```

### 2. Python仮想環境を構築する 

```
py -3.7 -m venv env
```

### 3. Python仮想環境にモジュールを設定する

```
env\Scripts\activate

python -m pip install --upgrade pip

pip install pipenv

pipenv sync --dev
```
pipenv により必要な Python モジュールが仮想環境に一通り組み込まれる


---
## パッケージ構築方法
---

### 1. Pythonコードの難読化

```
obfsucate.bat
```

VSCのタスク実行 [Ctrl]+[Shift]+[B] に登録済み

### 2. Wheelパッケージの生成とアップロード確認

Wheel生成と TestPyPI への登録までを実行
```
upload.bat
```

Wheel生成と開発リビジョン番号の更新と TestPyPI への登録までを実行
```
upload.bat -r
```

### 3. PyPIへのアップロード

Wheel生成と開発リビジョン番号の更新と PyPI への登録
```
upload.bat -U
```
