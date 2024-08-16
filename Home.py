import streamlit as st

# 페이지 설정 - 아이콘과 제목 설정
st.set_page_config(
    page_title="교사용 교육 도구 홈",  # 브라우저 탭에 표시될 제목
    page_icon="🧑‍🏫",  # 브라우저 탭에 표시될 아이콘 (이모지 또는 이미지 파일 경로)
)

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

# 홈 화면 제목
st.title("🎓 교사용 교육 도구 홈")

# 소개 문구
st.markdown("""
## 🛠️ 교사용 교육 도구 모음
이 페이지에서는 교육 활동을 지원하는 다양한 AI 및 이미지 기반 도구를 사용할 수 있습니다. 각 도구는 교사들이 쉽게 교육용 프롬프트를 생성하고 학생들에게 안전하게 적용할 수 있도록 설계되었습니다.
""")

# 도구 소개
st.header("1. 교사용 이미지분석 프롬프트 생성 도구")
st.markdown("""
이 도구를 사용하여 이미지분석 API를 활용한 교육용 프롬프트를 쉽게 생성할 수 있습니다. 학생들이 입력할 활동 코드를 설정하고, 주제를 입력하면, AI가 Vision API를 활용해 프롬프트를 생성하고 저장합니다.
""")

st.header("2. 교사용 프롬프트 생성 도구")
st.markdown("""
이 도구를 사용하여 교육 활동에 필요한 텍스트 프롬프트를 쉽게 생성할 수 있습니다. 주제를 입력하면, AI가 생성한 프롬프트를 확인하고 수정한 후 저장할 수 있습니다.
""")

st.header("3. 교사용 이미지 생성 프롬프트 도구")
st.markdown("""
이 도구를 사용하여 교육 활동에 필요한 이미지 생성 프롬프트를 직접 입력하고 저장할 수 있습니다. 이미지의 대상을 간단하게 입력하여, 학생들이 사용할 프롬프트를 손쉽게 생성하세요.
""")

# 이 페이지는 사용자가 각 도구의 목적과 기능을 이해하고, 필요에 따라 해당 도구를 선택해 사용할 수 있도록 안내하는 역할을 합니다.
