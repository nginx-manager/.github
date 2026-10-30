<div align="center">

[한국어](README.md) · [English](README.en.md) · **日本語** · [简体中文](README.zh-CN.md)

# nginx manager

**設定ファイルを直接いじってサイトを落とすのはもう終わり。ブラウザで確認して適用し、失敗したら自動で元に戻します。**

nginx と管理画面を 2 つのコンテナで動かす Web ベースの nginx 管理ツール

[![Release](https://img.shields.io/badge/release-v1.2.0-10b981.svg)](https://github.com/nginx-manager/app/releases/tag/v1.2.0)
[![nginx](https://img.shields.io/badge/nginx-1.31.8-009639.svg)](https://nginx.org/en/CHANGES)
[![Languages](https://img.shields.io/badge/UI-%ED%95%9C%EA%B5%AD%EC%96%B4%20%C2%B7%20English%20%C2%B7%20%E6%97%A5%E6%9C%AC%E8%AA%9E%20%C2%B7%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-0ea5e9.svg)](#4-言語とダークモード)

[サーバーにインストール](#サーバーにインストール) · [主な機能](#主な機能) · [リリースノート](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md) · [リポジトリ](https://github.com/nginx-manager/app)

</div>

<p align="center">
  <img src="images/dashboard.png" alt="nginx manager のダッシュボード" width="860" />
</p>

## 目次

- [なぜ nginx manager か](#なぜ-nginx-manager-か)
- [サーバーにインストール](#サーバーにインストール)
- [主な機能](#主な機能)
- [構成](#構成)
- [リポジトリ](#リポジトリ)
- [リリース](#リリース)

## なぜ nginx manager か

| | サーバーで直接編集 | nginx manager |
| --- | --- | --- |
| サイト追加 | 設定ファイルを手で書く | リバースプロキシ・静的サイト・TCP/UDP ストリームを**フォームで**作成し、生成される設定をすぐにプレビュー |
| 反映 | `nginx -t` の後に reload、失敗したら手で復旧 | **diff 確認 → 検証 → reload → 状態確認**、どの段階で失敗しても**直前の設定を自動で復元** |
| 履歴 | バックアップファイルを自分で管理 | 適用のたびに**バージョン**が残り、比較・ロールバックが可能。サーバーで直接変更されたファイルも検出 |
| HTTPS | certbot のインストールと更新スケジュール | サイトで HTTPS を選ぶと **Let's Encrypt の発行・適用・更新**まで自動 |
| ログ | サーバーに入って `tail` | サイトごとの access/error ログを**画面で検索・リアルタイム表示** |
| 権限 | サーバーアカウントを共有 | 管理者とメンバーのロール。メンバーは**担当サイトだけ**を管理し、**すべての変更は監査ログ**に記録 |

## サーバーにインストール

必要なもの: Docker Engine と Compose v2、sudo 権限、空いている 80・443 番ポート。管理ドメインを使う場合は、そのドメインの DNS がサーバーを指し、80 番ポートがインターネットから届く必要があります。

次の 1 行で `/opt/nginx-manager` にインストールしてすぐに起動します。

```bash
curl -fsSL https://github.com/nginx-manager/app/releases/latest/download/install.sh \
  | sudo sh -s -- --admin-domain nm.example.com --email ops@example.com
```

- `--admin-domain` を指定すると、そのドメインで管理画面を開きます。Let's Encrypt 証明書を取得し、80 番は 443 番へリダイレクトし、管理画面は HTTPS でのみ開きます。
- ドメインなしでインストールすると、管理画面はサーバー内の `http://127.0.0.1:9000` でのみ開きます。手元の PC から `ssh -L 9000:127.0.0.1:9000 <サーバー>` で接続し、`http://localhost:9000` を開きます。
- 最初にアクセスすると、最初の管理者アカウントを作る画面が表示されます。
- サーバーにある `/home/*/nginx` の設定を取り込むには、`--import-root /home` を付けてインストールします。インストール後は `./nm import-root add /home` で追加します。
- その他のオプション: `--version X.Y.Z`(バージョン固定)、`--dir`(インストール先)、`--http-port`、`--https-port`、`--manager-port`、`--bundle FILE`(インターネットにつながらないサーバー)。

### 設定 (`/opt/nginx-manager/.env`)

インストールすると `/opt/nginx-manager/.env` が作られます。編集した後は `./nm restart` で再起動し、nginx のポートを変えた場合は `./nm restart nginx` を実行します。

| 変数 | 既定値 | 変えるとき |
| --- | --- | --- |
| `MANAGER_VERSION`, `NGINX_IMAGE` | インストールしたバージョン | 直接編集しません。`nm upgrade` が変更します |
| `NGINX_MANAGER_ADMIN_DOMAIN` | 空 | 管理画面を `https://ドメイン` で開くとき |
| `NGINX_MANAGER_ADMIN_EMAIL` | 空 | Let's Encrypt の連絡先メール |
| `NGINX_MANAGER_ADMIN_ALLOW` | 空(すべて許可) | 管理ドメインに入れるアドレスを CIDR で制限するとき |
| `NGINX_MANAGER_PORT` | `9000` | 9000 番ポートがすでに使われているとき |
| `NGINX_MANAGER_BIND_ADDRESS` | `127.0.0.1` | ドメインなしで社内ネットワークに開くとき(`0.0.0.0` または社内 IP) |
| `NGINX_HTTP_PORT`, `NGINX_HTTPS_PORT` | `80`, `443` | 前段のプロキシがあり 80/443 を使えないとき |
| `NGINX_BIND_ADDRESS` | `0.0.0.0` | nginx を特定の IP だけで開くとき |
| `NGINX_MANAGER_BACKUP_KEEP` | `14` | `nm backup` の保存数 |
| `TZ` | `Asia/Seoul` | タイムゾーン |
| `NGINX_MANAGER_IMPORT_ROOTS` | 空 | `/etc/nginx` の外にある設定ファイルを取り込むとき |
| `SPRING_MAIL_*` | 空 | メール通知に使う SMTP サーバー |

### 運用コマンド

```bash
cd /opt/nginx-manager
./nm status            # 状態とバージョン
./nm restart           # .env を編集した後の再起動
./nm upgrade           # 管理画面だけを新しいバージョンに(nginx はトラフィックを受け続けます)
./nm upgrade --nginx   # nginx も新しいバージョンに(新しい nginx で先に設定を検証し、数秒で再起動)
./nm backup            # 設定とデータベースのバックアップ
./nm restore backups/<ファイル>
./nm migrate           # v1.0・v1.1 からの移行(先に --no-start でインストール)
./nm import-root check # 取り込むディレクトリを読めるか確認(読めなければ grant で読み取り権限)
```

詳しくは[ユーザーガイド 1 章 インストールと起動](https://github.com/nginx-manager/app/blob/main/src/main/resources/guide/ko/01-install.md)(韓国語)にあります。

## 主な機能

### フォームでサイトを作成

複数のバックエンド(負荷分散)、WebSocket、タイムアウト、リダイレクト、HTTP/3 までフォームで設定し、生成される nginx 設定を横ですぐに確認できます。フォームで表せない設定は、nginx 構文ハイライト付きの原文エディターで編集します。

<p align="center"><img src="images/site-form.png" alt="サイト追加フォームと設定プレビュー" width="860" /></p>

### 既存の設定ファイルを取り込む

`/home/*/nginx/*.conf` のようなパスパターンを登録すると、一致するファイルをすべて見つけて一度にサイトとして登録します。フォームに移せるものはフォームサイト、それ以外は原文のまま登録し、元のファイルが変わると知らせます。

<p align="center"><img src="images/import-scan.png" alt="設定ファイルの取り込み" width="860" /></p>

### TCP/UDP ストリーム

データベースや MQTT のような HTTP 以外のサービスも、ポート単位で転送します。

<p align="center"><img src="images/stream-form.png" alt="ストリーム追加フォーム" width="860" /></p>

### 確認してから適用

保存した下書きはファイルごとの diff で確認してから反映します。検証・reload・状態確認のどれかが失敗すると、直前の設定に戻ります。

<p align="center"><img src="images/apply-diff.png" alt="適用前の変更内容" width="860" /></p>

### 履歴とロールバック

適用のたびにバージョンが残り、2 つのバージョンを比較したり、以前のバージョンに戻したりできます。

<p align="center"><img src="images/version-diff.png" alt="2 つのバージョンの比較" width="860" /></p>

### HTTPS 証明書

Let's Encrypt 証明書を自動で取得し、期限切れ前に更新します。更新に失敗するとメールや Webhook で知らせます。ワイルドカード証明書や社内証明書はアップロードできます。

<p align="center"><img src="images/certs.png" alt="証明書一覧" width="860" /></p>

### ログ

サイトごとの access/error ログを検索したり、リアルタイムで表示したりできます。

<p align="center"><img src="images/logs.png" alt="サイトのログ表示" width="860" /></p>

### 4 言語とダークモード

画面を韓国語・英語・日本語・中国語(簡体字)で表示でき、ダークテーマに切り替えられます。

<p align="center"><img src="images/sites-en.png" alt="英語で表示したサイト一覧" width="860" /></p>

## 構成

| コンテナ | イメージ | 役割 |
| --- | --- | --- |
| `nginx` | `ghcr.io/nginx-manager/nginx` | nginx(オープンソース、全モジュールビルド)とエージェント。エージェントは管理画面の要求で `nginx -t` と reload だけを実行します |
| `manager` | `ghcr.io/nginx-manager/app` | 管理画面(Spring Boot)。設定ファイルは共有ボリュームに直接書き込み、検証と reload はエージェントに任せます |

管理画面を更新・再起動しても、nginx はトラフィックを受け続けます。新しい nginx イメージは nginx を起動する前にボリュームの設定を検証し、合わない場合は管理画面が問題のファイルと行を表示します。nginx の新しいリリースが出ると nginx イメージが自動で再ビルド・テスト・公開され、以前のタグもそのまま残ります。

## リポジトリ

| リポジトリ | 説明 |
| --- | --- |
| [app](https://github.com/nginx-manager/app) | 管理画面(Spring Boot)、nginx イメージとエージェント(Go)、インストールバンドル、リリースノート |

## リリース

バージョンは git タグ(`vX.Y.Z`)で管理し、1.0.0 から始まります。バージョンごとの変更点と画面は[リリースノート](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md)(韓国語)と [GitHub Releases](https://github.com/nginx-manager/app/releases) にまとめています。使用中のバージョンは管理画面の下部(footer)に表示されます。

<!-- releases:start -->
| バージョン | 日付 | リリースノート |
| --- | --- | --- |
| v1.2.0 | 2026-10-30 | [v1.2.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.0.md) |
| v1.1.0 | 2026-10-29 | [v1.1.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.1.0.md) |
| v1.0.0 | 2026-10-29 | [v1.0.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.0.0.md) |
<!-- releases:end -->
