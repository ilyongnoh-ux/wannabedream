from datetime import datetime

def calc_dday(target_date):
    """날짜를 받아서 오늘 기준 D-Day 계산 (지난 날짜는 내년으로)"""
    if pd.isna(target_date):
        return 999 # 날짜 없으면 제외
        
    today = datetime.now().date()
    target = target_date.date()
    
    # 올해의 기념일로 변환
    this_year_target = target.replace(year=today.year)
    
    # 이미 지났으면 내년으로
    if this_year_target < today:
        next_target = this_year_target.replace(year=today.year + 1)
    else:
        next_target = this_year_target
        
    return (next_target - today).days

def apply_dday(df):
    """데이터프레임 전체에 D-Day 계산 적용"""
    import pandas as pd # 함수 내 import
    if df.empty: return df
    
    df["생일_DDAY"] = df["생년월일"].apply(calc_dday)
    df["계약_DDAY"] = df["계약일"].apply(calc_dday)
    return df