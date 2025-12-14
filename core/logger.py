import pandas as pd
import os
from datetime import datetime

LOG_PATH = "data/action_log.csv"

def log_action(name, contact, action_type, region):
    """버튼 클릭 시 로그 저장"""
    new_data = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "고객명": name,
        "연락처": contact,
        "행동": action_type,
        "지역": region
    }])
    
    if not os.path.exists(LOG_PATH):
        new_data.to_csv(LOG_PATH, index=False, encoding="utf-8-sig")
    else:
        new_data.to_csv(LOG_PATH, mode='a', header=False, index=False, encoding="utf-8-sig")