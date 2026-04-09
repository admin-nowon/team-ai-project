# 🚀 팀 AI 업무 처리 시스템 - 5분 빠른 시작

이 가이드를 따라 5분 안에 시스템을 구동할 수 있습니다.

---

## 📋 요구사항

- Python 3.9 이상
- API 키 (Claude, OpenAI)
- 자신의 도메인 (향후)

---

## ⚡ 3단계 빠른 시작

### Step 1️⃣: API 키 발급 (3분)

#### Claude API 키 발급
```
1. https://console.anthropic.com/account/keys 접속
2. "Create Key" 클릭
3. 키 복사 및 저장
```

#### OpenAI API 키 발급
```
1. https://platform.openai.com/account/api-keys 접속
2. "Create new secret key" 클릭
3. 키 복사 및 저장
```

### Step 2️⃣: 로컬 설정 (1분)

```bash
# 1. 프로젝트 디렉토리 생성 및 이동
mkdir team-ai-project
cd team-ai-project

# 2. Python 가상환경 생성
python3 -m venv venv

# 3. 가상환경 활성화
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 4. 의존성 설치
pip install anthropic openai flask python-dotenv

# 5. .env 파일 생성
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-[위에서 복사한 키]
OPENAI_API_KEY=sk-[위에서 복사한 키]
FLASK_SECRET_KEY=development
FLASK_ENV=development
EOF
```

### Step 3️⃣: 실행 (1분)

**Option A: Python 스크립트 테스트**

```bash
# api_manager.py 가져오기 (위에서 제공한 코드)
# 그리고 실행
python api_manager.py
```

**예상 출력:**
```
==================================================
📄 문서 처리 예제
==================================================
✅ 요약 결과:
[AI가 생성한 요약 텍스트]

==================================================
💻 코드 처리 예제
==================================================
✅ 최적화 결과:
[AI가 생성한 최적화 코드]

...
```

**Option B: 웹 대시보드 실행**

```bash
# Flask 서버 시작
python app.py

# 브라우저에서 접속
# http://localhost:5000

# 로그인
# ID: admin
# Password: admin123
```

---

## 🎯 실행 후 첫 시도

### 문서 처리해보기

```python
from api_manager import TeamAIManager

manager = TeamAIManager()

# 예제 1: 문서 요약
result = manager.process_document(
    "인공지능은 현대 기술의 핵심입니다. ...",
    "summarize"
)
print(result['result'])

# 예제 2: 코드 리뷰
code = """
def calculate(x, y):
    sum = x + y
    return sum
"""
result = manager.process_code(code, "review", language="python")
print(result['result'])

# 예제 3: 데이터 분석
csv_data = """
월,매출,비용
1월,1000000,600000
2월,1200000,650000
"""
result = manager.analyze_data(csv_data, "월별 추세 분석")
print(result['analysis'])
```

---

## 📊 웹 대시보드 사용법

### 📄 문서 처리
1. "📄 문서" 탭 선택
2. 작업 유형 선택 (작성, 분석, 번역, 요약)
3. 문서 내용 입력
4. "처리하기" 클릭
5. 결과 확인 및 복사

### 💻 코드 처리
1. "💻 코드" 탭 선택
2. 작업 유형 선택 (리뷰, 버그 수정, 최적화, 설명)
3. 프로그래밍 언어 선택
4. 코드 입력
5. "처리하기" 클릭

### 📊 데이터 분석
1. "📊 데이터" 탭 선택
2. 데이터 유형 선택 (CSV, JSON, 텍스트)
3. 데이터 입력
4. 분석 질문 입력
5. "분석하기" 클릭
6. (선택) "시각화 코드 생성" 클릭

### 📈 통계 확인
1. "📈 통계" 탭 선택
2. 조회 기간 선택
3. 실시간 통계 확인
4. 팀 사용량 및 예상 비용 확인

---

## 🔐 다음 단계 (선택)

### 팀 멤버 추가

```python
# app.py의 TEAM_USERS 수정
TEAM_USERS = {
    "admin": "admin123",
    "alice": "password1",
    "bob": "password2",
    "charlie": "password3",
    "your-name": "your-password"  # 추가
}
```

### 팀 멤버 권한 설정

```python
# 향후: 데이터베이스 기반 권한 관리
# Phase 2에서 구현 예정
```

---

## 🚀 서버 배포 (선택)

2-3주 안정성을 확인한 후 서버 배포를 권장합니다.

```bash
# 자세한 배포 가이드는 DEPLOYMENT_GUIDE.md 참조
# - DigitalOcean 배포 단계별 가이드
# - 도메인 연결
# - SSL/TLS 설정
# - 자동 백업
```

---

## ❓ FAQ

### Q1: API 키를 잃어버렸어요
```
A: 새로운 키를 발급받으면 됩니다.
- Claude: https://console.anthropic.com/account/keys
- OpenAI: https://platform.openai.com/account/api-keys
이전 키는 비활성화하세요.
```

### Q2: 비용이 얼마나 들어요?
```
A: 월 $50-100 정도입니다 (10명 팀 기준)
- Claude API: 약 $30-50/월
- OpenAI API: 약 $20-30/월
- 서버 비용: $5-20/월 (Phase 2)
```

### Q3: 데이터 보안은 어떻게 되나요?
```
A: Phase 1에서는 API로 전송됩니다.
Phase 2(자체 서버)로 이전하면 로컬 처리 가능합니다.
```

### Q4: 오프라인에서도 사용 가능한가요?
```
A: Phase 1은 인터넷 필수입니다.
Phase 2에서 로컬 모델(Ollama) 통합으로 오프라인 지원 예정.
```

### Q5: 팀 멤버가 추가되면?
```
A: TEAM_USERS에 계정 추가하면 됩니다.
향후 데이터베이스 기반 사용자 관리 예정.
```

---

## 🔧 기술 스택

| 계층 | 기술 |
|------|------|
| **AI API** | Claude (Anthropic) + GPT-4 (OpenAI) |
| **백엔드** | Python + Flask |
| **데이터베이스** | SQLite (로컬) |
| **프론트엔드** | HTML5 + CSS3 + JavaScript |
| **서버** | Nginx + Gunicorn |
| **호스팅** | DigitalOcean (선택) |

---

## 📁 파일 구조

```
team-ai-project/
├── venv/                    # Python 가상환경
├── api_manager.py          # 핵심 API 매니저 ⭐
├── app.py                  # Flask 웹 서버
├── requirements.txt        # Python 의존성
├── .env                    # 환경 변수 (보안)
├── .env.example            # 환경 변수 템플릿
├── templates/
│   └── dashboard.html      # 웹 대시보드
├── team_ai_usage.db        # SQLite 데이터베이스 (자동 생성)
├── DEPLOYMENT_GUIDE.md     # 배포 가이드
└── README.md              # 문서
```

---

## 🎓 학습 자료

### Python으로 더 깊이 있게 배우기

```python
# 1. 비동기 처리 (향후)
from asyncio import gather
from api_manager import TeamAIManager

async def batch_process():
    manager = TeamAIManager()
    # 여러 요청을 동시 처리
    pass

# 2. 커스텀 프롬프트 (향후)
custom_prompt = """
당신은 전문 [직무]입니다.
다음 작업을 전문성 있게 처리하세요: {input}
"""

# 3. 플러그인 아키텍처 (향후)
class CustomPlugin(TeamAIManager):
    def custom_task(self, content):
        # 자신의 로직 추가
        pass
```

---

## 🆘 문제 해결

### 1. "ModuleNotFoundError: No module named 'anthropic'"
```bash
# 해결: 의존성 재설치
pip install -r requirements.txt
```

### 2. "Connection refused" (API 연결 오류)
```bash
# 해결: API 키 확인
cat .env
# ANTHROPIC_API_KEY, OPENAI_API_KEY 확인
```

### 3. "Port 5000 already in use"
```bash
# 해결: 다른 포트 사용
python app.py --port 5001
```

### 4. 웹 대시보드 로그인 실패
```bash
# 기본 계정 확인
# ID: admin, Password: admin123
```

---

## 📞 지원

**문제 발생 시:**
1. 로그 확인: 콘솔 출력 메시지 확인
2. API 키 재확인
3. 인터넷 연결 확인
4. Python 버전 확인: `python3 --version`

---

## 🎉 축하합니다!

이제 팀 AI 업무 처리 시스템을 사용할 준비가 완료되었습니다.

**다음 권장사항:**
1. 팀 멤버 10명과 함께 2주 테스트
2. 사용 패턴 분석
3. Phase 2 (자체 서버) 전환 검토
4. 비용 최적화 전략 수립

---

**Happy AI Working! 🚀**
