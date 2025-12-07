import streamlit as st
import pandas as pd
import numpy as np
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------------------------------------------------------------
# [UI 함수] 반응형 텍스트 (화면 꽉 차게 최대화)
# --------------------------------------------------------------------------
def responsive_text(text, type="title"):
    """
    화면 너비(vw)를 기준으로 폰트 크기를 최대한 키움 (Max Width)
    """
    if type == "title":
        # [메인 타이틀] 10~12글자 기준, 화면의 80% 이상 채우도록 설정
        # 기존 6vw -> 9vw로 대폭 확대
        style = "font-size: clamp(24px, 9vw, 50px); font-weight: 800; margin-bottom: 15px; white-space: nowrap; line-height: 1.2;"
        div_style = "margin-bottom: 10px;"
        
    elif type == "result_unified":
        # [진단 결과 & 예상 수명]
        # 가장 중요한 정보이므로 화면 밖으로 튀어 나가지 않는 선에서 제일 크게(Max)
        # 기존 5.5vw -> 8.5vw로 확대 (10글자 내외가 한 줄에 꽉 참)
        style = "font-size: clamp(26px, 8.5vw, 60px); font-weight: 900; line-height: 1.3; letter-spacing: -1px;" 
        div_style = "margin: 5px 0;"
        
    elif type == "subheader_one_line":
        # [신청 폼 제목]
        # 기존 4.5vw -> 6.5vw로 확대
        style = "font-size: clamp(18px, 6.5vw, 35px); font-weight: 700; white-space: nowrap;"
        div_style = "margin-top: 40px; margin-bottom: 10px;"
        
    else:
        style = "font-size: 16px;"
        div_style = ""
        
    st.markdown(f"""
    <div style="display: flex; justify-content: center; width: 100%; text-align: center; {div_style}">
        <span style="{style}">
            {text}
        </span>
    </div>
    """, unsafe_allow_html=True)

def emphasized_box(msg, status="SAFE"):
    """
    결과 해설 박스
    """
    if status == "DANGER":
        bg_color = "#FF4B4B" # 빨강
        icon = "🚨"
    elif status == "WARNING":
        bg_color = "#FFA421" # 주황
        icon = "⚠️"
    else:
        bg_color = "#3DD56D" # 초록
        icon = "🎉"
        
    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 25px;
        border-radius: 15px;
        margin-top: 20px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    ">
        <div style="font-size: clamp(22px, 7vw, 40px); font-weight: 800; color: white; line-height: 1.3; word-break: keep-all;">
            {icon} {msg}
        </div>
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
responsive_text("⛳ 나의 골프 수명 배터리", type="title")
st.markdown("<div style='text-align: center; opacity: 0.7; font-size: 1.0em; margin-bottom: 25px;'>👇 슬라이더를 움직여 미래를 확인하세요</div>", unsafe_allow_html=True)
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

# --------------------------------------------------------------------------
# 결과 표시 영역 (최대 크기)
# --------------------------------------------------------------------------

# 1. "진단 결과" 텍스트 (통일된 최대 크기)
responsive_text("📊 진단 결과", type="result_unified")

# 2. "예상 골프 수명" 텍스트 (통일된 최대 크기)
responsive_text(f"예상 골프 수명: {bankruptcy_age}세", type="result_unified")

# 배터리 계산
total_years = target_age - current_age
survive_years = bankruptcy_age - current_age
battery_percent = min(100, max(0, int((survive_years / total_years) * 100)))

st.progress(battery_percent / 100)

# 3. 해설 메시지 박스
if battery_percent >= 100:
    msg = f"완벽합니다!<br>{target_age}세까지 거뜬합니다!"
    status_code = "SAFE"
    result_msg = "자산 충분 (건강 리스크 대비 필요)"
elif battery_percent >= 70:
    msg = f"아슬아슬합니다.<br>{bankruptcy_age}세에 바닥납니다."
    status_code = "WARNING"
    shortfall = df_history[df_history['age'] == target_age]['balance'].values[0]
    result_msg = f"85세까지 {abs(shortfall):,.0f}원 부족"
else:
    msg = f"위험합니다!<br>{bankruptcy_age}세부터 파산입니다."
    status_code = "DANGER"
    shortfall = df_history[df_history['age'] == target_age]['balance'].values[0]
    result_msg = f"85세까지 {abs(shortfall):,.0f}원 부족"

emphasized_box(msg, status=status_code)

# 상세 금액 안내
if status_code != "SAFE":
    st.markdown(f"<div style='text-align: center; font-size: 1.2em; font-weight: bold; color: gray;'>📉 85세까지 약 {abs(shortfall // 10000):,.0f}만 원이 더 필요합니다.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='text-align: center; font-size: 1.2em; font-weight: bold; color: gray;'>📈 자금은 충분합니다. 이제 건강을 지키세요.</div>", unsafe_allow_html=True)


st.divider()

# --------------------------------------------------------------------------
# DB 수집 폼
# --------------------------------------------------------------------------
responsive_text("🎁 내 맞춤형 리포트 무료 신청", type="subheader_one_line")
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