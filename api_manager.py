"""
팀 단위 AI 업무 처리 매니저 (Phase 1: Cloud API)
사용 예제:
    manager = TeamAIManager()
    result = manager.process_document("분석할 문서", "summarize")
    print(result)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from anthropic import Anthropic
from openai import OpenAI
import sqlite3


class TeamAIManager:
    """팀 단위 AI 업무 처리 통합 매니저"""
    
    def __init__(self, db_path: str = "team_ai_usage.db"):
        """
        초기화
        
        Args:
            db_path: SQLite DB 경로 (사용 이력 저장)
        """
        self.claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                category TEXT,
                task TEXT,
                user TEXT,
                input_length INTEGER,
                output_length INTEGER,
                status TEXT,
                api_used TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def _log_request(self, category: str, task: str, user: str, 
                     input_text: str, output_text: str, api_used: str, 
                     status: str = "success"):
        """요청 이력 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests 
            (timestamp, category, task, user, input_length, output_length, status, api_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            category,
            task,
            user,
            len(input_text),
            len(output_text),
            status,
            api_used
        ))
        conn.commit()
        conn.close()
    
    # ==================== 문서 처리 ====================
    
    def process_document(self, content: str, task_type: str, 
                        user: str = "team") -> Dict:
        """
        문서 처리: 작성, 분석, 번역, 요약
        
        Args:
            content: 입력 문서 내용
            task_type: 'write', 'analyze', 'translate', 'summarize'
            user: 요청 사용자
        
        Returns:
            처리 결과 딕셔너리
        """
        prompts = {
            'write': f"""다음 주제로 전문적이고 체계적인 문서를 작성하세요.
            형식: 제목, 본문(최소 3개 섹션), 결론
            톤: 전문적이고 명확함
            
            주제: {content}""",
            
            'analyze': f"""다음 문서를 심층 분석하고 정리하세요.
            포함 항목:
            1. 핵심 주제
            2. 주요 포인트 (최소 3개)
            3. 강점
            4. 개선 사항
            5. 결론
            
            문서: {content}""",
            
            'translate': f"""다음 영어 텍스트를 한국어로 번역하세요.
            원칙: 자연스럽고 정확한 번역, 문맥 고려
            
            원문: {content}""",
            
            'summarize': f"""다음 문서를 3문장으로 요약하세요.
            핵심: 가장 중요한 정보만 포함
            
            문서: {content}"""
        }
        
        prompt = prompts.get(task_type, content)
        
        try:
            response = self.claude.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            result = response.content[0].text
            self._log_request("document", task_type, user, content, result, "claude-api")
            
            return {
                "status": "success",
                "task": task_type,
                "result": result,
                "model": "Claude Opus 4",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self._log_request("document", task_type, user, content, 
                            str(e), "claude-api", status="error")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== 코드 처리 ====================
    
    def process_code(self, code: str, task_type: str, 
                    language: str = "python", user: str = "team") -> Dict:
        """
        코드 처리: 리뷰, 버그 수정, 최적화, 설명
        
        Args:
            code: 입력 코드
            task_type: 'review', 'bug_fix', 'optimize', 'explain', 'document'
            language: 프로그래밍 언어 (python, javascript, java, etc)
            user: 요청 사용자
        
        Returns:
            처리 결과 딕셔너리
        """
        prompts = {
            'review': f"""다음 {language} 코드를 전문가 관점에서 검토하세요.
            평가 항목:
            1. 코드 품질 (가독성, 구조)
            2. 성능 문제
            3. 보안 취약점
            4. 베스트 프랙티스 준수
            5. 개선 방안 (구체적 예제 포함)
            
            코드:
            ```{language}
            {code}
            ```""",
            
            'bug_fix': f"""다음 {language} 코드의 버그를 찾아 수정하세요.
            1. 버그 설명 (어떤 문제인지)
            2. 원인 분석
            3. 수정된 코드
            4. 테스트 방법 제시
            
            코드:
            ```{language}
            {code}
            ```""",
            
            'optimize': f"""다음 {language} 코드를 최적화하세요.
            최적화 목표:
            1. 성능 개선 (시간/공간 복잡도)
            2. 가독성 향상
            3. 유지보수성 개선
            
            원본 코드:
            ```{language}
            {code}
            ```
            
            최적화된 코드를 설명과 함께 제시하세요.""",
            
            'explain': f"""다음 {language} 코드를 상세히 설명하세요.
            설명 구성:
            1. 전체 목적
            2. 함수/클래스별 역할
            3. 실행 흐름
            4. 입출력 예제
            
            코드:
            ```{language}
            {code}
            ```""",
            
            'document': f"""다음 {language} 코드에 주석과 docstring을 추가하세요.
            포함 항목:
            1. 함수/클래스 설명 (docstring)
            2. 파라미터 설명
            3. 반환값 설명
            4. 복잡한 로직에 인라인 주석
            
            코드:
            ```{language}
            {code}
            ```"""
        }
        
        prompt = prompts.get(task_type, code)
        
        try:
            response = self.claude.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=3000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            result = response.content[0].text
            self._log_request("code", task_type, user, code, result, "claude-api")
            
            return {
                "status": "success",
                "task": task_type,
                "language": language,
                "result": result,
                "model": "Claude Opus 4",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self._log_request("code", task_type, user, code, 
                            str(e), "claude-api", status="error")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== 데이터 분석 ====================
    
    def analyze_data(self, data_content: str, question: str, 
                    data_type: str = "csv", user: str = "team") -> Dict:
        """
        데이터 분석: CSV/JSON 분석, 통계, 인사이트 도출
        
        Args:
            data_content: 데이터 내용 (CSV, JSON 등)
            question: 분석 질문
            data_type: 'csv', 'json', 'text'
            user: 요청 사용자
        
        Returns:
            분석 결과 딕셔너리
        """
        prompt = f"""다음 {data_type} 데이터를 분석하고 질문에 답하세요.

데이터:
```
{data_content}
```

분석 질문: {question}

응답 구성:
1. 데이터 개요 (행 수, 열 수, 데이터 타입)
2. 질문에 대한 직접적인 답변
3. 통계 분석 (평균, 중간값, 표준편차 등)
4. 트렌드 및 패턴
5. 시각화 권장사항 (어떤 차트가 좋을지)
6. 추가 인사이트

가능하면 Python 코드 예제도 포함하세요."""
        
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            result = response.choices[0].message.content
            self._log_request("data_analysis", "analyze", user, data_content, result, "openai-gpt4")
            
            return {
                "status": "success",
                "analysis": result,
                "data_type": data_type,
                "model": "GPT-4 Turbo",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            self._log_request("data_analysis", "analyze", user, data_content, 
                            str(e), "openai-gpt4", status="error")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_visualization_code(self, data_description: str, 
                                   chart_type: str = "auto", 
                                   user: str = "team") -> Dict:
        """
        시각화 코드 생성 (Matplotlib, Seaborn)
        
        Args:
            data_description: 데이터 설명
            chart_type: 'auto', 'line', 'bar', 'scatter', 'heatmap', 'pie'
            user: 요청 사용자
        
        Returns:
            코드 생성 결과
        """
        prompt = f"""다음 데이터를 시각화하는 Python 코드를 생성하세요.
차트 유형: {chart_type}

데이터 설명:
{data_description}

요구사항:
1. Matplotlib + Seaborn 사용
2. 한글 폰트 설정 포함
3. 제목, 축 라벨, 범례 포함
4. 전문적인 스타일 적용
5. 저장 함수 포함 (PNG, SVG)

완전히 실행 가능한 Python 코드를 제공하세요."""
        
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            result = response.choices[0].message.content
            self._log_request("data_analysis", "visualization", user, 
                            data_description, result, "openai-gpt4")
            
            return {
                "status": "success",
                "code": result,
                "chart_type": chart_type,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ==================== 통계 및 리포트 ====================
    
    def get_team_usage_report(self, days: int = 7) -> Dict:
        """
        팀 사용량 리포트
        
        Args:
            days: 조회 기간 (일)
        
        Returns:
            사용 통계
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 기간 내 요청
        cursor.execute('''
            SELECT category, task, COUNT(*) as count, 
                   SUM(input_length) as total_input,
                   SUM(output_length) as total_output
            FROM requests
            WHERE timestamp > datetime('now', '-' || ? || ' days')
            GROUP BY category, task
        ''', (days,))
        
        results = cursor.fetchall()
        conn.close()
        
        # 정리
        summary = {}
        total_requests = 0
        
        for category, task, count, input_len, output_len in results:
            if category not in summary:
                summary[category] = {}
            summary[category][task] = {
                "requests": count,
                "total_input_chars": input_len or 0,
                "total_output_chars": output_len or 0,
                "avg_output_chars": (output_len or 0) // count if count > 0 else 0
            }
            total_requests += count
        
        # 비용 추정 (API 별)
        claude_cost = summary.get('document', {}).get('count', 0) * 0.003  # 추정
        openai_cost = (summary.get('data_analysis', {}).get('count', 0) or 0) * 0.03
        
        return {
            "period_days": days,
            "total_requests": total_requests,
            "by_category": summary,
            "estimated_cost": {
                "claude": f"${claude_cost:.2f}",
                "openai": f"${openai_cost:.2f}",
                "total": f"${claude_cost + openai_cost:.2f}"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_user_stats(self, user: str) -> Dict:
        """특정 사용자의 통계"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, task, COUNT(*) as count, status
            FROM requests
            WHERE user = ?
            GROUP BY category, task, status
        ''', (user,))
        
        results = cursor.fetchall()
        conn.close()
        
        summary = {"user": user, "stats": {}}
        for category, task, count, status in results:
            key = f"{category}_{task}_{status}"
            summary["stats"][key] = count
        
        return summary
    
    # ==================== 배치 처리 ====================
    
    def batch_process_documents(self, documents: List[Dict], task_type: str) -> List[Dict]:
        """
        여러 문서 일괄 처리
        
        Args:
            documents: [{"content": "...", "user": "..."}, ...]
            task_type: 처리 유형
        
        Returns:
            결과 리스트
        """
        results = []
        for doc in documents:
            result = self.process_document(
                doc.get("content", ""),
                task_type,
                user=doc.get("user", "team")
            )
            results.append(result)
        return results
    
    def batch_process_code(self, code_snippets: List[Dict], task_type: str) -> List[Dict]:
        """여러 코드 일괄 처리"""
        results = []
        for snippet in code_snippets:
            result = self.process_code(
                snippet.get("code", ""),
                task_type,
                language=snippet.get("language", "python"),
                user=snippet.get("user", "team")
            )
            results.append(result)
        return results


# ==================== 사용 예제 ====================

if __name__ == "__main__":
    # 환경변수 설정 필요:
    # export ANTHROPIC_API_KEY="sk-ant-..."
    # export OPENAI_API_KEY="sk-..."
    
    manager = TeamAIManager()
    
    print("\n" + "="*50)
    print("📄 문서 처리 예제")
    print("="*50)
    
    # 1. 문서 요약
    doc = """
    인공지능은 현대 사회의 모든 분야에서 혁신을 가져오고 있다. 
    머신러닝, 자연어처리, 컴퓨터비전 등 다양한 기술이 개발되었고,
    이를 통해 의료, 금융, 교육 등 여러 산업에서 효율성을 높이고 있다.
    """
    
    result = manager.process_document(doc, "summarize", user="alice")
    print(f"✅ 요약 결과:\n{result['result']}\n")
    
    print("="*50)
    print("💻 코드 처리 예제")
    print("="*50)
    
    # 2. 코드 리뷰
    code = """
    def find_max(arr):
        max_val = arr[0]
        for i in range(1, len(arr)):
            if arr[i] > max_val:
                max_val = arr[i]
        return max_val
    """
    
    result = manager.process_code(code, "optimize", language="python", user="bob")
    print(f"✅ 최적화 결과:\n{result['result']}\n")
    
    print("="*50)
    print("📊 데이터 분석 예제")
    print("="*50)
    
    # 3. 데이터 분석
    csv_data = """
    월,매출,비용,순이익
    1월,1000000,600000,400000
    2월,1200000,650000,550000
    3월,1150000,700000,450000
    """
    
    result = manager.analyze_data(csv_data, "월별 추세와 성장률 분석", user="charlie")
    print(f"✅ 분석 결과:\n{result['analysis']}\n")
    
    print("="*50)
    print("📈 팀 사용량 리포트")
    print("="*50)
    
    # 4. 사용량 리포트
    report = manager.get_team_usage_report(days=7)
    print(f"총 요청: {report['total_requests']}")
    print(f"예상 비용: {report['estimated_cost']['total']}")
    print(f"분류별:\n{json.dumps(report['by_category'], indent=2, ensure_ascii=False)}\n")
