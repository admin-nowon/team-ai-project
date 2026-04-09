"""
팀 AI 업무 처리 Flask 웹 대시보드
실행: python app.py
접속: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, session
from api_manager import TeamAIManager
from functools import wraps
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")

# API 매니저 초기화
manager = TeamAIManager()

# 간단한 인증 (실제로는 DB 사용 권장)
TEAM_USERS = {
    "admin": "admin123",
    "alice": "password1",
    "bob": "password2",
    "charlie": "password3"
}

# ==================== 인증 미들웨어 ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"error": "로그인 필요"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== 페이지 라우트 ====================

@app.route('/')
def index():
    """메인 대시보드"""
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in TEAM_USERS and TEAM_USERS[username] == password:
            session['user'] = username
            return redirect('/')
        else:
            return render_template('login.html', error='로그인 실패')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect('/login')

# ==================== API 엔드포인트 ====================

@app.route('/api/document', methods=['POST'])
@login_required
def api_process_document():
    """문서 처리 API"""
    try:
        data = request.json
        content = data.get('content')
        task_type = data.get('task_type', 'summarize')
        
        if not content:
            return jsonify({"error": "내용이 필요합니다"}), 400
        
        result = manager.process_document(
            content, 
            task_type, 
            user=session['user']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/code', methods=['POST'])
@login_required
def api_process_code():
    """코드 처리 API"""
    try:
        data = request.json
        code = data.get('code')
        task_type = data.get('task_type', 'review')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"error": "코드가 필요합니다"}), 400
        
        result = manager.process_code(
            code, 
            task_type,
            language=language,
            user=session['user']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data-analysis', methods=['POST'])
@login_required
def api_analyze_data():
    """데이터 분석 API"""
    try:
        data = request.json
        data_content = data.get('data')
        question = data.get('question')
        data_type = data.get('data_type', 'csv')
        
        if not data_content or not question:
            return jsonify({"error": "데이터와 질문이 필요합니다"}), 400
        
        result = manager.analyze_data(
            data_content,
            question,
            data_type=data_type,
            user=session['user']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/visualization', methods=['POST'])
@login_required
def api_generate_visualization():
    """시각화 코드 생성 API"""
    try:
        data = request.json
        description = data.get('description')
        chart_type = data.get('chart_type', 'auto')
        
        if not description:
            return jsonify({"error": "데이터 설명이 필요합니다"}), 400
        
        result = manager.generate_visualization_code(
            description,
            chart_type=chart_type,
            user=session['user']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/usage', methods=['GET'])
@login_required
def api_get_usage():
    """사용량 리포트 API"""
    try:
        days = request.args.get('days', 7, type=int)
        report = manager.get_team_usage_report(days=days)
        return jsonify(report)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user-stats', methods=['GET'])
@login_required
def api_get_user_stats():
    """사용자 통계 API"""
    try:
        stats = manager.get_user_stats(session['user'])
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/batch-documents', methods=['POST'])
@login_required
def api_batch_documents():
    """배치 문서 처리 API"""
    try:
        data = request.json
        documents = data.get('documents', [])
        task_type = data.get('task_type', 'summarize')
        
        if not documents:
            return jsonify({"error": "문서 리스트가 필요합니다"}), 400
        
        # user 필드 추가
        for doc in documents:
            doc['user'] = session['user']
        
        results = manager.batch_process_documents(documents, task_type)
        
        return jsonify({
            "status": "success",
            "total": len(results),
            "results": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== 에러 핸들링 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "페이지를 찾을 수 없습니다"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "서버 오류"}), 500

# ==================== 헬퍼 함수 ====================

def redirect(url):
    """간단한 리다이렉트"""
    from flask import redirect as flask_redirect
    return flask_redirect(url)

# ==================== 실행 ====================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 팀 AI 업무 처리 대시보드 시작")
    print("="*50)
    print("📍 주소: http://localhost:5000")
    print("👤 테스트 계정: admin / admin123")
    print("="*50 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # 운영환경에서는 False로 변경
    )
