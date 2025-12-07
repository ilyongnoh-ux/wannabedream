import streamlit as st
import pandas as pd
import numpy as np
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------------------------------------------------------------
# [UI 함수] 화면 폭에 따라 폰트 크기 자동 조절 (한 줄 유지)
# --------------------------------------------------------------------------
def responsive_text(text, type="title", color="#000000"):
    """
    vw(viewport width) 단위를 사용하여 화면 너비에 따라 글자 크기가 변하도록 설정
    white-space: nowrap 속성으로 줄바꿈 강제 방지
    """
    if type == "title":
        # 제목용: 최소 20px, 최대 40px, 평소 화면의 6% 크기
        style = f"font-size: clamp(20px, 6vw, 40px); font-weight: 700; color: {color}; margin-bottom: 10px;"
    elif type == "result":
        # 결과용: 최소 18px, 최대 30px, 평소 화면의 5% 크기
        style = f"font-size: clamp(18px, 5vw, 30px); font-weight: 600; color: {color};"
    else:
        style = f"font-size: 16px; color: {color};"
        
    st.markdown(f"""
    <div style="display: flex; justify-content: center; width: 100%;">
        <span style="{style} white-space: nowrap; overflow: visible;">
            {text}
        </span>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# [기능] 구글 시트 연동 함수
# --------------------------------------------------------------------------
def save_to_google_sheet(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" in st.secrets:
            key_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
            
        client = gspread.authorize(creds)
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
# [변경] 기존 st.title 대신 반응형 텍스트 함수 사용
responsive_text("⛳ 나의 골프 수명 배터리", type="title")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.9em;'>슬라이더를 움직여 미래를 확인하세요</div>", unsafe_allow_html=True)
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

# [변경] 결과 메시지도 반응형으로 적용
responsive_text(f"예상 골프 수명: {bankruptcy_age}세", type="result", color="#333333")
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
# DB 수집 폼
# --------------------------------------------------------------------------
st.subheader("🎁 내 맞춤형 리포트 무료 신청")
st.info("신청하시면 '골프 자산 포트폴리오' PDF를 카카오톡으로 보내드립니다.")

with st.form("lead_form"):
    c1, c2 = st.columns(2)
    user_name = c1.text_input("성함", placeholder="홍길동")
    user_phone = c2.text_input("연락처", placeholder="010-0000-0000")
    agreement = st.checkbox("개인정보 수집 및 이용에 동의합니다.")
    submit_btn = st.form_submit_button("무료 리포트 받기", use_container_width=True)

    if submit_btn:
        if not user_name or not user_phone:
            st.warning("성함과 연락처를 모두 입력해주세요.")
        elif not agreement:
            st.warning("개인정보 동의에 체크해주세요.")
        else:
            save_data = [
                str(datetime.now()), 
                user_name, 
                user_phone, 
                current_age, 
                retire_age, 
                assets, 
                saving, 
                rounds, 
                bankruptcy_age, 
                result_msg 
            ]
            
            with st.spinner('데이터 저장 중...'):
                is_success = save_to_google_sheet(save_data)
                
            if is_success:
                st.success(f"{user_name}님! 신청이 완료되었습니다. 곧 연락드리겠습니다.")
                st.balloons()