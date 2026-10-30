<div align="center">

**한국어** · [English](README.en.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

# nginx manager

**설정 파일을 직접 고치다 사이트를 내리는 일은 이제 그만. 브라우저에서 확인하고 적용하고, 실패하면 알아서 되돌립니다.**

nginx와 관리 화면을 컨테이너 두 개로 띄우는 웹 기반 nginx 관리도구

[![Release](https://img.shields.io/badge/release-v1.4.0-10b981.svg)](https://github.com/nginx-manager/app/releases/tag/v1.4.0)
[![nginx](https://img.shields.io/badge/nginx-1.31.8-009639.svg)](https://nginx.org/en/CHANGES)
[![Languages](https://img.shields.io/badge/UI-%ED%95%9C%EA%B5%AD%EC%96%B4%20%C2%B7%20English%20%C2%B7%20%E6%97%A5%E6%9C%AC%E8%AA%9E%20%C2%B7%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-0ea5e9.svg)](#4개-언어와-다크-모드)

[서버에 설치하기](#서버에-설치하기) · [주요 기능](#주요-기능) · [릴리스 노트](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md) · [저장소](https://github.com/nginx-manager/app)

</div>

<p align="center">
  <img src="images/dashboard.png" alt="nginx manager 대시보드" width="860" />
</p>

## 목차

- [왜 nginx manager인가](#왜-nginx-manager인가)
- [서버에 설치하기](#서버에-설치하기)
- [주요 기능](#주요-기능)
- [구성](#구성)
- [저장소](#저장소)
- [릴리스](#릴리스)

## 왜 nginx manager인가

| | 서버에서 직접 고치기 | nginx manager |
| --- | --- | --- |
| 사이트 추가 | 설정 파일을 손으로 작성 | 리버스 프록시·정적 사이트·TCP/UDP 스트림을 **폼으로**, 만들어질 설정을 바로 미리보기 |
| 반영 | `nginx -t` 후 reload, 실패하면 손으로 복구 | **diff 확인 → 검증 → reload → 상태 확인**, 어느 단계든 실패하면 **자동으로 직전 설정 복구** |
| 이력 | 백업 파일을 직접 관리 | 적용할 때마다 **버전**이 남고 비교·되돌리기, 서버에서 직접 바뀐 파일도 감지 |
| HTTPS | certbot 설치와 갱신 스케줄 | 사이트에서 HTTPS를 고르면 **Let's Encrypt 발급·적용·갱신**까지 자동 |
| 로그 | 서버에 접속해 `tail` | 사이트별 access/error 로그를 **화면에서 검색·실시간 보기** |
| 권한 | 서버 계정 공유 | 관리자와 멤버 역할, 멤버는 **담당 사이트만** 관리, **모든 변경은 감사 로그**에 기록 |

## 서버에 설치하기

준비물: Docker Engine과 Compose v2, sudo 권한, 비어 있는 80·443 포트. 관리 도메인을 쓰려면 그 도메인의 DNS가 서버를 가리키고 80번 포트가 인터넷에 열려 있어야 합니다.

아래 한 줄로 `/opt/nginx-manager`에 설치하고 바로 띄웁니다.

```bash
curl -fsSL https://github.com/nginx-manager/app/releases/latest/download/install.sh \
  | sudo sh -s -- --admin-domain nm.example.com --email ops@example.com
```

- `--admin-domain`을 주면 그 도메인으로 관리 화면을 엽니다. Let's Encrypt 인증서를 받고, 80은 443으로 넘기며, 관리 화면은 HTTPS로만 열립니다.
- 도메인 없이 설치하면 관리 화면은 서버 안의 `http://127.0.0.1:9000`에만 열립니다. 내 PC에서 `ssh -L 9000:127.0.0.1:9000 <서버>`로 연결한 뒤 `http://localhost:9000`을 엽니다.
- 처음 접속하면 최초 관리자 계정을 만드는 화면이 나옵니다.
- 서버에 있던 `/home/*/nginx` 설정을 가져오려면 `--import-root /home`을 붙여 설치하세요. 설치한 뒤에는 `./nm import-root add /home`으로 붙입니다.
- 그 밖의 옵션: `--version X.Y.Z`(버전 고정), `--dir`(설치 위치), `--http-port`, `--https-port`, `--manager-port`, `--bundle FILE`(인터넷이 안 되는 서버).

### 설정 (`/opt/nginx-manager/.env`)

설치하면 `/opt/nginx-manager/.env`가 만들어집니다. 고친 뒤에는 `./nm restart`로 다시 띄우고, nginx 포트를 바꿨다면 `./nm restart nginx`를 실행합니다.

| 변수 | 기본 | 언제 바꾸나 |
| --- | --- | --- |
| `MANAGER_VERSION`, `NGINX_IMAGE` | 설치한 버전 | 직접 고치지 않습니다. `nm upgrade`가 바꿉니다 |
| `NGINX_MANAGER_ADMIN_DOMAIN` | 비움 | 관리 화면을 `https://도메인`으로 열 때 |
| `NGINX_MANAGER_ADMIN_EMAIL` | 비움 | Let's Encrypt 연락 이메일 |
| `NGINX_MANAGER_ADMIN_ALLOW` | 비움(모두 허용) | 관리 도메인에 들어올 수 있는 주소를 CIDR로 제한할 때 |
| `NGINX_MANAGER_PORT` | `9000` | 9000번 포트를 이미 쓰고 있을 때 |
| `NGINX_MANAGER_BIND_ADDRESS` | `127.0.0.1` | 도메인 없이 사내망에서 열 때(`0.0.0.0`이나 사내 IP) |
| `NGINX_HTTP_PORT`, `NGINX_HTTPS_PORT` | `80`, `443` | 앞단 프록시가 있어 80/443을 쓸 수 없을 때 |
| `NGINX_BIND_ADDRESS` | `0.0.0.0` | nginx를 특정 IP에만 열 때 |
| `NGINX_MANAGER_BACKUP_KEEP` | `14` | `nm backup` 보관 개수 |
| `TZ` | `Asia/Seoul` | 시간대 |
| `NGINX_MANAGER_IMPORT_ROOTS` | 비움 | `/etc/nginx` 밖의 설정 파일을 가져올 때 |
| `SPRING_MAIL_*` | 비움 | 메일 알림에 쓸 SMTP 서버 |

### 운영 명령

```bash
cd /opt/nginx-manager
./nm status            # 상태와 버전
./nm restart           # .env를 고친 뒤 다시 띄우기
./nm upgrade           # 관리 화면만 새 버전으로 (nginx는 계속 트래픽을 받습니다)
./nm upgrade --nginx   # nginx도 새 버전으로 (새 nginx로 설정을 먼저 검증, 몇 초 재시작)
./nm backup            # 설정과 데이터베이스 백업
./nm restore backups/<파일>
./nm migrate           # v1.0·v1.1에서 옮겨 오기 (먼저 --no-start로 설치)
./nm import-root check # 가져올 디렉터리를 읽을 수 있는지 확인 (안 되면 grant로 읽기 권한)
```

자세한 내용은 [사용 설명서 1장 설치와 실행](https://github.com/nginx-manager/app/blob/main/src/main/resources/guide/ko/01-install.md)에 있습니다.

## 주요 기능

### 사이트를 폼으로

백엔드 여러 개(부하 분산), 웹소켓, 타임아웃, 리디렉션, HTTP/3까지 폼에서 정하고, 만들어질 nginx 설정을 옆에서 바로 봅니다. 폼으로 표현하지 않는 설정은 원문 편집기(nginx 문법 강조)로 고칩니다. 쓰지 않는 사이트는 지우고(v1.3.0), 삭제도 초안 → 적용을 거칩니다.

<p align="center"><img src="images/site-form.png" alt="사이트 추가 폼과 설정 미리보기" width="860" /></p>

### 쓰던 설정 파일 가져오기

`/home/*/nginx/*.conf`처럼 경로 패턴을 등록하면 맞는 파일을 모두 찾아 한꺼번에 사이트로 등록합니다. 폼으로 옮길 수 있으면 폼 사이트로, 아니면 원문 그대로 등록하고, 원본이 바뀌면 알려 줍니다.

<p align="center"><img src="images/import-scan.png" alt="설정 파일 가져오기" width="860" /></p>

### TCP/UDP 스트림

데이터베이스, MQTT처럼 HTTP가 아닌 서비스도 포트 단위로 넘깁니다.

<p align="center"><img src="images/stream-form.png" alt="스트림 추가 폼" width="860" /></p>

### 확인하고 적용하기

저장한 초안은 파일별 diff로 확인한 뒤 반영합니다. 검증·reload·상태 확인 중 하나라도 실패하면 직전 설정으로 돌아갑니다.

<p align="center"><img src="images/apply-diff.png" alt="적용 전 변경 내용" width="860" /></p>

### 이력과 되돌리기

적용할 때마다 버전이 남고, 두 버전을 비교하거나 이전 버전으로 되돌립니다. 사이트 화면에서 그 사이트가 바뀐 버전만 모아 보고, 멤버도 담당 사이트의 이력을 봅니다. 같은 내용은 한 번만 저장해 버전이 쌓여도 DB가 크게 늘지 않습니다(v1.3.0).

<p align="center"><img src="images/version-diff.png" alt="두 버전 비교" width="860" /></p>

### HTTPS 인증서

Let's Encrypt 인증서를 자동으로 받고 만료 전에 갱신합니다. 갱신에 실패하면 메일·웹훅으로 알립니다. 와일드카드·사내 인증서는 업로드합니다. 설정 파일 가져오기로 들여온 원문 사이트도 인증서를 받아 443 server 블록과 80→443 넘기기를 초안으로 더합니다(v1.2.3).

<p align="center"><img src="images/certs.png" alt="인증서 목록" width="860" /></p>

### 로그

사이트별 access/error 로그를 검색하거나 실시간으로 봅니다. 가져온 원문 사이트의 로그와 밀려난 지난 로그도 읽습니다(v1.3.0).

<p align="center"><img src="images/logs.png" alt="사이트 로그 보기" width="860" /></p>

### 4개 언어와 다크 모드

화면을 한국어·영어·일본어·중국어(간체)로 볼 수 있고, 어두운 테마로 바꿀 수 있습니다.

<p align="center"><img src="images/sites-en.png" alt="영어로 본 사이트 목록" width="860" /></p>

## 구성

| 컨테이너 | 이미지 | 하는 일 |
| --- | --- | --- |
| `nginx` | `ghcr.io/nginx-manager/nginx` | nginx(오픈소스, 전체 모듈 빌드)와 에이전트. 에이전트는 관리 화면의 요청으로 `nginx -t`·reload만 실행합니다 |
| `manager` | `ghcr.io/nginx-manager/app` | 관리 화면(Spring Boot). 설정 파일은 공유 볼륨에 직접 쓰고, 검증·reload는 에이전트에 맡깁니다 |

관리 화면을 업데이트하거나 다시 띄워도 nginx는 계속 트래픽을 받습니다. 새 nginx 이미지는 nginx를 띄우기 전에 볼륨의 설정을 검증하고, 맞지 않으면 관리 화면이 문제의 파일·줄을 보여 줍니다. nginx 새 릴리스가 나오면 nginx 이미지가 자동으로 다시 빌드·테스트·게시되고, 이전 태그는 그대로 남습니다.

## 저장소

| 저장소 | 설명 |
| --- | --- |
| [app](https://github.com/nginx-manager/app) | 관리 화면(Spring Boot), nginx 이미지와 에이전트(Go), 설치 묶음, 릴리스 노트 |

## 릴리스

버전은 git 태그(`vX.Y.Z`)로 관리하고, 1.0.0부터 시작합니다. 버전마다 [릴리스 노트](https://github.com/nginx-manager/app/blob/main/docs/releases/README.md)에 바뀐 내용과 화면을 정리하고, [GitHub Releases](https://github.com/nginx-manager/app/releases)에도 올립니다. 지금 쓰는 버전은 관리 화면 아래(footer)에 보입니다.

<!-- releases:start -->
| 버전 | 날짜 | 주요 내용 | 릴리스 노트 |
| --- | --- | --- | --- |
| v1.4.0 | 2026-10-30 | 로그인 2단계 인증(TOTP, 복구 코드, `nm reset-2fa`), PHP(PHP-FPM) 사이트, 외부 인증(auth_request, SSO 로그인 주소)과 gRPC 프록시, 매일 자동 백업과 대시보드 마지막 백업, 화면 용어 정리 | [v1.4.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.4.0.md) |
| v1.3.0 | 2026-10-30 | 사이트 지우기(삭제 초안 → 적용, 쓰지 않는 인증서 지우기), 사이트별 변경 이력과 멤버의 담당 사이트 이력 보기, 원문 사이트 로그·사이트별 로그로 남기기·지난 로그, 같은 내용은 한 번만 저장하는 버전 저장, 원문 사이트 HTTPS 버그 수정 | [v1.3.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.3.0.md) |
| v1.2.3 | 2026-10-30 | 원문 사이트에도 Let's Encrypt(인증 경로 초안 → 발급 → 443 server 블록과 80→443 넘기기 초안), 인증서 화면 탭·실패 인증서 삭제, 변경 이력 비교 칸 나눔 | [v1.2.3](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.3.md) |
| v1.2.2 | 2026-10-30 | 서버에서 `sudo`로 만든 디렉터리 때문에 적용이 실패하고 manager가 뜨지 않던 문제(시작할 때 소유자 맞추기, 복구 실패해도 시작) | [v1.2.2](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.2.md) |
| v1.2.1 | 2026-10-30 | 관리 도메인 점검(`nm check-domain`), 인증서를 받으면 바로 HTTPS, 적용 실패 이유를 화면에 표시, Certbot 인증서를 그대로 쓰기(`/etc/letsencrypt` 붙이기, `nm reload`) | [v1.2.1](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.1.md) |
| v1.2.0 | 2026-10-30 | 서버에 한 줄로 설치(`install.sh`, `nm` 명령, 관리 도메인 HTTPS, `nm import-root`), 사용자별 사이트 관리(관리자·멤버 역할, 사이트 담당자), 새 로그인·최초 설정 화면, 관리 화면 안에서 보는 사용 설명서 13장, 브라우저 탭 아이콘 | [v1.2.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.2.0.md) |
| v1.1.0 | 2026-10-29 | 쓰던 nginx 설정 파일을 사이트로 가져오기: 경로 패턴(`/home/*/nginx/*.conf`)으로 찾아 한꺼번에 등록, 폼/원문 자동 판단, 원본 바뀜 알림과 다시 가져오기. 화면 다듬기: 고른 유형만 보이는 사이트 폼, 놓치지 않는 미리보기, 대상이 보이는 사이트 목록, 접히는 적용 diff, 휴대폰 메뉴 버튼 | [v1.1.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.1.0.md) |
| v1.0.0 | 2026-10-29 | 첫 정식 릴리스: 폼으로 사이트·TCP/UDP 스트림 만들기, 검증 후 적용과 자동 복구, 이력·비교·되돌리기, Let's Encrypt 자동 발급·갱신, 대시보드와 로그, 4개 언어·다크 모드, 사용자·감사 로그, 컨테이너 두 개와 업그레이드 안전장치 | [v1.0.0](https://github.com/nginx-manager/app/blob/main/docs/releases/v1.0.0.md) |
<!-- releases:end -->
