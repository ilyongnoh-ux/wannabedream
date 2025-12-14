def calculate_score(row):
    """고객 1명의 우선순위 점수 계산"""
    score = 0
    
    # 1. 생일 임박 (3일전: 50점, 7일전: 30점)
    if 0 <= row["생일_DDAY"] <= 3:
        score += 50
    elif 4 <= row["생일_DDAY"] <= 7:
        score += 30
        
    # 2. 계약일 임박
    if 0 <= row["계약_DDAY"] <= 3:
        score += 40
    elif 4 <= row["계약_DDAY"] <= 7:
        score += 20
        
    # 3. 메모가 있으면 가산점
    if str(row["메모"]) != "nan" and str(row["메모"]) != "":
        score += 10
        
    return score

def rank_customers(df):
    """전체 고객 점수 매기기 및 정렬"""
    if df.empty: return df
    
    df["priority"] = df.apply(calculate_score, axis=1)
    # 점수 높은 순서로 정렬
    return df.sort_values("priority", ascending=False)