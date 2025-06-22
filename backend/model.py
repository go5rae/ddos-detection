import joblib
import numpy as np
import pandas as pd

# 모델 경로
MODEL_PATH = "backend/data/ddos_model.pkl"

# 모델 로딩
model = joblib.load(MODEL_PATH)

# 위험도 점수 계산 함수 (예: 확률 * 100)
def calculate_risk_score(probability: float) -> int:
    return int(probability * 100)

# 예측 함수
def predict_ddos(data: dict) -> dict:
    # JSON 데이터를 DataFrame으로 변환
    df = pd.DataFrame([data])
    
    # 모델 예측 (예: 1 = 공격, 0 = 정상)
    prediction = model.predict(df)[0]
    
    # 예측 확률
    probability = model.predict_proba(df)[0][1]  # 1: 공격 클래스
    
    # 위험도 점수 계산
    risk_score = calculate_risk_score(probability)

    result = {
        "prediction": int(prediction),
        "risk_score": risk_score,
        "is_ddos": prediction == 1
    }

    return result
