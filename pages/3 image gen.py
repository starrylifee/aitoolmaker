import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime
import json

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="교사용 교육 도구 홈",  # 브라우저 탭에 표시될 제목
    page_icon="🧑‍🏫",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

# Streamlit의 배경색 변경
background_color = "#C5E1A5"  # 파스텔 그린

# 배경색 변경을 위한 CSS
page_bg_css = f"""
<style>
    .stApp {{
        background-color: {background_color};
    }}
</style>
"""

# Streamlit의 기본 메뉴와 푸터 숨기기
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden; }
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        var mainMenu = document.getElementById('MainMenu');
        if (mainMenu) {
            mainMenu.style.display = 'none';
        }
        var footer = document.getElementsByTagName('footer')[0];
        if (footer) {
            footer.style.display = 'none';
        }
        var header = document.getElementsByTagName('header')[0];
        if (header) {
            header.style.display = 'none';
        }
    });
    </script>
"""

# Streamlit에서 HTML 및 CSS 적용
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown(page_bg_css, unsafe_allow_html=True)

# Google Sheets 및 Google Drive API 인증 설정
credentials_dict = json.loads(st.secrets["gcp"]["credentials"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets"
])
gc = gspread.authorize(credentials)

# Google Drive API 클라이언트 생성
drive_service = build('drive', 'v3', credentials=credentials)

# 폴더 ID와 스프레드시트 이름 설정
folder_id = "1xJHiTJWXkeIhEOFBX2WyCb4fTQtGOIY-"  # 교사 페이지에 맞는 폴더 ID로 변경
spreadsheet_name = st.secrets["google"]["spreadsheet_name"]

# 폴더 내의 스프레드시트 파일 검색
with st.spinner('🔍 서버 데이터를 검색 중입니다...'):
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet' and name='{spreadsheet_name}'"
    results = drive_service.files().list(q=query).execute()
    items = results.get('files', [])

if not items:
    st.error('❌ 해당 폴더 내에서 서버 데이터를 찾을 수 없습니다.')
else:
    # 스프레드시트 ID로 열기
    spreadsheet_id = items[0]['id']
    spreadsheet = gc.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet("시트3")  # '시트3'에 데이터를 저장하도록 변경

    # 교사용 인터페이스
    st.title("🎨 교사용 이미지 생성 프롬프트 도구")

    st.markdown("""
    **안내:** 이 도구를 사용하여 교육 활동에 필요한 이미지 생성 프롬프트를 직접 입력하고 저장할 수 있습니다. 아래의 단계를 따라 입력해 주세요.
    1. **활동 코드**: 학생들이 입력할 고유 코드를 설정합니다. (숫자만으로 구성될 수 없습니다. 문자 또는 문자+숫자 조합만 허용됩니다.)
    2. **이미지 대상**: 생성하고자 하는 이미지의 대상을 간단하게 입력합니다.
    3. **프롬프트 저장**: 입력한 프롬프트를 저장하여 서버에 추가합니다.
    4. **학생용 앱과 연동**: 이곳에서 저장한 프롬프트는 [학생용 앱](https://students.streamlit.app/)에서 불러와 안전하게 AI를 사용할 수 있습니다.
    """)

    # 기존 활동 코드 리스트 가져오기
    existing_codes = worksheet.col_values(2)  # 스프레드시트에서 두 번째 열의 모든 값을 가져옴

    # 활동 코드 입력 (숫자만으로 입력된 경우 오류 처리 및 중복 검사)
    activity_code = st.text_input("🔑 활동 코드 입력", value=st.session_state.get('activity_code', '')).strip()

    if activity_code.isdigit():
        st.error("⚠️ 활동 코드는 숫자만으로 구성될 수 없습니다. 문자 또는 문자+숫자 조합을 사용하세요.")
        activity_code = ""  # 숫자만 입력된 경우 초기화
    elif activity_code in existing_codes:
        st.error("⚠️ 이미 사용된 코드입니다. 다른 코드를 입력해주세요.")
        activity_code = ""  # 중복된 경우 초기화
    else:
        st.session_state['activity_code'] = activity_code

    # 교사가 이미지 대상을 입력
    input_topic = st.text_input("🖼️ 이미지 대상을 간단하게 입력하세요 (예: '곰', '나무', '산'): ", "")

    # Email 및 Password 입력
    email = st.text_input("📧 Email (선택사항) 학생의 생성결과물을 받아볼 수 있습니다.", value=st.session_state.get('email', '')).strip()
    password = st.text_input("🔒 Password (선택사항) 저장한 프롬프트를 조회, 삭제할 수 있습니다.", value=st.session_state.get('password', ''), type="password").strip()

    # 프롬프트 바로 저장
    if st.button("💾 프롬프트를 서버에 저장") and activity_code:
        if input_topic:
            if password and password.isnumeric():
                st.error("⚠️ 비밀번호는 숫자만 입력할 수 없습니다. 영문 또는 영문+숫자 조합을 사용하세요.")
            else:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with st.spinner('💾 데이터를 저장하는 중입니다...'):
                    st.info("✅ 모든 입력값이 유효합니다. 서버에 데이터를 추가하는 중입니다...")

                    try:
                        worksheet.append_row([current_time, activity_code, input_topic, email, password])
                        st.success("🎉 프롬프트가 성공적으로 저장되었습니다.")
                        # 세션 상태 초기화
                        st.session_state.activity_code = ""
                        st.session_state.email = ""
                        st.session_state.password = ""

                    except Exception as e:
                        st.error(f"❌ 프롬프트 저장 중 오류가 발생했습니다: {e}")
        else:
            st.error("⚠️ 이미지 대상을 입력하세요.")