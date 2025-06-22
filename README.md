DDoS 탐지·대응 시스템
FastAPI 백엔드와 Streamlit 대시보드, XGBoost 기반 머신러닝 모델을 결합한 엔드투엔드 DDoS 공격 탐지·대응 시스템입니다.

🔍 주요 기능
실시간 패킷 캡처
Scapy 기반 스니퍼로 네트워크 흐름을 수집 → 핵심 피처(Flow Duration, Total Fwd/Bwd Packets 등) 계산

이진 분류 (Normal vs Attack)
XGBoost 모델로 정상/공격 여부 판별 (정확도 99.1%)

다중 분류 (Attack Type)
XGBoost + 언더샘플링/SMOTE → UDP, SYN, MSSQL 등 7종 공격 식별 (정확도 94.5%)

리스크 스코어링 & 알림
risk_score = confidence × log(flow_size) 계산 후, 임계치 초과 시 이메일 자동 발송

지리 위치 시각화
GeoLite2 DB로 IP→위치 변환 → pydeck 지도에 공격 지점 표시

Streamlit 대시보드
실시간 차트·메트릭·지도 제공, 랜덤 샘플 테스트 버튼으로 운영 환경 시뮬레이션

⚙️ 설치 & 실행
레포지토리 클론

git clone https://github.com/go5rae/ddos-detection.git
cd ddos-detection
가상환경 생성 및 활성화

Windows PowerShell

python -m venv venv
.\venv\Scripts\Activate.ps1
macOS/Linux

python3 -m venv venv
source venv/bin/activate
의존성 설치

pip install --upgrade pip
pip install -r requirements.txt
설정 파일 복사

cp .env.example .env
.env 에서 SMTP, DB 경로 등 환경 변수 입력

GeoLite2 DB 준비
backend/data/GeoLite2-City.mmdb 파일을 다운받아 해당 경로에 넣기

백엔드 서버 실행

uvicorn main:app --reload
대시보드 실행

streamlit run streamlit_app.py
📂 디렉터리 구조
ddos-detection/
├─ .github/                 # CI 설정
├─ backend/
│   ├─ data/                # GeoLite2 DB, 라벨 클래스
│   ├─ training/            # 모델 학습 스크립트
│   ├─ routers/             # FastAPI 라우터
│   ├─ auth.py              # 인증
│   ├─ database.py          # DB 연결
│   ├─ geolocation.py       # IP→위치 변환
│   ├─ predict.py           # 예측 API
│   └─ recommendation.py    # 대응 가이드
├─ realtime_sniffer.py      # 패킷 캡처 및 피처 계산
├─ generate_dummy_logs.py   # 더미 로그 생성
├─ streamlit_app.py         # Streamlit UI
├─ requirements.txt         # 패키지 목록
└─ README.md
🧪 테스트
pytest
tests/test_predict.py 로 예측 API 검증

📝 라이선스
MIT License
자세한 내용은 LICENSE 파일 참고
