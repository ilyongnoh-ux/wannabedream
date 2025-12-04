import streamlit as st
import pandas as pd
import numpy as np
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------------------------------------------------------------
# [설정] 구글 시트 연동 함수
# --------------------------------------------------------------------------
# [수정된 부분] 구글 시트 연동 함수 (로컬/클라우드 호환)
def save_to_google_sheet(data):
    try:
        # 인증 범위 설정
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # [변경점] secrets에서 정보를 가져와서 딕셔너리로 만듦
        # Streamlit Cloud 환경인지 확인
        if "gcp_service_account" in st.secrets:
            key_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        else:
            # 로컬 환경 (기존 방식)
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
            
        client = gspread.authorize(creds)

        # 시트 열기
        sheet = client.open("WannabeDB").sheet1 
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"DB 저장 중 오류가 발생했습니다: {e}")
        return False

# --------------------------------------------------------------------------
# 페이지 기본 설정
# --------------------------------------------------------------------------
st.set_page_config(page_title="Wannabe Golf - Life Battery", page_icon="⛳", layout="centered")

# --------------------------------------------------------------------------
# 핵심 계산 엔진
# --------------------------------------------------------------------------
def calculate_golf_life(current_age, retire_age, target_age, assets, saving, rounds, cost_per_round):
    inflation_rate = 0.03
    roi_rate = 0.04
    balance = assets
    bankruptcy_age = target_age + 1
    status = "SAFE"
    history = []
    
    for age in range(current_age, target_age + 5):
        annual_income = (saving * 12) if age < retire_age else 0
        years_passed = age - current_age
        current_annual_cost = rounds * cost_per_round * 12
        inflated_cost = current_annual_cost * ((1 + inflation_rate) ** years_passed)
        
        balance = balance * (1 + roi_rate) + annual_income - inflated_cost
        history.append({"age": age, "balance": int(balance)})
        
        if balance < 0 and status == "SAFE":
            bankruptcy_age = age
            status = "DANGER"
    
    return bankruptcy_age, status, pd.DataFrame(history)

# --------------------------------------------------------------------------
# UI 구성
# --------------------------------------------------------------------------
st.title("⛳ 나의 골프 수명 배터리")
st.markdown("### 슬라이더를 움직여 미래를 확인하세요")
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏌️‍♂️ 라이프스타일")
    current_age = st.number_input("현재 나이", value=54, min_value=30, max_value=80)
    retire_age = st.slider("은퇴 예정 나이", 50, 75, 60)
    rounds = st.slider("월 라운딩 횟수 (회)", 0, 10, 4)
    cost = st.select_slider("회당 비용 (그늘집 포함)", options=[20, 30, 35, 40, 50, 70], value=35) * 10000

with col2:
    st.subheader("💰 자산 현황")
    assets = st.slider("현재 골프 자금 (만원)", 0, 50000, 10000, step=1000) * 10000
    saving = st.slider("월 추가 저축액 (만원)", 0, 500, 0, step=10) * 10000

# 계산 실행
target_age = 85
bankruptcy_age, status, df_history = calculate_golf_life(current_age, retire_age, target_age, assets, saving, rounds, cost)

st.divider()
st.header("진단 결과")

# 배터리 로직
total_years = target_age - current_age
survive_years = bankruptcy_age - current_age
battery_percent = min(100, max(0, int((survive_years / total_years) * 100)))

if battery_percent >= 100:
    color = "green"
    msg = f"완벽합니다! {target_age}세까지 거뜬합니다. 🎉"
elif battery_percent >= 70:
    color = "orange"
    msg = f"아슬아슬합니다. {bankruptcy_age}세에 자금이 바닥납니다. ⚠️"
else:
    color = "red"
    msg = f"위험합니다! {bankruptcy_age}세부터 골프 파산입니다. 🚨"

st.markdown(f"### 예상 골프 수명: **{bankruptcy_age}세**")
st.progress(battery_percent / 100)

if status == "DANGER":
    st.error(msg)
    shortfall = df_history[df_history['age'] == target_age]['balance'].values[0]
    result_msg = f"85세까지 {abs(shortfall):,.0f}원 부족"
    st.write(f"📉 {result_msg}")
else:
    st.success(msg)
    result_msg = "자산 충분 (건강 리스크 대비 필요)"
    st.write(f"📈 {result_msg}")

st.divider()

# --------------------------------------------------------------------------
# [NEW] DB 수집 폼 (Form)
# --------------------------------------------------------------------------
st.subheader("🎁 내 맞춤형 리포트 무료 신청")
st.info("신청하시면 '골프 자산 포트폴리오' PDF를 카카오톡으로 보내드립니다.")

with st.form("lead_form"):
    # 고객 정보 입력 필드 추가
    c1, c2 = st.columns(2)
    user_name = c1.text_input("성함", placeholder="홍길동")
    user_phone = c2.text_input("연락처", placeholder="010-0000-0000")
    
    # 개인정보 동의 (형식상)
    agreement = st.checkbox("개인정보 수집 및 이용에 동의합니다.")
    
    submit_btn = st.form_submit_button("무료 리포트 받기", use_container_width=True)

    if submit_btn:
        if not user_name or not user_phone:
            st.warning("성함과 연락처를 모두 입력해주세요.")
        elif not agreement:
            st.warning("개인정보 동의에 체크해주세요.")
        else:
            # 저장할 데이터 리스트 구성
            save_data = [
                str(datetime.now()), # 시간
                user_name,           # 이름
                user_phone,          # 전화번호
                current_age,         # 나이
                retire_age,          # 은퇴나이
                assets,              # 자산
                saving,              # 저축액
                rounds,              # 라운딩횟수
                bankruptcy_age,      # 파산나이
                result_msg           # 진단결과
            ]
            
            with st.spinner('데이터 저장 중...'):
                is_success = save_to_google_sheet(save_data)
                
            if is_success:
                st.success(f"{user_name}님! 신청이 완료되었습니다. 곧 연락드리겠습니다.")
                st.balloons() # 성공 축하 효과