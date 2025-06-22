DDoS 탐지·대응 시스템
실시간 네트워크 트래픽을 분석해 DDoS 공격을 탐지·차단하고, 대시보드로 시각화까지 지원하는 end-to-end 솔루션

📂 폴더 구조
bash
코드 복사
.
├── backend/
│   ├── api/                        # FastAPI 엔드포인트
│   ├── training/                   # 모델 학습 스크립트
│   │   ├── train_binary_ddos_model.py
│   │   └── ddos_multiclass_model.py
│   ├── models/                     # 학습된 .pkl 파일
│   ├── utils.py
│   └── requirements.txt
├── notebooks/                      # 실험·분석용 Jupyter 노트북
├── streamlit_app.py                # 대시보드 실행 스크립트
└── README.md
🚀 주요 기능
실시간 DDoS 탐지

Binary 모델로 정상 vs 공격 구분

Multiclass 모델로 공격 유형 식별

자동 차단 연동

위험도 임계치 초과 시 방화벽 API 호출

대시보드 시각화

Streamlit 기반 실시간 지표·지도·알림

로그 저장 & 보고서 생성

탐지 이벤트 DB 저장

주간 요약 PDF 리포트 자동 발송

🛠️ 설치 및 실행
1. 클론 & 가상환경 설정
bash
코드 복사
git clone https://github.com/YourUser/ddos-detection.git
cd ddos-detection/backend
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
2. 데이터 준비
CIC-DDoS-2019 데이터는 공식 사이트에서 다운로드

압축 해제 후, backend/.env 파일에
DATA_DIR=/path/to/datasets 형태로 경로 설정

3. 모델 학습
# 이진 분류 모델 학습
python backend/training/train_binary_ddos_model.py

# 다중 분류 모델 학습
python backend/training/ddos_multiclass_model.py
학습이 완료되면 backend/models/ 폴더에 .pkl 파일이 생성됩니다.

4. API 서버 실행
uvicorn backend.api.main:app --reload
POST /predict_ddos 등 예측·차단·로그용 엔드포인트 제공

5. 대시보드 실행
streamlit run streamlit_app.py
브라우저에서 http://localhost:8501 로 접속

📄 기타
로그 DB: backend/logs.db (SQLite)

환경 변수:

DATA_DIR : 데이터셋 경로

FIREWALL_API_URL, EMAIL_CREDENTIALS 등 .env에 설정

CI/CD: GitHub Actions → Docker → GCP Cloud Run 배포

🙏 기여 및 문의
이슈 혹은 PR을 환영합니다.

사용 중 문제 발생 시 issues 탭에 남겨 주세요.