import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime
import json

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
st.markdown(hide_menu_style, unsafe_allow_html=True)

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["api"]["keys"][0])

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
folder_id = "1xJHiTJWXkeIhEOFBX2WyCb4fTQtGOIY-"
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
    worksheet = spreadsheet.sheet1

    # 교사용 인터페이스
    st.title("🎓 교사용 프롬프트 생성 도구")

    st.markdown("""
    **안내:** 이 도구를 사용하여 교육 활동에 필요한 프롬프트를 쉽게 생성할 수 있습니다. 아래의 단계를 따라 입력해 주세요.
    1. **활동 코드**: 학생들이 입력할 고유 코드를 설정합니다. (숫자는 포함할 수 없습니다.)
    2. **프롬프트 주제**: 생성하고자 하는 프롬프트의 주제를 입력합니다.
    3. **프롬프트 생성**: 인공지능 또는 직접 입력한 프롬프트를 확인하고 필요에 따라 수정합니다.
    4. **프롬프트 저장**: 최종 프롬프트를 저장하여 서버에 추가합니다.
    """)

    # 활동 코드 입력 (숫자 포함 여부 검사)
    activity_code = st.text_input("🔑 활동 코드 입력", value=st.session_state.get('activity_code', '')).strip()
    
    if any(char.isdigit() for char in activity_code):
        st.error("⚠️ 활동 코드에 숫자를 포함할 수 없습니다. 다시 입력해주세요.")
        activity_code = ""  # 잘못된 입력일 경우 초기화
    else:
        st.session_state['activity_code'] = activity_code

    # 교사가 프롬프트 생성 방법 선택
    option = st.selectbox("프롬프트 생성 방법을 선택하세요:", ["직접 입력", "인공지능 사용"])

    if option == "직접 입력":
        # 교사가 직접 입력하는 경우 기본 예제를 제공
        example_prompt = "예시: 너는 A활동을 돕는 보조교사 입니다. 학생이 B를 입력하면, C를 할 수 있도록 도움을 주세요.."
        final_prompt = st.text_area("✏️ 직접 입력할 프롬프트:", example_prompt, height=300)
    else:
        # 교사가 주제를 입력
        input_topic = st.text_input("📚 프롬프트 주제 또는 키워드를 입력하세요:", "")

        if st.button("✨ 인공지능아 프롬프트를 만들어줘") and activity_code:
            # 교사의 입력을 바탕으로 GPT에게 프롬프트 생성 요청
            with st.spinner('🧠 프롬프트를 생성 중입니다...'):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # 적절한 GPT 모델을 선택
                    messages=[
                        {"role": "system", "content": "당신은 교육 목적으로 시스템 프롬프트를 만드는 것을 돕는 AI입니다."},
                        {"role": "user", "content": f"주제 '{input_topic}'에 대한 시스템 프롬프트를 만들어 주세요."}
                    ]
                )
                
                # 생성된 프롬프트를 교사에게 보여주기
                generated_prompt = response.choices[0].message.content.strip()

            # 교사가 프롬프트를 수정할 수 있도록 제공
            final_prompt = st.text_area("✏️ 인공지능이 만든 프롬프트를 살펴보고 직접 수정하세요:", generated_prompt, height=300)

        # final_prompt와 activity_code를 세션 상태에 저장
        st.session_state['final_prompt'] = final_prompt

    if st.button("💾 프롬프트를 서버에 저장") and activity_code:
        # 세션에서 저장된 값을 사용하여 Google Sheets에 데이터 추가
        if 'final_prompt' in st.session_state:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with st.spinner('💾 데이터를 저장하는 중입니다...'):
                st.info("✅ 모든 입력값이 유효합니다. 서버에 데이터를 추가하는 중입니다...")

                try:
                    worksheet.append_row([current_time, activity_code, st.session_state['final_prompt']])
                    st.success("🎉 프롬프트가 성공적으로 저장되었습니다.")
                except Exception as e:
                    st.error(f"❌ 프롬프트 저장 중 오류가 발생했습니다: {e}")
        else:
            st.error("⚠️ 프롬프트가 없습니다. 먼저 프롬프트를 생성하세요.")
