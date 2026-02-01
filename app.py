# 필수 설치: pip install streamlit korean_lunar_calendar matplotlib numpy

import streamlit as st
import datetime
import random
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components
from korean_lunar_calendar import KoreanLunarCalendar

# ==========================================
# 0. 다국어 설정 (Language Pack)
# ==========================================
LANG_PACK = {
    "KO": {
        "title": "📱 AI 운세 마스터",
        "info": "왼쪽 상단의 버튼(👈)을 눌러 사주 정보를 입력해 주세요.",
        "sidebar_header": "정보 입력",
        "input_name": "이름",
        "input_gender": "성별",
        "gender_m": "남자",
        "gender_f": "여자",
        "cal_type": "달력",
        "cal_solar": "양력",
        "cal_lunar": "음력",
        "is_leap": "윤달 (음력)",
        "birth_txt": "생년월일 (8자리)",
        "birth_ph": "예: 19800101",
        "birth_time": "태어난 시간",
        "btn_run": "운세 분석 시작",
        "err_msg": "이름과 생년월일 8자리를 입력해주세요.",
        "loading": "천기누설 중...",
        "ad_title": "성공적인 미래를 위한 오늘의 한걸음 🍀",
        "ad_desc": "실제 광고 승인 후 이 영역에 광고가 표시됩니다.",
        "footer": "본 서비스는 엔터테인먼트용이며 법적 책임을 지지 않습니다.",
        "saju_title": "🔮 사주 명식",
        "daewoon_title": "🌊 대운 흐름",
        "ai_title": "📜 AI 도사의 감명",
        "zodiac_title": "✨ 천문 별자리 (Chart)",
        "z_monthly": "별자리 이달의 운세",
        "z_daily": "별자리 오늘의 운세",
        "s_monthly": "사주 월간 운세",
        "s_daily": "사주 오늘의 운세",
        "z_analysis": "📌 별자리 심층 분석"
    },
    "EN": {
        "title": "📱 AI Destiny Master",
        "info": "Press the button (👈) on the top left to enter your details.",
        "sidebar_header": "Input Details",
        "input_name": "Name",
        "input_gender": "Gender",
        "gender_m": "Male",
        "gender_f": "Female",
        "cal_type": "Calendar",
        "cal_solar": "Solar",
        "cal_lunar": "Lunar",
        "is_leap": "Leap Month",
        "birth_txt": "Birth Date (8 digits)",
        "birth_ph": "Ex: 19800101",
        "birth_time": "Birth Time",
        "btn_run": "Analyze Destiny",
        "err_msg": "Please enter your name and 8-digit birth date.",
        "loading": "Decoding the Heavens...",
        "ad_title": "A step towards a successful future 🍀",
        "ad_desc": "Ads will appear here after approval.",
        "footer": "This service is for entertainment purposes only.",
        "saju_title": "🔮 Four Pillars of Destiny",
        "daewoon_title": "🌊 Life Path (Daewoon)",
        "ai_title": "📜 AI Master's Reading",
        "zodiac_title": "✨ Zodiac Chart",
        "z_monthly": "Monthly Zodiac",
        "z_daily": "Daily Zodiac",
        "s_monthly": "Monthly Fortune",
        "s_daily": "Daily Fortune",
        "z_analysis": "📌 Zodiac Deep Dive"
    }
}

# ==========================================
# 1. 통합 데이터 베이스
# ==========================================
class UniversalDB:
    def __init__(self):
        # 다국어 지원을 위해 키는 한글로 유지하되, 표출 시 매핑
        self.shipsin_desc = {
            "비견": "Self/Friend", "겁재": "Competitor",
            "식신": "Talent/Food", "상관": "Genius/Rebel",
            "편재": "Big Wealth", "정재": "Stable Wealth",
            "편관": "Power/Stress", "정관": "Honor/Job",
            "편인": "Intuition", "정인": "Study/Doc",
            "일간": "The Self"
        }
        self.zodiac_dates = [
            (1, 20, "Aquarius", "물병자리", "Innovator"), (2, 19, "Pisces", "물고기자리", "Artist"),
            (3, 21, "Aries", "양자리", "Pioneer"), (4, 20, "Taurus", "황소자리", "Stabilizer"),
            (5, 21, "Gemini", "쌍둥이자리", "Communicator"), (6, 22, "Cancer", "게자리", "Protector"),
            (7, 23, "Leo", "사자자리", "King"), (8, 23, "Virgo", "처녀자리", "Analyst"),
            (9, 24, "Libra", "천칭자리", "Mediator"), (10, 23, "Scorpio", "전갈자리", "Strategist"),
            (11, 23, "Sagittarius", "사수자리", "Adventurer"), (12, 25, "Capricorn", "염소자리", "Ambitious")
        ]

# ==========================================
# 2. 통합 엔진 (로직)
# ==========================================
class UniversalEngine:
    def __init__(self):
        self.db = UniversalDB()
        self.gan_hanja = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.ji_hanja = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        self.oh_map = {
            "목": {"color": "#00C73C", "text": "white"}, "화": {"color": "#FF4444", "text": "white"},
            "토": {"color": "#E6B800", "text": "black"}, "금": {"color": "#DDDDDD", "text": "black"},
            "수": {"color": "#333333", "text": "white"}
        }
        self.gan_oh = ["목", "목", "화", "화", "토", "토", "금", "금", "수", "수"]
        self.ji_oh = ["수", "토", "목", "목", "토", "화", "화", "토", "금", "금", "토", "수"]

    def get_ganji(self, y, m, d, h):
        base = datetime.date(1900, 1, 1)
        target = datetime.date(y, m, d)
        diff = (target - base).days
        y_stem = (6 + (y - 1900)) % 10
        y_branch = (0 + (y - 1900)) % 12
        m_start = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}[y_stem]
        m_stem = (m_start + (m - 2)) % 10
        m_branch = (m + 1) % 12
        if m < 2: m_stem = (m_stem + 10) % 10
        d_stem = (0 + diff) % 10
        d_branch = (10 + diff) % 12
        h_branch = (h + 1) // 2 % 12
        t_start_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
        t_start = t_start_map[d_stem]
        t_stem = (t_start + h_branch) % 10
        return {"year": (y_stem, y_branch), "month": (m_stem, m_branch), "day": (d_stem, d_branch), "time": (t_stem, h_branch)}

    def get_shipsin(self, me, target): 
        lookup = ["비견", "식상", "재성", "관성", "인성"]
        me_idx = ["목","화","토","금","수"].index(me)
        tg_idx = ["목","화","토","금","수"].index(target)
        diff = (tg_idx - me_idx + 5) % 5
        return lookup[diff]

    def get_daewoon(self, y_s, m_s, m_b, gender, lang_code):
        is_yang = y_s % 2 == 0
        is_man = (gender == '남자' or gender == 'Male')
        is_fwd = (is_yang and is_man) or (not is_yang and not is_man)
        curr_s, curr_b, lst = m_s, m_b, []
        for i in range(1, 10):
            if is_fwd: curr_s, curr_b = (curr_s + 1) % 10, (curr_b + 1) % 12
            else: curr_s, curr_b = (curr_s - 1 + 10) % 10, (curr_b - 1 + 12) % 12
            ji_elem = self.ji_oh[curr_b]
            lst.append({
                "age": 4+(i-1)*10, "gan": self.gan_hanja[curr_s], "ji": self.ji_hanja[curr_b], 
                "bg": self.oh_map[ji_elem]['color'], "tc": self.oh_map[ji_elem]['text']
            })
        return lst

    def get_zodiac_info(self, m, d):
        dates = self.db.zodiac_dates
        z_eng, z_kor, z_desc = "Capricorn", "염소자리", "Ambitious"
        md = m * 100 + d
        for cm, cd, eng, kor, desc in dates:
            start_md = cm * 100 + cd
            idx = dates.index((cm, cd, eng, kor, desc))
            next_idx = (idx + 1) % 12
            nm, nd, _, _, _ = dates[next_idx]
            if eng == "Capricorn":
                if md >= 1225 or md <= 119:
                    z_eng, z_kor, z_desc = eng, kor, desc; break
            else:
                end_md = nm * 100 + nd
                if start_md <= md < end_md:
                    z_eng, z_kor, z_desc = eng, kor, desc; break
        return z_eng, z_kor, z_desc

    def generate_chart_image(self, target_eng, m, d):
        day_of_year = datetime.date(2000, m, d).timetuple().tm_yday
        vern_equinox = datetime.date(2000, 3, 21).timetuple().tm_yday
        diff_days = day_of_year - vern_equinox
        if diff_days < 0: diff_days += 365
        sun_lon = diff_days * 0.986 
        fig = plt.figure(figsize=(4, 4))
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ax.set_ylim(0, 10)
        ax.set_yticks([])
        ax.set_xticks(np.deg2rad(np.arange(0, 360, 30)))
        ax.set_xticklabels([])
        labels = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        target_idx = labels.index(target_eng)
        for i, label in enumerate(labels):
            angle = np.deg2rad(i * 30 + 15)
            color = '#9c27b0' if i == target_idx else '#808080'
            alpha = 0.9 if i == target_idx else 0.15
            ax.bar(np.deg2rad(i*30 + 15), 10, width=np.deg2rad(30), bottom=0, color=color, alpha=alpha, edgecolor='none')
            ax.text(angle, 8.5, label[:3], ha='center', va='center', fontsize=9, color='#888', fontweight='bold')
        sun_angle = np.deg2rad(sun_lon)
        ax.text(sun_angle, 6, "☉", color='orange', fontsize=20, ha='center', va='center', fontweight='bold')
        plt.axis('off')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    def generate_full_report(self, name, gender, y, m, d, h, is_lunar, solar_date_str, lang_code):
        L = LANG_PACK[lang_code]
        ganji = self.get_ganji(y, m, d, h)
        pillars = ["time", "day", "month", "year"]
        saju_data = []
        me_oh = self.gan_oh[ganji["day"][0]]
        
        # 다국어 십신 변환
        def trans_ship(ship_kor):
            return self.db.shipsin_desc.get(ship_kor, ship_kor) if lang_code == "EN" else ship_kor

        for p in pillars:
            s_idx, b_idx = ganji[p]
            s_oh, b_oh = self.gan_oh[s_idx], self.ji_oh[b_idx]
            s_ship = self.get_shipsin(me_oh, s_oh)
            b_ship = self.get_shipsin(me_oh, b_oh)
            if p=="day": s_ship="<b>일간(Self)</b>" if lang_code=="EN" else "<b>일간</b>"
            
            saju_data.append({
                "g_c": self.gan_hanja[s_idx], "j_c": self.ji_hanja[b_idx],
                "g_bg": self.oh_map[s_oh]['color'], "j_bg": self.oh_map[b_oh]['color'],
                "g_tc": self.oh_map[s_oh]['text'], "j_tc": self.oh_map[b_oh]['text'],
                "s_s": trans_ship(s_ship), "b_s": trans_ship(b_ship)
            })
            
        daewoon = self.get_daewoon(ganji["year"][0], ganji["month"][0], ganji["month"][1], gender, lang_code)
        z_eng, z_kor, z_desc = self.get_zodiac_info(m, d)
        z_display_name = z_kor if lang_code == "KO" else z_eng
        chart_img = self.generate_chart_image(z_eng, m, d)
        
        # 메시지 생성 (다국어 분기)
        random.seed(int(f"{y}{m}{d}") + datetime.datetime.now().day)
        s_d_score = random.randint(70, 99)
        z_d_score = random.randint(60, 100)
        
        if lang_code == "KO":
            s_d_msg = random.choice(["귀인의 도움이 있습니다.", "재물운이 상승합니다.", "건강을 챙기세요.", "뜻밖의 행운이 옵니다."])
            s_m_msg = random.choice(["이동수가 있는 달입니다.", "안정을 취하면 길합니다.", "새로운 인연이 찾아옵니다."])
            z_d_msg = random.choice(["직관력이 높아지는 날입니다.", "주변 사람과 대화하세요.", "창의적인 아이디어가 떠오릅니다."])
            z_m_keyword = random.choice(["사랑", "변화", "성공", "치유", "열정"])
            z_m_msg = f"이번 달의 키워드는 '{z_m_keyword}'입니다."
            ai_reading = f"{name}님은 <b>{me_oh}</b> 일간의 기질을 타고났습니다.<br>조화를 이루면 큰 성취가 있을 것입니다."
        else:
            s_d_msg = random.choice(["A noble person will help you.", "Wealth luck is rising.", "Watch your health.", "Unexpected luck is coming."])
            s_m_msg = random.choice(["A month of movement.", "Stability brings luck.", "New relationships arrive."])
            z_d_msg = random.choice(["Intuition is high today.", "Talk to people around you.", "Creative ideas will flow."])
            z_m_keyword = random.choice(["Love", "Change", "Success", "Healing", "Passion"])
            z_m_msg = f"This month's keyword is '{z_m_keyword}'."
            ai_reading = f"{name} is born with the energy of <b>{me_oh}</b>.<br>Harmony will bring great achievement."

        # CSS 및 HTML 조립 (이전과 동일하되 다국어 변수 적용)
        style = """
        <style>
            .container { display: flex; flex-direction: column; width: 100%; gap: 15px; font-family: sans-serif; }
            .panel { width: 100%; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 12px; background: transparent; padding-bottom:10px; overflow: hidden; color: inherit; }
            .hd { padding: 12px; color: white; font-weight: bold; text-align: center; font-size: 16px; }
            .s-grid { display: flex; justify-content: space-around; padding: 15px 5px; border-bottom:1px dashed rgba(128, 128, 128, 0.3); }
            .s-col { display: flex; flex-direction: column; align-items: center; }
            .char { width: 50px; height: 50px; font-size: 26px; line-height: 50px; font-weight: bold; border-radius: 8px; margin: 2px; text-align: center; box-shadow: 1px 1px 3px rgba(0,0,0,0.2); }
            .dw-box { display: flex; overflow-x: auto; padding: 10px; gap: 8px; background: rgba(128, 128, 128, 0.05); }
            .dw-cd { min-width: 50px; height: 65px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; color:white; font-size:12px; font-weight:bold; flex-shrink: 0; }
            .card { margin: 10px; padding: 15px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 10px; background: rgba(128, 128, 128, 0.03); color: inherit; }
            .tag { font-size: 11px; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 5px; vertical-align: middle; }
            .z-title { font-size: 24px; font-weight: bold; color: #673ab7; text-align: center; margin-top:10px; }
            .chart-box { text-align: center; margin: 15px 0; }
            .chart-img { width: 280px; max-width: 80%; }
        </style>
        """

        saju_html = f"""
        <div class="panel">
            <div class="hd" style="background:#333;">{L['saju_title']} ({solar_date_str})</div>
            <div class="s-grid">
                <div class="s-col">
                    <span style="font-size:12px; opacity:0.8;">Time</span>
                    <div class="char" style="background:{saju_data[0]['g_bg']}; color:{saju_data[0]['g_tc']}">{saju_data[0]['g_c']}</div>
                    <div class="char" style="background:{saju_data[0]['j_bg']}; color:{saju_data[0]['j_tc']}">{saju_data[0]['j_c']}</div>
                    <span style="font-size:10px;">{saju_data[0]['s_s']}</span>
                </div>
                <div class="s-col">
                    <span style="font-size:12px; opacity:0.8;">Day</span>
                    <div class="char" style="background:{saju_data[1]['g_bg']}; color:{saju_data[1]['g_tc']}">{saju_data[1]['g_c']}</div>
                    <div class="char" style="background:{saju_data[1]['j_bg']}; color:{saju_data[1]['j_tc']}">{saju_data[1]['j_c']}</div>
                    <span style="font-size:10px; color:#2196f3;">{saju_data[1]['s_s']}</span>
                </div>
                <div class="s-col">
                    <span style="font-size:12px; opacity:0.8;">Month</span>
                    <div class="char" style="background:{saju_data[2]['g_bg']}; color:{saju_data[2]['g_tc']}">{saju_data[2]['g_c']}</div>
                    <div class="char" style="background:{saju_data[2]['j_bg']}; color:{saju_data[2]['j_tc']}">{saju_data[2]['j_c']}</div>
                    <span style="font-size:10px;">{saju_data[2]['s_s']}</span>
                </div>
                <div class="s-col">
                    <span style="font-size:12px; opacity:0.8;">Year</span>
                    <div class="char" style="background:{saju_data[3]['g_bg']}; color:{saju_data[3]['g_tc']}">{saju_data[3]['g_c']}</div>
                    <div class="char" style="background:{saju_data[3]['j_bg']}; color:{saju_data[3]['j_tc']}">{saju_data[3]['j_c']}</div>
                    <span style="font-size:10px;">{saju_data[3]['s_s']}</span>
                </div>
            </div>
            <div style="padding:8px 12px; font-weight:bold; font-size:14px; background:rgba(128,128,128,0.1);">{L['daewoon_title']}</div>
            <div class="dw-box">
                {''.join([f"<div class='dw-cd' style='background:{d['bg']}; color:{d['tc']}'><span>{d['age']}</span><span>{d['gan']}{d['ji']}</span></div>" for d in daewoon])}
            </div>
            <div class="card" style="border-left: 5px solid #333;">
                <div style="font-weight:bold; font-size:15px; margin-bottom:5px;">{L['ai_title']}</div>
                <div style="font-size:14px; line-height:1.6;">{ai_reading}</div>
            </div>
            <div class="card" style="border-left: 5px solid #009688;">
                <div style="font-weight:bold; font-size:15px;"><span class="tag" style="background:#009688;">Monthly</span>{L['s_monthly']}</div>
                <div style="font-size:14px; margin-top:8px;">{s_m_msg}</div>
            </div>
            <div class="card" style="border-left: 5px solid #ff9800;">
                <div style="font-weight:bold; font-size:15px;"><span class="tag" style="background:#ff9800;">Daily</span>{L['s_daily']} ({s_d_score} pts)</div>
                <div style="font-size:14px; margin-top:8px;">{s_d_msg}</div>
            </div>
        </div>
        """

        zodiac_html = f"""
        <div class="panel">
            <div class="hd" style="background:#673ab7;">{L['zodiac_title']}</div>
            <div class="z-title">{z_display_name}</div>
            <div style="text-align:center; opacity:0.7; font-size:14px; margin-bottom:10px;">"{z_desc}"</div>
            <div class="chart-box">
                <img src="data:image/png;base64,{chart_img}" class="chart-img">
            </div>
            <div class="card" style="border-left: 5px solid #9c27b0;">
                <div style="font-weight:bold; font-size:15px;"><span class="tag" style="background:#9c27b0;">Monthly</span>{L['z_monthly']}</div>
                <div style="font-size:14px; margin-top:8px;">{z_m_msg}</div>
            </div>
            <div class="card" style="border-left: 5px solid #e91e63;">
                <div style="font-weight:bold; font-size:15px;"><span class="tag" style="background:#e91e63;">Daily</span>{L['z_daily']} ({z_d_score} pts)</div>
                <div style="font-size:14px; margin-top:8px;">{z_d_msg}</div>
            </div>
        </div>
        """
        final_html = f"{style}<div class='container'>{saju_html}{zodiac_html}</div>"
        return final_html

# ==========================================
# 3. Streamlit 앱 실행부
# ==========================================
def main():
    st.set_page_config(page_title="AI 운세/Destiny", page_icon="🔮", layout="centered", initial_sidebar_state="collapsed")
    
    # 세션 스테이트 초기화 (언어 설정)
    if 'lang' not in st.session_state:
        st.session_state.lang = "KO" # 기본값 한국어

    # 사이드바에서 언어 선택
    with st.sidebar:
        sel_lang = st.radio("Language / 언어", ["한국어", "English"])
        if sel_lang == "한국어":
            st.session_state.lang = "KO"
        else:
            st.session_state.lang = "EN"

    L = LANG_PACK[st.session_state.lang]

    # 스타일 적용 (생략: 기존 코드와 동일)
    st.markdown("""
        <style>
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { background: transparent !important; height: 3rem !important; }
            html, body, [data-testid="stAppViewContainer"] { color: inherit; }
            [data-testid="stSidebarCollapsedControl"] {
                background-color: #ff4444 !important; color: white !important;
                border-radius: 50% !important; width: 45px !important; height: 45px !important;
                z-index: 999999 !important; animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7); }
                70% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(255, 68, 68, 0); }
                100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 68, 68, 0); }
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title(L['title'])
    st.info(L['info'])
    
    with st.sidebar:
        st.header(L['sidebar_header'])
        name = st.text_input(L['input_name'], value="")
        
        # 성별 선택 다국어 처리
        gender_opts = [L['gender_m'], L['gender_f']]
        gender_sel = st.radio(L['input_gender'], gender_opts)
        
        cal_opts = [L['cal_solar'], L['cal_lunar']]
        cal_type = st.radio(L['cal_type'], cal_opts)
        
        is_leap = False
        if cal_type == L['cal_lunar']:
            is_leap = st.checkbox(L['is_leap'], value=False)
            
        birth_txt = st.text_input(L['birth_txt'], placeholder=L['birth_ph'])
        b_time = st.time_input(L['birth_time'], value=datetime.time(12, 0))
        btn_run = st.button(L['btn_run'], type="primary")

    if btn_run:
        if not name or len(birth_txt) != 8:
            st.error(L['err_msg'])
            return
        engine = UniversalEngine()
        y, m, d = int(birth_txt[:4]), int(birth_txt[4:6]), int(birth_txt[6:8])
        h = b_time.hour
        solar_str = f"{y}-{m}-{d}"
        if cal_type == L['cal_lunar']:
            cal = KoreanLunarCalendar()
            cal.setLunarDate(y, m, d, is_leap)
            y, m, d = cal.solarYear, cal.solarMonth, cal.solarDay
            solar_str = f"{y}-{m}-{d} (Lunar Conv.)"
            
        with st.spinner(L['loading']):
            html_report = engine.generate_full_report(name, gender_sel, y, m, d, h, (cal_type==L['cal_lunar']), solar_str, st.session_state.lang)
            st.markdown(html_report, unsafe_allow_html=True)
            st.markdown("---")
            ad_content = f"""
            <div style="background-color: rgba(128, 128, 128, 0.1); border-radius: 10px; padding: 20px; text-align: center; border: 1px dashed rgba(128, 128, 128, 0.3); color: inherit;">
                <p style="opacity: 0.7; font-size: 12px; margin: 0;">ADVERTISEMENT</p>
                <div style="margin: 10px 0; font-weight: bold; color: #1a73e8;">{L['ad_title']}</div>
                <p style="opacity: 0.8; font-size: 14px;">{L['ad_desc']}</p>
            </div>
            """
            components.html(ad_content, height=150)
            st.caption(L['footer'])

if __name__ == "__main__":
    main()
