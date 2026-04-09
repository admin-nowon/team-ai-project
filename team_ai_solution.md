# 팀 단위 AI 업무 처리 솔루션
## Phase 1: Cloud API (현재) → Phase 2: 자체 서버 (향후)

---

## 🎯 솔루션 개요

### 현재 상황
- **팀 규모**: 10명 이하 (집약적 사용)
- **예산**: API 구독 중심
- **인프라**: 자체 도메인 + 서버 준비
- **업무**: 문서 작업(1) + 데이터 분석(3)

### 로드맵
```
Phase 1 (0-3개월)     Phase 2 (3-6개월)      Phase 3 (6개월+)
─────────────────────────────────────────────────────────
Cloud API 기반   →   Hybrid 구축        →   완전 자체 서버
(비용 최소)          (비용 절감)            (완전 자유도)
```

---

## 📊 Phase 1: Cloud API 기반 솔루션

### 1-1. 추천 API 조합

| 용도 | 서비스 | 가격 | 용량 |
|------|--------|------|------|
| **주력 LLM** | Claude API (Anthropic) | $3-20/월 (기본) | 문서, 코드 최적 |
| **보조 모델** | OpenAI GPT-4 | $20/월 | 실시간 필요시 |
| **데이터 분석** | OpenAI + Code Interpreter | $20/월 | CSV, 통계 분석 |
| **총 예상** | - | **$50-100/월** | 10명 팀 충분 |

### 1-2. Phase 1 아키텍처

```
┌─────────────────────────────────────────────────────┐
│            팀 멤버 (Slack, 웹 대시보드)              │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ↓                     ↓
   ┌─────────┐          ┌──────────┐
   │   Web   │          │  Slack   │
   │ Dashboard│          │   Bot    │
   │(Flask)  │          │          │
   └────┬────┘          └────┬─────┘
        │                    │
        └──────────┬─────────┘
                   ↓
        ┌──────────────────────┐
        │  Python Backend      │
        │  (api_manager.py)    │
        └────────┬─────────────┘
                 │
    ┌────────────┼────────────┐
    ↓            ↓            ↓
┌─────────┐ ┌────────┐ ┌──────────┐
│ Claude  │ │ OpenAI │ │  Database│
│  API    │ │  API   │ │(요청이력)│
└─────────┘ └────────┘ └──────────┘
```

---

## 💻 Phase 1 구현 코드

### 1. API Manager (핵심 모듈)

```python
# api_manager.py
import os
from anthropic import Anthropic
from openai import OpenAI
import json
from datetime import datetime

class TeamAIManager:
    def __init__(self):
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.request_history = []
    
    def process_document(self, content: str, task_type: str) -> dict:
        """
        문서 처리: 작성, 분석, 번역
        task_type: 'write', 'analyze', 'translate', 'summarize'
        """
        prompts = {
            'write': f"다음 주제로 전문적인 문서를 작성하세요:\n{content}",
            'analyze': f"다음 문서를 분석하고 핵심 요점을 정리하세요:\n{content}",
            'translate': f"다음 텍스트를 영어에서 한국어로 번역하세요:\n{content}",
            'summarize': f"다음 문서를 3문장으로 요약하세요:\n{content}"
        }
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompts.get(task_type, content)
            }]
        )
        
        result = response.content[0].text
        self._log_request("document", task_type, content[:100], result[:100])
        
        return {
            "status": "success",
            "task": task_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_code(self, code: str, task_type: str) -> dict:
        """
        코드 처리: 리뷰, 버그 찾기, 최적화, 설명
        task_type: 'review', 'bug_fix', 'optimize', 'explain'
        """
        prompts = {
            'review': f"다음 코드를 검토하고 개선사항을 제안하세요:\n```\n{code}\n```",
            'bug_fix': f"다음 코드의 버그를 찾고 수정하세요:\n```\n{code}\n```",
            'optimize': f"다음 코드를 최적화하세요:\n```\n{code}\n```",
            'explain': f"다음 코드를 설명하세요:\n```\n{code}\n```"
        }
        
        response = self.claude.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompts.get(task_type, code)
            }]
        )
        
        result = response.content[0].text
        self._log_request("code", task_type, code[:100], result[:100])
        
        return {
            "status": "success",
            "task": task_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_data(self, csv_data: str, question: str) -> dict:
        """
        데이터 분석: CSV 분석, 통계, 그래프 생성 요청
        """
        response = self.openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"""
                다음 CSV 데이터를 분석하세요:
                ```
                {csv_data}
                ```
                
                질문: {question}
                
                Python 코드와 분석 결과를 제공하세요.
                """
            }]
        )
        
        result = response.choices[0].message.content
        self._log_request("data_analysis", "analyze", question, result[:100])
        
        return {
            "status": "success",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_request(self, category: str, task: str, input_text: str, output_text: str):
        """요청 이력 저장 (추후 자체 서버 마이그레이션시 DB로 이관)"""
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "task": task,
            "input_preview": input_text,
            "output_preview": output_text
        })
    
    def get_usage_report(self) -> dict:
        """팀 사용량 리포트"""
        categories = {}
        for req in self.request_history:
            cat = req["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_requests": len(self.request_history),
            "by_category": categories,
            "estimated_cost": len(self.request_history) * 0.01  # 평균 $0.01/요청
        }


# 사용 예제
if __name__ == "__main__":
    manager = TeamAIManager()
    
    # 문서 작성
    doc_result = manager.process_document(
        "회사 분기별 성과 보고서",
        "write"
    )
    print("문서 작성:", doc_result)
    
    # 코드 리뷰
    code = """
    def calculate_average(numbers):
        total = 0
        for i in numbers:
            total = total + i
        return total / len(numbers)
    """
    code_result = manager.process_code(code, "review")
    print("코드 리뷰:", code_result)
    
    # 사용량 리포트
    print("사용량:", manager.get_usage_report())
```

### 2. Flask 웹 대시보드

```python
# app.py
from flask import Flask, render_template, request, jsonify
from api_manager import TeamAIManager
import os

app = Flask(__name__)
manager = TeamAIManager()

@app.route('/api/document', methods=['POST'])
def process_document():
    data = request.json
    result = manager.process_document(data['content'], data['task_type'])
    return jsonify(result)

@app.route('/api/code', methods=['POST'])
def process_code():
    data = request.json
    result = manager.process_code(data['code'], data['task_type'])
    return jsonify(result)

@app.route('/api/data-analysis', methods=['POST'])
def analyze_data():
    data = request.json
    result = manager.analyze_data(data['csv_data'], data['question'])
    return jsonify(result)

@app.route('/api/usage', methods=['GET'])
def get_usage():
    return jsonify(manager.get_usage_report())

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 3. HTML 대시보드 (templates/dashboard.html)

```html
<!DOCTYPE html>
<html>
<head>
    <title>팀 AI 업무 처리 대시보드</title>
    <style>
        body { font-family: Arial; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        textarea { width: 100%; height: 150px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; }
        .result { background: #f0f0f0; padding: 10px; margin-top: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🤖 팀 AI 업무 처리 대시보드</h1>
    
    <div class="container">
        <!-- 문서 처리 -->
        <div class="card">
            <h2>📄 문서 처리</h2>
            <select id="docTaskType">
                <option value="write">작성</option>
                <option value="analyze">분석</option>
                <option value="translate">번역</option>
                <option value="summarize">요약</option>
            </select>
            <textarea id="docInput" placeholder="문서 내용 입력..."></textarea>
            <button onclick="processDocument()">처리하기</button>
            <div id="docResult" class="result"></div>
        </div>
        
        <!-- 코드 처리 -->
        <div class="card">
            <h2>💻 코드 처리</h2>
            <select id="codeTaskType">
                <option value="review">리뷰</option>
                <option value="bug_fix">버그 수정</option>
                <option value="optimize">최적화</option>
                <option value="explain">설명</option>
            </select>
            <textarea id="codeInput" placeholder="코드 입력..."></textarea>
            <button onclick="processCode()">처리하기</button>
            <div id="codeResult" class="result"></div>
        </div>
    </div>
    
    <!-- 사용량 리포트 -->
    <div class="card" style="margin-top: 20px;">
        <h2>📊 사용량 리포트</h2>
        <button onclick="getUsageReport()">리포트 조회</button>
        <div id="usageResult" class="result"></div>
    </div>
    
    <script>
        async function processDocument() {
            const content = document.getElementById('docInput').value;
            const taskType = document.getElementById('docTaskType').value;
            
            const response = await fetch('/api/document', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, task_type: taskType })
            });
            
            const result = await response.json();
            document.getElementById('docResult').innerHTML = 
                '<strong>결과:</strong><pre>' + result.result + '</pre>';
        }
        
        async function processCode() {
            const code = document.getElementById('codeInput').value;
            const taskType = document.getElementById('codeTaskType').value;
            
            const response = await fetch('/api/code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, task_type: taskType })
            });
            
            const result = await response.json();
            document.getElementById('codeResult').innerHTML = 
                '<strong>결과:</strong><pre>' + result.result + '</pre>';
        }
        
        async function getUsageReport() {
            const response = await fetch('/api/usage');
            const data = await response.json();
            
            document.getElementById('usageResult').innerHTML = `
                <p><strong>총 요청:</strong> ${data.total_requests}</p>
                <p><strong>분류별:</strong> ${JSON.stringify(data.by_category)}</p>
                <p><strong>예상 비용:</strong> $${data.estimated_cost.toFixed(2)}</p>
            `;
        }
    </script>
</body>
</html>
```

---

## 🔧 배포 가이드 (자체 도메인 + 서버)

### AWS/GCP/Azure 배포 예제

```bash
# 1. 서버 준비 (Ubuntu 22.04)
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git nginx -y

# 2. 프로젝트 클론 및 설정
git clone [your-repo] /opt/team-ai
cd /opt/team-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 환경변수 설정
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxxxx
FLASK_ENV=production
EOF

# 4. Nginx 설정 (리버스 프록시)
sudo cat > /etc/nginx/sites-available/team-ai << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/team-ai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 5. Gunicorn + Systemd로 자동 실행
sudo cat > /etc/systemd/system/team-ai.service << EOF
[Unit]
Description=Team AI Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/team-ai
ExecStart=/opt/team-ai/venv/bin/gunicorn app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload && sudo systemctl enable team-ai && sudo systemctl start team-ai

# 6. SSL 인증서 (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d your-domain.com
```

---

## 📈 Phase 1 → Phase 2 마이그레이션 경로

### Phase 2: 자체 서버 (6개월 후)

```
Phase 1 (Cloud API)          Phase 2 (Hybrid)              Phase 3 (Full Local)
─────────────────────────────────────────────────────────────────────────
Claude API              Claude API               Ollama (로컬)
OpenAI API         +    OpenAI API         +    LLaMA 2 70B
(클라우드)              (고급작업만)              (일상 작업)
                                             
비용: $100/월          비용: $50/월            비용: 인프라만 (절감)
```

### Phase 2 추가 구현 (향후)

```python
# phase2_hybrid_manager.py
from ollama import Client
from api_manager import TeamAIManager

class HybridAIManager(TeamAIManager):
    def __init__(self):
        super().__init__()
        self.ollama = Client(host='http://localhost:11434')
    
    def process_document_hybrid(self, content: str, task_type: str):
        """
        로컬 모델로 먼저 시도, 필요시 클라우드 API 사용
        """
        # 간단한 작업은 로컬 (비용 절감)
        if task_type in ['summarize', 'explain']:
            response = self.ollama.generate(
                model='llama2',
                prompt=content
            )
            return {"status": "success", "result": response, "source": "local"}
        
        # 복잡한 작업은 클라우드 (품질 보장)
        else:
            return super().process_document(content, task_type)
```

---

## 💰 비용 비교표

| Phase | 월 비용 | 인프라 | 특징 |
|-------|---------|--------|------|
| **Phase 1 (현재)** | $100 | Cloud API | 관리 간단, 최신 모델 |
| **Phase 2 (6개월)** | $50 + 인프라 | Hybrid | 비용 50% 절감 |
| **Phase 3 (12개월)** | 인프라만 | Self-hosted | 완전 자유도, 데이터 보안 |

---

## 📋 필수 파일 목록

```
team-ai-project/
├── api_manager.py           # 핵심 API 매니저
├── app.py                   # Flask 서버
├── requirements.txt         # 의존성
├── .env.example            # 환경변수 템플릿
├── templates/
│   └── dashboard.html      # 웹 UI
├── docker-compose.yml      # (선택) Docker 배포
└── README.md               # 문서
```

---

## 🚀 시작 체크리스트

- [ ] Claude API 키 발급 (claude.ai → Account → API keys)
- [ ] OpenAI API 키 발급
- [ ] AWS/GCP 서버 준비
- [ ] 도메인 구매 + DNS 설정
- [ ] 로컬에서 테스트 완료
- [ ] 팀 멤버 액세스 권한 설정
- [ ] 모니터링 대시보드 구성

---

**다음 단계:** 
1. 위 코드를 자신의 도메인 서버에 배포
2. 2주간 Phase 1 안정화
3. 사용 패턴 분석 후 Phase 2 계획 수립
