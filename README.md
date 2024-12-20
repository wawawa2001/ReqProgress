# 依頼進捗状況シェアアプリ

## 概要
このプロジェクトは、クライアントから受けた依頼タスクの進捗状況を管理・共有するためのウェブアプリケーションです。Flask を使用して開発され、PostgreSQL データベースと連携しています。

## 主な機能
1. **タスクの表示と管理**
   - `/req` エンドポイントで特定のタスク情報を取得し表示します。
   - `/manage` エンドポイントで特定の管理者に関連するタスクを一覧表示します。

2. **タスクの編集と削除**
   - `/reqedit` エンドポイントでタスクの作成、編集を行います。
   - `/delete` エンドポイントでタスクを削除します。

3. **進捗のリアルタイム共有**
   - クライアントに進捗状況をタイムリーに共有するためのインターフェースを提供します。

4. **ロギング**
   - アプリケーションの動作状況を詳細に記録するロギング機能を備えています。
   - ログはファイルとコンソールに出力されます。

## ファイル構成
- `main.py` : メインの Flask アプリケーション。
- `templates/` : HTML テンプレートを格納するディレクトリ。
- `static/` : CSS, FONTを格納するディレクトリ。
- `app.log` : アプリケーションのログファイル。
- `requiments.txt` : ライブラリ情報
- `schema.sql` : テーブルスキーマ

## 必要要件
- Python 3.9以上

## 画面イメージ

### TOPページ

<img width="700" alt="image" src="https://github.com/user-attachments/assets/b91f62ac-e452-463d-938c-eb8cecb75ea7" />

### クリエイター管理画面

<img width="700" alt="image" src="https://github.com/user-attachments/assets/a3305b0b-a88d-4355-a97c-1638439c4a59" />

### 各依頼 管理画面

<img width="700" alt="image" src="https://github.com/user-attachments/assets/48dc019f-3f3b-4fce-b159-af2e3ccf6693" />

### 入力例

<img width="700" alt="image" src="https://github.com/user-attachments/assets/c8ee668d-522e-4b00-811c-edf160b43db9" />

### クライアント側画面（PC例）

<img width="700" alt="image" src="https://github.com/user-attachments/assets/39b0f029-314e-49c6-b0cd-b890f3402949" />

### クライアント側画面（スマホ例）

<img width="215" alt="image" src="https://github.com/user-attachments/assets/b3dad3bd-90e0-4838-b506-242b20d70a3c" />


## セットアップ手順
1. **依存関係のインストール**
    ```bash
    pip install -r requiments.txt
    ```

2. **データベースの設定**
   - PostgreSQLでデータベースを作成し、main.pyの`app.config['SQLALCHEMY_DATABASE_URI']` の値を適切に設定します。
   - テーブルはschema.sqlで作成できます。
   - その後、main.pyで`app.config['SQLALCHEMY_DATABASE_URI']` の値を適切に設定

3. **アプリケーションの起動**
    ```bash
    python3 main.py
    ```

4. **アクセス**
   - ブラウザで `http://localhost:8001` にアクセスします。
   - ルータ設定後に外部公開も可能です。

## エンドポイントの詳細
### `/`
- **概要**: トップページを表示します。
- **HTTP メソッド**: GET

### `/delete`
- **概要**: 指定された `mgr_id` と `req_id` に基づいてタスクを削除します。
- **HTTP メソッド**: GET
- **パラメータ**:
  - `id` : 管理者 ID
  - `req_id` : タスク ID

### `/req`
- **概要**: タスクの詳細を表示します。
- **HTTP メソッド**: GET
- **パラメータ**:
  - `req_id` : タスク ID

### `/manage`
- **概要**: 指定された管理者 ID に関連するタスクを一覧表示します。
- **HTTP メソッド**: GET
- **パラメータ**:
  - `id` : 管理者 ID

### `/reqedit`
- **概要**: タスクを編集または新規作成します。
- **HTTP メソッド**: GET, POST
- **パラメータ**:
  - `id` : 管理者 ID
  - `req_id` : タスク ID

## ロギングについて
- ログは `app.log` ファイルに記録され、アプリケーションのデバッグや監視に利用できます。
- **ログレベル**: DEBUG, INFO, WARNING, ERROR

## 注意事項
- main.pyにて、SSL 証明書 (`cert.pem` と `privkey.pem`) を適切に設定する必要があります。
- PostgreSQL データベースを作成し、main.pyの`app.config['SQLALCHEMY_DATABASE_URI']` の値を適切に設定します。

## トラブルシューティング
- **データベース接続エラー**:
  - データベースの URI が正しいか確認してください。
- **500 エラー**:
  - ログ (`app.log`) を確認してエラーの詳細を特定してください。

## ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。
