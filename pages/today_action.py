import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.loader import load_from_local
from core.scheduler import apply_dday
from core.scorer import rank_customers
from core.logger import log_action

st.title("🔥 2. 오늘의 추천 액션")

# 1. 로드 -> 2. D-Day계산 -> 3. 랭킹산정
df = load_from_local()

if df.empty:
    st.info("데이터가 없습니다. [1_데이터업로드] 메뉴를 먼저 이용해주세요.")
else:
    df = apply_dday(df)
    df = rank_customers(df)
    
    # 점수가 0보다 큰(연락할 이유가 있는) 고객만 필터링
    targets = df[df["priority"] > 0]
    
    st.subheader(f"오늘 연락 대상: {len(targets)}명")
    
    for idx, row in targets.iterrows():
        with st.container():
            st.markdown(f"### 👤 **{row['고객명']}** <small>({row['지역']})</small>", unsafe_allow_html=True)
            
            # 연락 이유 표시
            reasons = []
            if row['생일_DDAY'] <= 7: reasons.append(f"🎂 생일 D-{row['생일_DDAY']}")
            if row['계약_DDAY'] <= 7: reasons.append(f"📄 계약 D-{row['계약_DDAY']}")
            st.info(", ".join(reasons))
            
            # 액션 버튼
            c1, c2, c3 = st.columns(3)
            if c1.button("📞 전화", key=f"call_{idx}"):
                log_action(row['고객명'], row['연락처'], "전화", row['지역'])
                st.toast(f"{row['고객명']} 전화 기록 완료!")
                
            if c2.button("💬 카톡", key=f"msg_{idx}"):
                log_action(row['고객명'], row['연락처'], "카톡", row['지역'])
                st.toast(f"{row['고객명']} 카톡 기록 완료!")
                
            if c3.button("🚶 방문", key=f"visit_{idx}"):
                log_action(row['고객명'], row['연락처'], "방문", row['지역'])
                st.toast(f"{row['고객명']} 방문 기록 완료!")
            
            st.divider()