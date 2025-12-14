import streamlit as st
import sys
import os

# --- [경로 설정 시작] 이 코드가 import보다 무조건 위에 있어야 합니다 ---
# 현재 파일(pages 폴더)의 부모 폴더(프로젝트 루트)를 찾아서 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# ------------------------------------------------------------------

# 이제 시스템이 'core' 폴더를 볼 수 있습니다
from core.loader import load_from_local
from core.scheduler import apply_dday
from core.scorer import rank_customers
from core.logger import log_action

# ... (이 아래부터 기존 화면 코드 작성) ...
st.title("🚗 4. 동선 기반 추가 추천")

df = load_from_local()

if not df.empty:
    region = st.selectbox("오늘 방문할 지역은 어디인가요?", df["지역"].unique())
    
    nearby_customers = df[df["지역"] == region]
    st.success(f"📍 {region} 지역에 {len(nearby_customers)}명의 고객이 있습니다.")
    
    for idx, row in nearby_customers.iterrows():
        with st.expander(f"{row['고객명']} ({row['연락처']})"):
            st.write(f"메모: {row.get('메모', '-')}")
            if st.button("이 고객도 방문하기", key=f"route_{idx}"):
                log_action(row['고객명'], row['연락처'], "방문(동선)", region)
                st.success("기록됨")