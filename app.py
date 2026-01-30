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
# 1. 통합 데이터 베이스
# ==========================================
class UniversalDB:
    def __init__(self):
        self.shipsin_desc = {
            "비견": "주체성/친구/경쟁", "겁재": "승부욕/투쟁/야망",
            "식신": "의식주/재능/온화", "상관": "천재성/언변/개혁",
            "편재": "사업운/큰재물/확장", "정재": "성실함/월급/신용",
            "편관": "권력/카리스마/인내", "정관": "명예/직장/원칙",
            "편인": "직관/눈치/아이디어", "정인": "학문/문서/수용",
            "일간": "나 자신"
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
# 2. 통합 엔진
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
        t_start = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}[d_stem]
        t_stem = (t_start + h_branch) % 10
        return {"year": (y_stem, y_branch), "month": (m_stem, m_branch), "day": (d_stem, d_branch), "time": (t_stem, h_branch)}

    def get_daewoon(self, y_s, m_s, m_b, gender):
        is_fwd = (y_s % 2 == 0 and gender == '남자') or (y_s % 2 != 0 and gender == '여자')
        curr_s, curr_b, lst = m_s, m_b, []
        for i in range(1, 9): # 미니 사이즈를 위해 8개로 조정
            if is_fwd: curr_s, curr_b = (curr_s + 1) % 10, (curr_b + 1) % 12
            else: curr_s, curr_b = (curr_s - 1 + 10) % 10, (curr_b - 1 + 12) % 12
            ji_elem = self.ji_oh[curr_b]
            lst.append({"age": 4+(i-1)*10, "gan": self.gan_hanja[curr_s], "ji": self.ji_hanja[curr_b], "bg": self.oh_map[ji_elem]['color'], "tc": self.oh_map[ji_elem]['text']})
        return lst

    def generate_chart_image(self, target_eng, m, d):
        day_of_year = datetime.date(2000, m, d).timetuple().tm_yday
        sun_lon = (day_of_year - 80) * 0.986
        fig = plt.figure(figsize=(3, 3)) # 사이즈 축소
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ax.set_ylim(0, 10)
        ax.set_yticks([]); ax.set_xticks([]); plt.axis('off')
        labels = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        target_idx = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].index(target_eng)
        for i, label in enumerate(labels):
            color = '#673ab7' if i == target_idx else '#88888822'
            ax.bar(np.deg2rad(i*30 + 15), 10, width=np.deg2rad(30), bottom=0, color=color, alpha=0.5, edgecolor='gray')
        ax.text(np.deg2rad(sun_lon), 6, "☉", color='orange', fontsize=18, ha='center', va='center', fontweight='bold')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    def generate_full_report(self, name, gender, y, m, d, h, is_lunar, solar_date_str):
        ganji = self.get_ganji(y, m, d, h)
        me_oh = self.gan_oh[ganji["day"][0]]
        saju_data = []
        for p in ["time", "day", "month", "year"]:
            s_idx, b_idx = ganji[p]; s_oh, b_oh = self.gan_oh[s_idx], self.ji_oh[b_idx]
            saju_data.append({"g_c": self.gan_hanja[s_idx], "j_c": self.ji_hanja[b_idx], "g_bg": self.oh_map[s_oh]['color'], "j_bg": self.oh_map[b_oh]['color'], "g_tc": self.oh_map[s_oh]['text'], "j_tc": self.oh_map[b_oh]['text']})
        
        daewoon = self.get_daewoon(ganji["year"][0], ganji["month"][0], ganji["month"][1], gender)
        z_eng, z_kor, z_desc = UniversalEngine().get_zodiac_info_static(m, d)
        chart_img = self.generate_chart_image(z_eng, m, d)

        style = """<style>
            .mini-card { border: 1px solid rgba(128,128,128,0.3); border-radius: 10px; margin-bottom: 10px; overflow: hidden; }
            .mini-hd { padding: 8px; font-size: 14px; text-align: center; color: white; font-weight: bold; }
            .s-grid { display: grid; grid-template-columns: repeat(4, 1fr); padding: 10px 5px; text-align: center; }
            .char { font-size: 20px; font-weight: bold; height: 40px; line-height: 40px; border-radius: 5px; margin: 2px; }
            .dw-scroll { display: flex; overflow-x: auto; padding: 5px; gap: 5px; background: rgba(128,128,128,0.05); }
            .dw-item { min-width: 40px; font-size: 11px; text-align: center; border-radius: 5px; padding: 5px 0; color: white; }
            .fortune-box { padding: 10px; font-size: 13px; border-left: 4px solid; margin: 8px; background: rgba(128,128,128,0.03); }
        </style>"""

        saju_html = f"""<div class="mini-card">
            <div class="mini-hd" style="background:#333;">🔮 사주 ({solar_date_str})</div>
            <div class="s-grid">
                {''.join([f'<div><div class="char" style="background:{d["g_bg"]}; color:{d["g_tc"]}">{d["g_c"]}</div><div class="char" style="background:{d["j_bg"]}; color:{d["j_tc"]}">{d["j_c"]}</div></div>' for d in saju_data])}
            </div>
            <div class="dw-scroll">{''.join([f'<div class="dw-item" style="background:{d["bg"]}; color:{d["tc"]}">{d["age"]}<br>{d["gan"]}{d["ji"]}</div>' for d in daewoon])}</div>
            <div class="fortune-box" style="border-color: #009688;"><b>[이달의 사주]</b> 변화가 길하게 작용합니다.</div>
            <div class="fortune-box" style="border-color: #ff9800;"><b>[오늘의 사주]</b> 귀인의 도움이 예상됩니다.</div>
        </div>"""

        zodiac_html = f"""<div class="mini-card">
            <div class="mini-hd" style="background:#673ab7;">✨ {z_kor} ({z_eng})</div>
            <div style="text-align:center; padding:10px;"><img src="data:image/png;base64,{chart_img}" style="width:200px;"></div>
            <div class="fortune-box" style="border-color: #9c27b0;"><b>[이달의 별자리]</b> 별들이 당신을 응원합니다.</div>
            <div class="fortune-box" style="border-color: #e91e63;"><b>[오늘의 별자리]</b> 직관을 믿고 나아가세요.</div>
        </div>"""
        
        return f"{style}{saju_html}{zodiac_html}"

    @staticmethod
    def get_zodiac_info_static(m, d):
        dates = UniversalDB().zodiac_dates
        md = m * 100 + d
        for i, (cm, cd, eng, kor, desc) in enumerate(dates):
            nm, nd = dates[(i + 1) % 12][:2]
            if eng == "Capricorn" and (md >= 1225 or md <= 119): return eng, kor, desc
            if (cm * 100 + cd) <= md < (nm * 100 + nd): return eng, kor, desc
        return "Capricorn", "염소자리", "야망가"

# ==========================================
# 3. 메인 앱 (아이폰 미니 대응 UI & 레이어 제어)
# ==========================================
def main():
    st.set_page_config(page_title="AI 운세", page_icon="🔮", layout="centered", initial_sidebar_state="collapsed")
    
    # 🌟 최상위 레이어 제어 및 하단 바 완전 박멸 자바스크립트/CSS
    st.markdown("""
        <script>
            function killStreamlitUI() {
                const elements = [
                    'footer', 'header', '[data-testid="stViewerBadge"]', 
                    '.viewerBadge_container__1QSob', '[data-testid="stAppDeployButton"]',
                    '[data-testid="stStatusWidget"]', '#MainMenu'
                ];
                elements.forEach(selector => {
                    const el = document.querySelector(selector);
                    if (el) {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.remove();
                    }
                });
                // 배경을 덮어씌우는 하단 가림막 생성
                if (!document.getElementById('shield')) {
                    const shield = document.createElement('div');
                    shield.id = 'shield';
                    shield.style = 'position:fixed; bottom:0; left:0; width:100%; height:50px; background:inherit; z-index:9999998;';
                    document.body.appendChild(shield);
                }
            }
            setInterval(killStreamlitUI, 50);
        </script>
        <style>
            /* 전체 화면 컴팩트화 */
            .main .block-container { padding: 1rem 0.5rem !important; max-width: 400px !important; }
            header, footer { display: none !important; }

            /* 플로팅 버튼 - 최상위 레이어 ($z$-index 극대화) */
            [data-testid="stSidebarCollapsedControl"] {
                display: flex !important;
                position: fixed !important;
                bottom: 30px !important;
                right: 20px !important;
                width: 120px !important;
                height: 50px !important;
                background-color: #ff4444 !important;
                border-radius: 25px !important;
                z-index: 9999999 !important; /* 그 어떤 요소보다 위 */
                box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
                justify-content: center !important;
                align-items: center !important;
                border: 2px solid #fff !important;
            }
            [data-testid="stSidebarCollapsedControl"] svg { display: none !important; }
            [data-testid="stSidebarCollapsedControl"]::after {
                content: "📝 정보입력";
                color: white !important;
                font-size: 14px !important;
                font-weight: bold !important;
            }
            html, body { color: inherit; background: transparent; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📱 AI 운세 마스터")
    
    with st.sidebar:
        st.header("입력창")
        name = st.text_input("이름", value="")
        gender = st.radio("성별", ["남자", "여자"], horizontal=True)
        cal_type = st.radio("달력", ["양력", "음력"], horizontal=True)
        birth_txt = st.text_input("생년월일 (8자리)", placeholder="19900101")
        b_time = st.time_input("시간", value=datetime.time(12, 0))
        btn_run = st.button("운세 보기", type="primary", use_container_width=True)

    if btn_run:
        if not name or len(birth_txt) != 8:
            st.error("정보를 채워주세요.")
        else:
            engine = UniversalEngine()
            y, m, d = int(birth_txt[:4]), int(birth_txt[4:6]), int(birth_txt[6:8])
            solar_str = f"{y}-{m}-{d}"
            if cal_type == "음력":
                cal = KoreanLunarCalendar()
                cal.setLunarDate(y, m, d, False)
                y, m, d = cal.solarYear, cal.solarMonth, cal.solarDay
                solar_str = f"{y}-{m}-{d} (음력)"
            
            with st.spinner("분석 중..."):
                html_report = engine.generate_full_report(name, gender, y, m, d, b_time.hour, (cal_type=="음력"), solar_str)
                st.markdown(html_report, unsafe_allow_html=True)
                
                # 하단 광고 영역
                st.write("---")
                ad_html = """<div style="background:rgba(128,128,128,0.1); border-radius:10px; padding:15px; text-align:center; border:1px dashed #888; color:inherit; font-size:12px;">
                    🍀 오늘의 행운을 잡으세요 🍀<br><b>[ADVERTISEMENT]</b></div>"""
                components.html(ad_html, height=80)

if __name__ == "__main__":
    main()