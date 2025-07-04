# -*- coding: utf-8 -*-
"""train_binary_ddos_model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12ixTa7qVtweCUijYoo7Ob1k0DyyYufMs
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

"""
train_binary_ddos_fast.py  – 3-feature, 균형·경량 최종
──────────────────────────────────────────────────────
• 기본 경로: /content/drive/MyDrive/CSV-03-11/Datasets
• 재귀 glob → *.csv / *.CSV
• NaN/Inf/음수 제거 → 라벨별 20 % 표본 → 언더샘플 1 : 1
• MinMaxScaler → XGBoost(400트리, early-stopping 호환)
• ddos_binary_model.pkl · ddos_scaler.pkl 저장
"""

import os, glob, gc, argparse, joblib, logging, warnings, inspect
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from xgboost import XGBClassifier

warnings.filterwarnings("ignore", category=FutureWarning)
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# ────────── 설정
FEATURES = ["Flow Duration", "Total Fwd Packets", "Total Backward Packets"]
CHUNK      = 10_000      # CSV 청크
SAMPLE_FR  = 0.20        # 라벨별 표본 비율
TEST_RATIO = 0.20
RAND       = 42
OUT_DIR    = Path("trained_models_fast"); OUT_DIR.mkdir(exist_ok=True)
DEFAULT_DATA_DIR = "/content/drive/MyDrive/CSV-03-11/Datasets"

# ────────── 데이터 로드
def load_df(folder: str) -> pd.DataFrame:
    csvs = glob.glob(os.path.join(folder, "**", "*.csv*"), recursive=True)
    if not csvs:
        raise FileNotFoundError(f"No CSV found under {folder}")

    frames = []
    for fp in csvs:
        label = 0 if os.path.basename(fp).upper() == "BENIGN.CSV" else 1
        log.info(f"Loading {os.path.basename(fp)}  label={label}")
        for chunk in pd.read_csv(
            fp, chunksize=CHUNK, low_memory=False,
            usecols=lambda c: c.strip() in FEATURES):
            chunk.columns = [c.strip() for c in chunk.columns]
            chunk = (chunk.replace([np.inf, -np.inf], np.nan)
                         .dropna()
                         .loc[lambda d: (d[FEATURES] >= 0).all(axis=1)])
            if not chunk.empty:
                chunk["Label"] = label
                frames.append(chunk)
        gc.collect()

    if not frames:
        raise ValueError("Required columns missing in all files.")
    df = pd.concat(frames, ignore_index=True)

    # ── 1) 라벨별 20 % 표본
    df = df.groupby('Label', group_keys=False).apply(
            lambda x: x.sample(frac=SAMPLE_FR, random_state=RAND))

    # ── 2) BENIGN 수만큼 ATTACK 언더샘플링
    n_benign = len(df[df.Label == 0])
    df_attack = df[df.Label == 1].sample(n=n_benign, random_state=RAND)
    df = pd.concat([df[df.Label == 0], df_attack]).sample(
            frac=1, random_state=RAND).reset_index(drop=True)

    log.info(f"Final training set: {df.shape}  (BENIGN {n_benign} / ATTACK {n_benign})")
    return df

# ────────── 학습
def train(data_dir: str):
    df = load_df(data_dir)
    X, y = df[FEATURES].astype(np.float32), df["Label"].astype(int)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=TEST_RATIO, stratify=y, random_state=RAND)

    scaler = MinMaxScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    model = XGBClassifier(
        objective="binary:logistic", tree_method="hist",
        n_estimators=400, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8,
        random_state=RAND, n_jobs=-1, eval_metric="logloss")

    if "early_stopping_rounds" in inspect.signature(model.fit).parameters:
        model.fit(X_tr_s, y_tr,
                  eval_set=[(X_te_s, y_te)],
                  early_stopping_rounds=30,
                  verbose=False)
    else:
        model.fit(X_tr_s, y_tr,
                  eval_set=[(X_te_s, y_te)],
                  verbose=False)

    # ─ 평가
    y_pred = model.predict(X_te_s)
    y_prob = model.predict_proba(X_te_s)[:, 1]
    try:
        auc = roc_auc_score(y_te, y_prob)
    except ValueError:
        auc = float("nan")

    print("\n" + "="*60)
    print("[BINARY CLASSIFICATION RESULTS]")
    print("="*60)
    print(classification_report(y_te, y_pred, target_names=["BENIGN","ATTACK"]))
    print(f"AUC-ROC: {auc:.4f}")
    print("Confusion matrix:\n", confusion_matrix(y_te, y_pred))

    # ─ 저장
    scaler_path = OUT_DIR / "ddos_scaler.pkl"
    model_path  = OUT_DIR / "ddos_binary_model.pkl"
    joblib.dump(scaler, scaler_path)
    joblib.dump(model , model_path)

    print(f"\nSaved scaler to {scaler_path}")
    print(f"Saved model  to {model_path}")
    print("Download them via the Colab Files panel on the left.")

# ────────── CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DDoS binary training (fast)")
    parser.add_argument("--data_dir", default=DEFAULT_DATA_DIR,
                        help="Path to CSV folder")
    args, _ = parser.parse_known_args()
    train(args.data_dir)