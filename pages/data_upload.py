import streamlit as st
import sys
import os

# --- [길 안내 코드: 이 3줄이 없으면 무조건 에러납니다] ---
# "내 현재 위치(pages)에서 한 단계 위(..)로 올라가서 core를 찾아라" 라는 뜻입니다.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --------------------------------------------------

# 이제 에러 없이 core를 불러올 수 있습니다
from core.loader import load_customer_excel, save_to_local

st.title("📂 1. 고객 엑셀 업로드")
st.info("이 데이터는 오직 대표님의 PC(로컬)에만 저장됩니다.")

uploaded = st.file_uploader("엑셀 파일을 올려주세요", type=['xlsx', 'xls'])

if uploaded:
    df = load_customer_excel(uploaded)
    if df is not None:
        st.write("데이터 미리보기:")
        st.dataframe(df.head(3))
        
        # 저장 버튼
        if st.button("💾 내 PC에 저장하기"):
            save_to_local(df)
            st.success(f"총 {len(df)}명의 데이터가 안전하게 저장되었습니다!")
            st.balloons()
        else:
            st.error(f"필수 컬럼이 없습니다. 확인해주세요: {required}")