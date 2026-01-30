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
# 1. 통합 데이터 베이스 (기존 동일)
# ==========================================
class UniversalDB:
    def __init__(self):
        self.shipsin_desc = {
            "비견": "주체성/친구/경쟁", "겁재": "승부욕/투쟁/야망",
            "식신": "의식주/재능/온화", "상관": "천재성/언변/개혁",
            "편재": "사업운/큰재물/확장", "정재": "성실함/월급/신용",
            "편관": "권력/카리스마/인내", "정관": "명예/직장/원칙",
            "편인": "직관/눈치/아이디어", "정인": "학문/문서/수용",
            "일간": "나 자신(The Self)"
        }
        self.zodiac_dates = [
            (1, 20, "Aquarius", "물병자리", "혁신가"), (2, 19, "Pisces", "물고기자리", "예술가"),
            (3, 21, "Aries", "양자리", "개척자"), (4, 20, "Taurus", "황소자리", "안정가"),
            (5, 21, "Gemini", "쌍둥이자리", "소통왕"), (6, 22, "Cancer", "게자리", "보호자"),
            (7, 23, "Leo", "사자자리", "제왕"), (8, 23, "Virgo", "처녀자리", "분석가"),
            (9, 24, "Libra", "천칭자리", "조정자"), (10, 23, "Scorpio", "전갈자리", "승부사"),
            (11, 23, "Sagittarius", "사수자리", "모험가"), (12, 25, "Capricorn", "염소자리", "야망가")
        ]

# ==========================================
# 2. 통합 엔진 (기존 동일)
# ==========================================
class UniversalEngine:
    def __init__(self):
        self.db = UniversalDB()
        self.gan_hanja = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.ji_hanja = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        self.oh_map = {
            "목": {"color": "#00C73C", "text": "white"}, "화": {"color": "#FF4444", "text": "white"},
            "토": {"color": "#E6B800", "text": "black"}, "금": {"color": "#CCCCCC", "text": "black"},
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

    def get_daewoon(self, y_s, m_s, m_b, gender):
        is_yang = y_s % 2 == 0
        is_man = (gender == '남자')
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

    def generate_chart_image(self, target_eng, m, d):
        day_of_year = datetime.date(2000, m, d).timetuple().tm_yday
        sun_lon = (day_of_year - 80) * 0.986
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
            color = '#673ab7' if i == target_idx else '#88888822'
            ax.bar(np.deg2rad(i*30 + 15), 10, width=np.deg2rad(30), bottom=0, color=color, alpha=0.5, edgecolor='gray')
            ax.text(angle, 8.5, label[:3], ha='center', va='center', fontsize=9, color='gray', fontweight='bold')
        ax.text(np.deg2rad(sun_lon), 6, "☉", color='orange', fontsize=20, ha='center', va='center', fontweight='bold')
        plt.axis('off')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    def get_shipsin(self, me, target): 
        lookup = ["비견", "식상", "재성", "관성", "인성"]
        me_idx = ["목","화","토","금","수"].index(me)
        tg_idx = ["목","화","토","금","수"].index(target)
        diff = (tg_idx - me_idx + 5) % 5
        return lookup[diff]

    def get_zodiac_info(self, m, d):
        dates = UniversalDB().zodiac_dates
        z_eng, z_kor, z_desc = "Capricorn", "염소자리", "야망가"
        md = m * 100 + d
        for cm, cd, eng, kor, desc in dates:
            start_md = cm * 100 + cd
            idx = dates.index((cm, cd, eng, kor, desc))
            next_idx = (idx + 1) % 12
            nm, nd, _, _, _ = dates[next_idx]
            if eng == "Capricorn":
                if md >= 1225 or md <= 119: z_eng, z_kor, z_desc = eng, kor, desc; break
            else:
                if start_md <= md < (nm * 100 + nd): z_eng, z_kor, z_desc = eng, kor, desc; break
        return z_eng, z_kor, z_desc

    def generate_full_report(self, name, gender, y, m, d, h, is_lunar, solar_date_str):
        ganji = self.get_ganji(y, m, d, h)
        pillars = ["time", "day", "month", "year"]
        saju_data = []
        me_oh = self.gan_oh[ganji["day"][0]]
        for p in pillars:
            s_idx, b_idx = ganji[p]
            s_oh, b_oh = self.gan_oh[s_idx], self.ji_oh[b_idx]
            saju_data.append({
                "g_c": self.gan_hanja[s_idx], "j_c": self.ji_hanja[b_idx],
                "g_bg": self.oh_map[s_oh]['color'], "j_bg": self.oh_map[b_oh]['color'],
                "g_tc": self.oh_map[s_oh]['text'], "j_tc": self.oh_map[b_oh]['text'],
                "s_s": self.get_shipsin(me_oh, s_oh) if p != "day" else "<b>일간</b>",
                "b_s": self.get_shipsin(me_oh, b_oh)
            })
        daewoon = self.get_daewoon(ganji["year"][0], ganji["month"][0], ganji["month"][1], gender)
        z_eng, z_kor, z_desc = self.get_zodiac_info(m, d)
        chart_img = self.generate_chart_image(z_eng, m, d)
        
        # 랜덤 메시지 생성
        s_d_score = random.randint(75, 99)
        s_d_msg = random.choice(["귀인의 도움이 있는 날입니다.", "재물운이 상승합니다.", "뜻밖의 소식이 옵니다."])
        s_m_msg = random.choice(["이번 달은 변화가 길합니다.", "안정을 취하는 한 달이 되세요."])
        z_d_score = random.randint(70, 100)
        z_d_msg = random.choice(["직관력이 예리해집니다.", "소통에서 행운을 찾으세요."])
        z_m_msg = f"이달의 별들이 당신을 비춥니다."

        seen = set()
        terms = []
        for d_item in saju_data:
            for k in [d_item['s_s'], d_item['b_s']]:
                clean_k = k.replace("<b>","").replace("</b>","")
                if clean_k in UniversalDB().shipsin_desc and clean_k not in seen:
                    terms.append(clean_k); seen.add(clean_k)
        
        style = """<style>
            .container { display: flex; flex-direction: column; gap: 15px; }
            .panel { border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 12px; padding-bottom:10px; overflow: hidden; color: inherit; }
            .hd { padding: 12px; color: white; font-weight: bold; text-align: center; }
            .s-grid { display: flex; justify-content: space-around; padding: 15px 5px; border-bottom:1px dashed rgba(128, 128, 128, 0.3); }
            .s-col { display: flex; flex-direction: column; align-items: center; }
            .char { width: 50px; height: 50px; font-size: 26px; line-height: 50px; font-weight: bold; border-radius: 8px; margin: 2px; text-align: center; }
            .dw-box { display: flex; overflow-x: auto; padding: 10px; gap: 8px; background: rgba(128, 128, 128, 0.05); }
            .dw-cd { min-width: 50px; height: 65px; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; color:white; font-size:12px; font-weight:bold; }
            .card { margin: 10px; padding: 15px; border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 10px; background: rgba(128, 128, 128, 0.03); }
            .tag { font-size: 11px; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 5px; }
        </style>"""

        saju_html = f"""<div class="panel">
            <div class="hd" style="background:#333;">🔮 사주 결과 ({solar_date_str})</div>
            <div class="s-grid">
                {''.join([f'<div class="s-col"><span style="font-size:11px; opacity:0.7;">{p}주</span><div class="char" style="background:{d["g_bg"]}; color:{d["g_tc"]}">{d["g_c"]}</div><div class="char" style="background:{d["j_bg"]}; color:{d["j_tc"]}">{d["j_c"]}</div></div>' for p, d in zip(["시","일","월","년"], saju_data)])}
            </div>
            <div style="padding:8px 12px; font-weight:bold; font-size:13px; background:rgba(128,128,128,0.1);">🌊 대운 흐름</div>
            <div class="dw-box">{''.join([f"<div class='dw-cd' style='background:{d['bg']}; color:{d['tc']}'><span>{d['age']}</span><span>{d['gan']}{d['ji']}</span></div>" for d in daewoon])}</div>
            <div class="card" style="border-left: 5px solid #009688;"><span class="tag" style="background:#009688;">Monthly</span>{s_m_msg}</div>
            <div class="card" style="border-left: 5px solid #ff9800;"><span class="tag" style="background:#ff9800;">Daily</span>{s_d_msg} ({s_d_score}점)</div>
        </div>"""

        zodiac_html = f"""<div class="panel">
            <div class="hd" style="background:#673ab7;">✨ 별자리 운세 ({z_kor})</div>
            <div style="text-align:center; margin:15px 0;"><img src="data:image/png;base64,{chart_img}" style="width:260px; max-width:80%;"></div>
            <div class="card" style="border-left: 5px solid #9c27b0;"><span class="tag" style="background:#9c27b0;">Monthly</span>{z_m_msg}</div>
            <div class="card" style="border-left: 5px solid #e91e63;"><span class="tag" style="background:#e91e63;">Today</span>{z_d_msg} ({z_d_score}점)</div>
        </div>"""
        
        return f"{style}<div class='container'>{saju_html}{zodiac_html}</div>"

# ==========================================
# 3. Streamlit 앱 실행부
# ==========================================
def main():
    st.set_page_config(page_title="AI 운세 마스터", page_icon="🔮", layout="centered", initial_sidebar_state="collapsed")
    
    # 🌟 강력한 CSS 수정 (하단 바 및 로고 완전 제거 + 플로팅 버튼 최적화)
    st.markdown("""
        <style>
            /* 1. 하단 바, 로고, 푸터, 배지 완전 박멸 */
            #MainMenu, footer, header, [data-testid="stViewerBadge"], .viewerBadge_container__1QSob, 
            [data-testid="stAppDeployButton"], [data-testid="stStatusWidget"], .stDeployButton {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
            }
            
            /* 2. 스마트폰 하단 여백 제거 */
            .main .block-container { padding-bottom: 0px !important; }

            /* 3. 사이드바 버튼 -> 강력한 플로팅 버튼으로 변신 */
            [data-testid="stSidebarCollapsedControl"] {
                display: flex !important;
                visibility: visible !important;
                position: fixed !important;
                bottom: 100px !important; /* 조금 더 위로 */
                right: 20px !important;
                width: 140px !important;  /* 가로로 더 길게 */
                height: 60px !important;
                background-color: #ff4444 !important;
                color: white !important;
                border-radius: 30px !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
                z-index: 9999999 !important; /* 최상단 */
                justify-content: center !important;
                align-items: center !important;
                animation: pulse 2s infinite;
            }
            
            /* 버튼 텍스트 강제 삽입 */
            [data-testid="stSidebarCollapsedControl"]::after {
                content: "📋 정보입력";
                font-size: 16px !important;
                font-weight: bold !important;
                color: white !important;
            }
            
            /* 원래 있던 작은 화살표 아이콘 숨기기 */
            [data-testid="stSidebarCollapsedControl"] svg {
                display: none !important;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 68, 68, 0.7); }
                70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(255, 68, 68, 0); }
                100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 68, 68, 0); }
            }

            html, body, [data-testid="stAppViewContainer"] { color: inherit; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📱 AI 운세 마스터")
    st.info("우측 하단의 [📋 정보입력] 버튼을 눌러주세요.")
    
    with st.sidebar:
        st.header("정보 입력")
        name = st.text_input("이름", value="")
        gender = st.radio("성별", ["남자", "여자"])
        cal_type = st.radio("달력", ["양력", "음력"])
        is_leap = st.checkbox("윤달", value=False) if cal_type == "음력" else False
        birth_txt = st.text_input("생년월일 (8자리)", placeholder="19900101")
        b_time = st.time_input("태어난 시간", value=datetime.time(12, 0))
        btn_run = st.button("운세 분석 시작", type="primary")

    if btn_run:
        if not name or len(birth_txt) != 8:
            st.error("이름과 생년월일 8자리를 입력해주세요.")
            return
        engine = UniversalEngine()
        y, m, d = int(birth_txt[:4]), int(birth_txt[4:6]), int(birth_txt[6:8])
        h = b_time.hour
        solar_str = f"{y}-{m}-{d}"
        if cal_type == "음력":
            cal = KoreanLunarCalendar()
            cal.setLunarDate(y, m, d, is_leap)
            y, m, d = cal.solarYear, cal.solarMonth, cal.solarDay
            solar_str = f"{y}-{m}-{d} (음력)"
        
        with st.spinner("분석 중..."):
            html_report = engine.generate_full_report(name, gender, y, m, d, h, (cal_type=="음력"), solar_str)
            st.markdown(html_report, unsafe_allow_html=True)
            st.markdown("---")
            ad_content = """<div style="background-color: rgba(128, 128, 128, 0.08); border-radius: 10px; padding: 20px; text-align: center; border: 1px dashed rgba(128, 128, 128, 0.4); color: inherit;">
                <p style="opacity: 0.6; font-size: 11px; margin: 0;">ADVERTISEMENT</p>
                <div style="margin: 10px 0; font-weight: bold; color: #1a73e8;">성공적인 미래를 위한 오늘의 한걸음 🍀</div>
            </div>"""
            components.html(ad_content, height=110)
            st.caption("본 서비스는 엔터테인먼트용입니다.")

if __name__ == "__main__":
    main()