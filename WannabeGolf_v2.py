import streamlit as st
import pandas as pd
import numpy as np
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --------------------------------------------------------------------------
# [UI 함수] 반응형 텍스트 (폰트 통일 및 디자인 수정)
# --------------------------------------------------------------------------
def responsive_text(text, type="title"):
    """
    type에 따라 글자 크기와 스타일을 다르게 적용
    """
    if type == "title":
        # [메인 타이틀]
        style = "font-size: clamp(20px, 6vw, 40px); font-weight: 700; margin-bottom: 10px; white-space: nowrap;"
        div_style = "margin-bottom: 10px;"
        
    elif type == "result_unified":
        # [수정됨] 진단 결과 & 예상 수명을 동일한 크기로 통일
        # clamp(최소, 가변, 최대) -> 헤드라인(st.header)과 비슷한 크기지만 반응형
        style = "font-size: clamp(22px, 5.5vw, 36px); font-weight: 800; line-height: 1.3; color: #31333F;" 
        # color를 지정하지 않으면 다크모드 자동 호환되지만, 강조를 위해 테마 텍스트 컬러 사용 권장. 
        # 여기서는 자동 색상 사용을 위해 color 속성 제거하고 굵기만 유지
        style = "font-size: clamp(22px, 5.5vw, 36px); font-weight: 800; line-height: 1.3;"
        div_style = "margin: 5px 0;"
        
    elif type == "subheader_one_line":
        # [신청 폼 제목]
        style = "font-size: clamp(16px, 4.5vw, 28px); font-weight: 700; white-space: nowrap;"
        div_style = "margin-top: 30px;"
        
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
    결과 해설 박스 (강조 디자인)
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
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="font-size: clamp(20px, 5vw, 32px); font-weight: 800; color: white; line-height: 1.4; word-break: keep-all;">
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
st.markdown("<div style='text-align: center; opacity: 0.7; font-size: 0.9em; margin-bottom: 20px;'>슬라이더를 움직여 미래를 확인하세요</div>", unsafe_allow_html=True)
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
# [수정] 결과 표시 영역 (폰트 크기 통일)
# --------------------------------------------------------------------------
# 기존 st.header("진단 결과") 삭제하고 아래 코드로 대체

# 1. "진단 결과" 텍스트 (통일된 크기)
responsive_text("📊 진단 결과", type="result_unified")

# 2. "예상 골프 수명" 텍스트 (통일된 크기)
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
    st.markdown(f"<div style='text-align: center; font-size: 1.1em; font-weight: bold; color: gray;'>📉 85세까지 약 {abs(shortfall // 10000):,.0f}만 원이 더 필요합니다.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='text-align: center; font-size: 1.1em; font-weight: bold; color: gray;'>📈 자금은 충분합니다. 이제 건강을 지키세요.</div>", unsafe_allow_html=True)


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