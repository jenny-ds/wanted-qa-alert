# QA 채용 알리미

원티드와 리멤버에서 QA 채용 공고를 매일 오전 9시에 자동으로 수집하고, 전날과 비교해 새로운 공고와 마감된 공고를 이메일로 알려주는 서비스입니다.

## 검색 조건

### 원티드
- **검색어**: QA · **경력**: 3~7년 · **지역**: 서울/인천/경기 · **정렬**: 최신순

### 리멤버
- **검색어**: QA · **필터**: 없음 · **정렬**: 최신순 (최근 1,000개 기준)

## 동작 방식

1. 매일 오전 9시 (KST) GitHub Actions가 자동 실행
2. 원티드/리멤버 API로 공고 목록 수집 → `data/{source}_YYYY-MM-DD.json`으로 저장
3. 어제 스냅샷과 비교해 신규/마감 공고 추출
4. 결과를 하나의 HTML 이메일로 합산 발송

## 설치 및 설정

### 1. 저장소 Fork 또는 Clone

```bash
git clone https://github.com/jenny-ds/qa-job-alert.git
cd qa_job_alert
```

### 2. Gmail 앱 비밀번호 발급

Gmail은 일반 비밀번호로 SMTP 접속이 불가합니다. 앱 비밀번호를 발급해야 합니다.

1. [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 접속
2. 앱 선택 → **기타** → 이름 입력 (예: `qa-job-alert`)
3. 생성된 16자리 비밀번호 복사

### 3. GitHub Secrets 등록

저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | 설명 |
|------|------|
| `SMTP_USER` | 발신 Gmail 주소 |
| `SMTP_PASS` | Gmail 앱 비밀번호 (16자리, 띄어쓰기 없이) |
| `ALERT_TO` | 수신 이메일 주소 |

### 4. 수동 테스트

저장소 → **Actions** → **QA Alert (Wanted + Remember)** → **Run workflow**

이메일이 오면 설정 완료입니다.

## 로컬 실행

```bash
# 의존성 설치
pip install requests

# .env 파일 생성
cp .env.example .env
# .env 파일을 열어 SMTP 정보 입력

# 실행
set -a && source .env && set +a
python main.py
```

## 파일 구조

```
├── main.py               # 진입점
├── fetcher.py            # 원티드 API 공고 수집
├── remember_fetcher.py   # 리멤버 API 공고 수집
├── store.py              # 날짜별 스냅샷 저장/로드 (data/{source}_YYYY-MM-DD.json)
├── compare.py            # 어제/오늘 공고 비교
├── notifier.py           # HTML 이메일 발송 (원티드 + 리멤버 합산)
├── run.sh                # 로컬 cron 실행용 래퍼
└── .github/
    └── workflows/
        └── daily_alert.yml  # GitHub Actions 스케줄
```
