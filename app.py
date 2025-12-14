import pandas as pd
import os

DATA_PATH = "data/customers_local.parquet"

def load_customer_excel(uploaded_file):
    """업로드된 엑셀 파일을 읽어서 데이터프레임으로 반환"""
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        return None

def save_to_local(df):
    """데이터프레임을 로컬 Parquet 파일로 영구 저장"""
    # 날짜 컬럼 강제 변환 (안전장치)
    for col in ["생년월일", "계약일"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    df.to_parquet(DATA_PATH, index=False)
    return True

def load_from_local():
    """저장된 파일 불러오기"""
    if os.path.exists(DATA_PATH):
        return pd.read_parquet(DATA_PATH)
    return pd.DataFrame()