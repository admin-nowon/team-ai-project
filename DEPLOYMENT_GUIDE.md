# 팀 AI 업무 처리 시스템 - 배포 및 운영 가이드

## 📋 목차
1. [로컬 환경 설정](#로컬-환경-설정)
2. [자체 도메인 서버 배포](#자체-도메인-서버-배포)
3. [운영 및 모니터링](#운영-및-모니터링)
4. [보안 설정](#보안-설정)
5. [트러블슈팅](#트러블슈팅)

---

## 로컬 환경 설정

### 1단계: 환경 준비

```bash
# 프로젝트 디렉토리 생성
mkdir team-ai-project
cd team-ai-project

# Python 가상환경 생성 (Python 3.9+ 필요)
python3 -m venv venv

# 가상환경 활성화
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2단계: 의존성 설치

```bash
# requirements.txt에서 설치
pip install -r requirements.txt
```

### 3단계: API 키 설정

```bash
# .env 파일 생성
cat > .env << EOF
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# OpenAI API
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Flask
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=development
EOF

# Windows PowerShell:
# notepad .env  (또는 editor 로 수동 생성)
```

**API 키 발급:**
- **Claude API**: https://console.anthropic.com/account/keys
- **OpenAI API**: https://platform.openai.com/account/api-keys

### 4단계: 로컬 테스트

```bash
# 개발 서버 실행
python app.py

# 브라우저에서 접속
# http://localhost:5000

# 테스트 계정
# ID: admin, PW: admin123
```

---

## 자체 도메인 서버 배포

### 추천 클라우드 인프라

| 제공자 | 가격 | 특징 | 추천 사양 |
|--------|------|------|---------|
| **AWS EC2** | $5-20/월 | 안정적, 확장성 | t3.micro |
| **Google Cloud** | $5-20/월 | 빠른 배포 | e2-micro |
| **Azure** | $5-20/월 | Windows 지원 | B1s |
| **DigitalOcean** | $4-12/월 | 단순함 | Basic Droplet |
| **Linode** | $5-15/월 | 빠른 네트워크 | Nanode |

**추천**: DigitalOcean (가장 간단)

---

### DigitalOcean 배포 (자세한 가이드)

#### 1단계: Droplet 생성

```
1. https://www.digitalocean.com 접속 → 회원가입
2. Create → Droplets
3. Image: Ubuntu 22.04 LTS
4. Size: Basic / $4/월 (512MB RAM, 10GB SSD)
5. Region: Singapore (한국 근처)
6. Add SSH key (또는 password 설정)
7. Create Droplet → IP 주소 메모
```

#### 2단계: 서버 접속 및 초기 설정

```bash
# SSH로 접속 (Windows는 PuTTY 사용)
ssh root@your-droplet-ip

# 시스템 업데이트
apt update && apt upgrade -y

# 필수 패키지 설치
apt install -y python3-pip python3-venv git nginx curl certbot python3-certbot-nginx

# 타임존 설정 (서울)
timedatectl set-timezone Asia/Seoul

# 방화벽 설정
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

#### 3단계: 애플리케이션 배포

```bash
# 프로젝트 디렉토리 생성
mkdir -p /opt/team-ai
cd /opt/team-ai

# GitHub에서 클론 (또는 수동으로 업로드)
git clone https://github.com/your-username/team-ai.git .
# 또는:
# scp -r ./team-ai-project/* root@your-ip:/opt/team-ai/

# 가상환경 설정
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 파일 생성
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=production
EOF

# 권한 설정
chown -R www-data:www-data /opt/team-ai
chmod -R 750 /opt/team-ai
```

#### 4단계: Nginx 설정 (리버스 프록시)

```bash
# Nginx 설정 파일 생성
cat > /etc/nginx/sites-available/team-ai << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 타임아웃 설정 (AI 응답 대기)
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# 설정 활성화
ln -s /etc/nginx/sites-available/team-ai /etc/nginx/sites-enabled/

# 기본 설정 비활성화
rm /etc/nginx/sites-enabled/default

# Nginx 문법 확인 및 재시작
nginx -t
systemctl restart nginx
```

#### 5단계: 도메인 연결

```bash
# DNS 설정 (도메인 레지스트라)
# A 레코드: your-domain.com → droplet-ip
# CNAME: www.your-domain.com → your-domain.com

# 테스트 (10분 정도 소요)
ping your-domain.com
```

#### 6단계: SSL/TLS 인증서 설치 (HTTPS)

```bash
# Let's Encrypt 인증서 자동 설치
certbot --nginx -d your-domain.com -d www.your-domain.com

# 인증서 자동 갱신 설정
systemctl enable certbot.timer
systemctl start certbot.timer

# 갱신 테스트
certbot renew --dry-run
```

#### 7단계: Gunicorn + Systemd 설정

```bash
# Systemd 서비스 파일 생성
cat > /etc/systemd/system/team-ai.service << EOF
[Unit]
Description=Team AI Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/team-ai
Environment="PATH=/opt/team-ai/venv/bin"
ExecStart=/opt/team-ai/venv/bin/gunicorn \
    --workers=4 \
    --worker-class=gevent \
    --bind=127.0.0.1:8000 \
    --access-logfile=/var/log/team-ai/access.log \
    --error-logfile=/var/log/team-ai/error.log \
    --log-level=info \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 로그 디렉토리 생성
mkdir -p /var/log/team-ai
chown www-data:www-data /var/log/team-ai

# 서비스 시작
systemctl daemon-reload
systemctl enable team-ai
systemctl start team-ai

# 상태 확인
systemctl status team-ai
```

#### 8단계: 배포 완료 확인

```bash
# 로그 확인
tail -f /var/log/team-ai/error.log

# 서비스 상태
systemctl status team-ai

# Nginx 상태
systemctl status nginx

# 브라우저 접속
# https://your-domain.com
```

---

## 운영 및 모니터링

### 로그 관리

```bash
# 실시간 로그 확인
tail -f /var/log/team-ai/error.log
tail -f /var/log/team-ai/access.log

# 로그 크기 제한 (logrotate)
cat > /etc/logrotate.d/team-ai << EOF
/var/log/team-ai/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
EOF
```

### 정기 백업

```bash
# 데이터베이스 백업 스크립트
cat > /opt/team-ai/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/team-ai/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 디렉토리 생성
mkdir -p $BACKUP_DIR

# SQLite 백업
cp /opt/team-ai/team_ai_usage.db $BACKUP_DIR/team_ai_usage_$TIMESTAMP.db.bak

# 7일 이상된 백업 삭제
find $BACKUP_DIR -name "*.bak" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/team_ai_usage_$TIMESTAMP.db.bak"
EOF

# 실행 권한 설정
chmod +x /opt/team-ai/backup.sh

# 정기 실행 (매일 밤 2시)
crontab -e
# 추가 라인: 0 2 * * * /opt/team-ai/backup.sh
```

### 모니터링 및 알림

```bash
# 간단한 헬스 체크 스크립트
cat > /opt/team-ai/health_check.sh << 'EOF'
#!/bin/bash

URL="https://your-domain.com"
MAX_RETRIES=3
RETRY_COUNT=0

check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" $URL/login)
    return $response
}

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    status=$(check_health)
    
    if [ "$status" == "200" ]; then
        echo "✅ Service is healthy"
        exit 0
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 5
done

echo "❌ Service is down! Status: $status"
# 여기에 알림 로직 추가 (이메일, Slack 등)
exit 1
EOF

# 5분마다 실행
crontab -e
# 추가 라인: */5 * * * * /opt/team-ai/health_check.sh
```

### 리소스 모니터링

```bash
# 서버 리소스 확인
free -h              # 메모리
df -h               # 디스크
top -b -n 1        # CPU 사용률

# 프로세스 확인
ps aux | grep gunicorn
ps aux | grep nginx

# 네트워크 확인
netstat -tulpn | grep 8000
```

---

## 보안 설정

### 1. SSH 보안

```bash
# SSH 설정 파일
nano /etc/ssh/sshd_config

# 변경사항:
Port 2222                          # 기본 포트 변경
PermitRootLogin no                 # root 로그인 금지
PasswordAuthentication no           # 키 인증만 허용
PubkeyAuthentication yes

# 재시작
systemctl restart sshd

# SSH 포트 방화벽 업데이트
ufw allow 2222/tcp
ufw delete allow 22/tcp
```

### 2. 데이터 암호화

```python
# .env 파일 권한 설정
chmod 600 /opt/team-ai/.env

# 환경변수 암호화 (선택)
# pip install python-dotenv-vault
```

### 3. API 키 보호

```bash
# API 키는 절대 코드에 포함하지 않기
# .env 파일만 사용

# 샘플 파일 생성 (.env.example)
cat > /opt/team-ai/.env.example << EOF
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=production
EOF
```

### 4. 방화벽 규칙

```bash
# UFW 방화벽 설정
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp          # SSH
ufw allow 80/tcp          # HTTP
ufw allow 443/tcp         # HTTPS
ufw enable

# 특정 IP만 허용 (선택)
# ufw allow from 192.168.1.0/24 to any port 22
```

### 5. Rate Limiting (DDoS 방지)

```bash
# Nginx 설정에 추가
cat >> /etc/nginx/sites-available/team-ai << 'EOF'

limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
    }
}
EOF

systemctl restart nginx
```

---

## 트러블슈팅

### 1. 포트 충돌

```bash
# 포트 사용 확인
lsof -i :8000
netstat -tulpn | grep 8000

# 프로세스 강제 종료
kill -9 <PID>
```

### 2. 메모리 부족

```bash
# 메모리 상황 확인
free -h

# Swap 메모리 생성
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 3. 데이터베이스 오류

```bash
# SQLite 복구
sqlite3 /opt/team-ai/team_ai_usage.db "PRAGMA integrity_check;"

# 무결성 확인
sqlite3 /opt/team-ai/team_ai_usage.db "PRAGMA integrity_check;"

# 백업에서 복구
cp /opt/team-ai/backups/team_ai_usage_*.db.bak /opt/team-ai/team_ai_usage.db
```

### 4. API 연결 오류

```bash
# API 키 확인
cat /opt/team-ai/.env

# 네트워크 연결 테스트
curl -X GET https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json"

# 로그 확인
tail -100 /var/log/team-ai/error.log
```

### 5. SSL 인증서 오류

```bash
# 인증서 만료 확인
openssl s_client -connect your-domain.com:443

# 수동 갱신
certbot renew --force-renewal

# 인증서 상세 정보
certbot certificates
```

---

## Phase 1 → Phase 2 마이그레이션 준비

### 향후 확장 (6-12개월 후)

```bash
# 로컬 LLM 설정 (Ollama)
curl https://ollama.ai/install.sh | sh
ollama pull llama2

# 하이브리드 매니저 설치
pip install ollama

# Phase 2 코드로 업그레이드 (추후 제공)
```

---

## 체크리스트

배포 전 확인사항:

- [ ] API 키 발급 완료 (Claude, OpenAI)
- [ ] 도메인 구매 및 DNS 설정
- [ ] 클라우드 서버 생성 (DigitalOcean 등)
- [ ] SSH 키 쌍 생성
- [ ] 로컬에서 테스트 완료
- [ ] 환경변수 파일 설정
- [ ] SSL 인증서 설치
- [ ] 백업 정책 수립
- [ ] 모니터링 설정
- [ ] 팀 멤버에게 액세스 권한 배분

---

## 지원 및 유지보수

```bash
# 정기 점검
# - 매주: 로그 검토, 성능 확인
# - 매달: 백업 테스트, 업데이트 확인
# - 분기: 보안 감사, 비용 최적화

# 자동화 스크립트
# /opt/team-ai/scripts/weekly_health_check.sh
# /opt/team-ai/scripts/monthly_backup_verify.sh
```

---

**문제 발생 시:**
1. 로그 확인: `/var/log/team-ai/error.log`
2. 서비스 상태: `systemctl status team-ai`
3. 재시작: `systemctl restart team-ai`
