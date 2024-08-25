import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="교사용 프롬프트 조회/삭제 도구",  # 브라우저 탭에 표시될 제목
    page_icon="🧑‍🏫",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

# Streamlit의 배경색 변경
background_color = "#E0F7FA"  # 파스텔 블루

# Streamlit의 기본 메뉴와 푸터 숨기기
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""

# 배경색 변경을 위한 CSS
page_bg_css = f"""
<style>
    .stApp {{
        background-color: {background_color};
    }}
</style>
"""

# Streamlit에서 HTML 및 CSS 적용
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown(page_bg_css, unsafe_allow_html=True)

# Google Sheets 인증 설정
credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
])
gc = gspread.authorize(credentials)

# 스프레드시트 열기
spreadsheet = gc.open(st.secrets["google"]["spreadsheet_name"])

# 교사용 인터페이스
st.title("📄 교사용 프롬프트 조회/삭제 도구")

# UI에서 활동 선택
activity_type = st.selectbox("활동 유형을 선택하세요", ["이미지 분석", "텍스트 생성", "이미지 생성"])

# 선택한 활동 유형에 따라 시트 설정
if activity_type == "이미지 분석":
    worksheet = spreadsheet.worksheet("시트1")  # 비전
elif activity_type == "텍스트 생성":
    worksheet = spreadsheet.worksheet("시트2")  # 텍스트
elif activity_type == "이미지 생성":
    worksheet = spreadsheet.worksheet("시트3")  # 그림생성

# password 입력
password = st.text_input("🔑 비밀번호('영문'+'숫자'조합)를 입력하세요", type="password")

if password:
    # password에 해당하는 모든 데이터 검색
    records = worksheet.get_all_records()
    filtered_records = [record for record in records if record.get('password') == password]

    if filtered_records:
        st.success(f"✅ 비밀번호: {password}에 대한 데이터를 찾았습니다.")
        st.subheader("📄 저장된 프롬프트 목록")

        # 모든 setting_name과 프롬프트 출력
        for record in filtered_records:
            st.write(f"**설정 이름 (Setting Name):** {record['setting_name']}")
            st.write(f"**프롬프트:** {record['prompt']}")
            st.write("---")

        # 삭제할 setting_name 입력
        setting_name_to_delete = st.text_input("삭제할 설정 이름을 입력하세요 (Setting Name)")

        if setting_name_to_delete:
            if st.button("🗑️ 삭제"):
                # 특정 설정 이름 삭제
                row_to_delete = None
                for idx, record in enumerate(filtered_records):
                    if record.get('setting_name') == setting_name_to_delete:
                        row_to_delete = idx + 2  # 실제 시트에서의 행 번호는 리스트 인덱스에 2를 더한 값
                        break

                if row_to_delete:
                    worksheet.delete_rows(row_to_delete)
                    st.success(f"✅ 설정 이름 {setting_name_to_delete}에 해당하는 프롬프트가 삭제되었습니다.")
                else:
                    st.error("❌ 해당 설정 이름을 찾을 수 없습니다.")
    else:
        st.warning(f"⚠️ 비밀번호: {password}에 대한 데이터를 찾을 수 없습니다.")
else:
    st.info("비밀번호를 입력하여 데이터를 조회하세요.")
