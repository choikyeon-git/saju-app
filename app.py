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
            "비견": "주체성", "겁재": "승부욕",
            "식신": "의식주", "상관": "천재성",
            "편재": "사업운", "정재": "성실함",
            "편관": "카리스마", "정관": "원칙",
            "편인": "직관", "정인": "수용",
            "일간": "나"
        }
        self.zodiac_dates = [
            (1, 20, "Aquarius", "물병", "혁신"), (2, 19, "Pisces", "물고기", "예술"),
            (3, 21, "Aries", "양자리", "개척"), (4, 20, "Taurus", "황소", "안정"),
            (5, 21, "Gemini", "쌍둥이", "소통"), (6, 22, "Cancer", "게자리", "보호"),
            (7, 23, "Leo", "사자", "제왕"), (8, 23, "Virgo", "처녀", "분석"),
            (9, 24, "Libra", "천칭", "조정"), (10, 23, "Scorpio", "전갈", "승부"),
            (11, 23, "Sagittarius", "사수", "모험"), (12, 25, "Capricorn", "염소", "야망")
        ]

# ==========================================
# 2. 통합 엔진 (로직 복구 및 최적화)
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

    def get_daewoon(self, y_s, m_s, m_b, gender):
        is_yang = y_s % 2 == 0
        is_man = (gender == '남자')
        is_fwd = (is_yang and is_man) or (not is_yang and not is_man)
        curr_s, curr_b, lst = m_s, m_b, []
        for i in range(1, 9): # 미니 화면을 위해 8개까지만
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
        z_eng, z_kor, z_desc = "Capricorn", "염소", "야망"
        md = m * 100 + d
        for cm, cd, eng, kor, desc in dates:
            start_md = cm * 100 + cd
            nm, nd = dates[(dates.index((cm, cd, eng, kor, desc)) + 1) % 12][:2]
            if eng == "Capricorn":
                if md >= 1225 or md <= 119: z_eng, z_kor, z_desc = eng, kor, desc; break
            elif start_md <= md < (nm * 100 + nd):
                z_eng, z_kor, z_desc = eng, kor, desc; break
        return z_eng, z_kor, z_desc

    def generate_chart_image(self, target_eng, m, d):
        day_of_year = datetime.date(2000, m, d).timetuple().tm_yday
        sun_lon = (day_of_year - 80) * 0.986 
        fig = plt.figure(figsize=(3, 3)) # 사이즈 축소
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ax.set_ylim(0, 10)
        ax.set_yticks([]); ax.set_xticks([])
        plt.axis('off')
        labels = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        target_idx = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].index(target_eng)
        for i, label in enumerate(labels):
            color = '#673ab7' if i == target_idx else '#88888822'
            ax.bar(np.deg2rad(i*30 + 15), 10, width=np.deg2rad(30), bottom=0, color=color, alpha=0.5, edgecolor='gray')
            ax.text(np.deg2rad(i*30 + 15), 8.5, label, ha='center', va='center', fontsize=8, color='gray', fontweight='bold')
        ax.text(np.deg2rad(sun_lon), 6, "☉", color='orange', fontsize=18, ha='center', va='center', fontweight='bold')
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode()

    def generate_full_report(self, name, gender, y, m, d, h, is_lunar, solar_date_str):
        ganji = self.get_ganji(y, m, d, h)
        pillars = ["time", "day", "month", "year"]
        saju_data = []
        me_oh = self.gan_oh[ganji["day"][0]]
        for p in pillars:
            s_idx, b_idx = ganji[p]
            s_oh, b_oh = self.gan_oh[s_idx], self.ji_oh[b_idx]
            s_ship = self.get_shipsin(me_oh, s_oh)
            if p=="day": s_ship="<b>일간</b>"
            saju_data.append({
                "g_c": self.gan_hanja[s_idx], "j_c": self.ji_hanja[b_idx],
                "g_bg": self.oh_map[s_oh]['color'], "j_bg": self.oh_map[b_oh]['color'],
                "g_tc": self.oh_map[s_oh]['text'], "j_tc": self.oh_map[b_oh]['text'],
                "s_s": s_ship
            })
        daewoon = self.get_daewoon(ganji["year"][0], ganji["month"][0], ganji["month"][1], gender)
        z_eng, z_kor, z_desc = self.get_zodiac_info(m, d)
        chart_img = self.generate_chart_image(z_eng, m, d)
        
        # 메시지 생성
        s_d_score = random.randint(70, 99)
        s_d_msg = random.choice(["귀인의 도움이 있습니다.", "재물운이 상승합니다.", "뜻밖의 행운이 옵니다."])
        s_m_msg = random.choice(["변화가 길합니다.", "안정을 취하세요.", "새로운 인연이 옵니다."])
        z_d_score = random.randint(60, 100)
        z_d_msg = random.choice(["직관력이 좋아집니다.", "행운을 찾으세요.", "메모하세요."])
        z_m_msg = f"별들이 당신을 비춥니다."

        # HTML 구성 (주의: 들여쓰기 제거)
        saju_rows = "".join([f"<div style='text-align:center;'><div class='char' style='background:{d['g_bg']}; color:{d['g_tc']}'>{d['g_c']}</div><div class='char' style='background:{d['j_bg']}; color:{d['j_tc']}'>{d['j_c']}</div><div style='font-size:10px; margin-top:2px;'>{d['s_s']}</div></div>" for d in saju_data])
        dw_rows = "".join([f"<div class='dw-item' style='background:{d['bg']}; color:{d['tc']}'>{d['age']}<br>{d['gan']}{d['ji']}</div>" for d in daewoon])

        saju_html = f"""<div class="mini-card"><div class="mini-hd" style="background:#333;">🔮 사주 ({solar_date_str})</div><div class="s-grid">{saju_rows}</div><div class="dw-scroll">{dw_rows}</div><div class="fortune-row"><div class="fortune-box" style="border-left:3px solid #009688;"><div class="f-title" style="color:#009688">MONTHLY</div>{s_m_msg}</div><div class="fortune-box" style="border-left:3px solid #ff9800;"><div class="f-title" style="color:#ff9800">DAILY ({s_d_score}점)</div>{s_d_msg}</div></div></div>"""

        zodiac_html = f"""<div class="mini-card"><div class="mini-hd" style="background:#673ab7;">✨ {z_kor} ({z_eng})</div><div style="text-align:center; padding:5px;"><img src="data:image/png;base64,{chart_img}" style="width:160px;"></div><div class="fortune-row"><div class="fortune-box" style="border-left:3px solid #9c27b0;"><div class="f-title" style="color:#9c27b0">MONTHLY</div>{z_m_msg}</div><div class="fortune-box" style="border-left:3px solid #e91e63;"><div class="f-title" style="color:#e91e63">DAILY ({z_d_score}점)</div>{z_d_msg}</div></div></div>"""

        return saju_html + zodiac_html

# ==========================================
# 3. Streamlit 앱 실행부
# ==========================================
def main():
    st.set_page_config(page_title="AI 운세", page_icon="🔮", layout="centered", initial_sidebar_state="collapsed")
    
    # 🌟 [개선] 아이폰 미니 화면 축소 & 하단바 완전 제거 CSS
    st.markdown("""
        <style>
            /* 1. 화면 전체 축소 (Zoom Out) */
            .main .block-container {
                max-width: 100% !important;
                padding: 1rem 0.5rem !important;
                transform: scale(0.88); /* 88%로 축소 */
                transform-origin: top center;
                width: 113% !important; /* 축소된 만큼 너비 보정 */
                margin-bottom: -50px !important;
            }

            /* 2. 하단 툴바 및 Manage App 버튼 박멸 */
            footer, header, [data-testid="stToolbar"], .stAppDeployButton, [data-testid="stHeader"], [data-testid="stStatusWidget"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }

            /* 3. 카드 스타일 (미니) */
            .mini-card { background:rgba(128,128,128,0.05); border-radius:12px; margin-bottom:12px; overflow:hidden; border:1px solid rgba(128,128,128,0.2); }
            .mini-hd { padding:6px; font-size:13px; text-align:center; color:white; font-weight:bold; }
            .s-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:4px; padding:10px; }
            .char { width:100%; height:38px; line-height:38px; font-size:18px; font-weight:bold; border-radius:6px; margin-bottom:2px; color:white; text-shadow:0 1px 2px rgba(0,0,0,0.3); }
            .dw-scroll { display:flex; overflow-x:auto; padding:0 10px 10px 10px; gap:6px; -webkit-overflow-scrolling:touch; }
            .dw-item { min-width:36px; font-size:10px; text-align:center; border-radius:5px; padding:4px 0; color:white; font-weight:bold; flex-shrink:0; }
            .fortune-row { display:flex; gap:8px; padding:0 10px 10px 10px; }
            .fortune-box { flex:1; background:rgba(255,255,255,0.05); padding:8px; border-radius:6px; font-size:11px; line-height:1.3; }
            .f-title { font-weight:900; font-size:9px; margin-bottom:3px; letter-spacing:0.5px; }

            /* 4. 플로팅 버튼 */
            [data-testid="stSidebarCollapsedControl"] {
                position: fixed !important; bottom: 30px !important; right: 20px !important;
                width: 50px !important; height: 50px !important;
                background: #ff4444 !important; border-radius: 50% !important;
                z-index: 2147483647 !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
                border: 2px solid white !important;
                display: flex !important; justify-content: center !important; align-items: center !important;
            }
            [data-testid="stSidebarCollapsedControl"]::after {
                content: "입력"; color: white; font-size: 11px; font-weight: bold;
            }
            [data-testid="stSidebarCollapsedControl"] svg { display: none !important; }
            
            /* 기본 텍스트 크기 조정 */
            html, body { font-size: 14px; color: inherit; }
        </style>
        
        <script>
            // 하단 툴바 및 배포 버튼 강제 제거 (지속적 감시)
            setInterval(() => {
                const selectors = ['[data-testid="stToolbar"]', '.stAppDeployButton', 'footer', '[data-testid="stHeader"]', '[data-testid="stStatusWidget"]'];
                selectors.forEach(s => {
                    const el = document.querySelector(s);
                    if(el) { el.remove(); el.style.display='none'; }
                });
            }, 300);
        </script>
    """, unsafe_allow_html=True)
    
    st.title("📱 AI 운세 마스터")
    
    with st.sidebar:
        st.header("입력창")
        name = st.text_input("이름")
        gender = st.radio("성별", ["남자", "여자"], horizontal=True)
        cal_type = st.radio("달력", ["양력", "음력"], horizontal=True)
        birth_txt = st.text_input("생년월일 (예:19900101)", max_chars=8)
        b_time = st.time_input("시간", value=datetime.time(12, 0))
        btn_run = st.button("운세 보기", type="primary", use_container_width=True)

    if btn_run and len(birth_txt) == 8:
        engine = UniversalEngine()
        y, m, d = int(birth_txt[:4]), int(birth_txt[4:6]), int(birth_txt[6:8])
        solar_str = f"{y}-{m}-{d}"
        if cal_type == "음력":
            cal = KoreanLunarCalendar()
            cal.setLunarDate(y, m, d, False)
            y, m, d = cal.solarYear, cal.solarMonth, cal.solarDay
            solar_str = f"{y}-{m}-{d} (음력)"
        
        with st.spinner("분석 중..."):
            html_content = engine.generate_full_report(name, gender, y, m, d, b_time.hour, (cal_type=="음력"), solar_str)
            st.markdown(html_content, unsafe_allow_html=True)
            
            st.markdown("---")
            ad_html = """
            <div style="background:rgba(128,128,128,0.08); border-radius:8px; padding:12px; text-align:center; border:1px dashed rgba(128,128,128,0.5);">
                <div style="font-size:10px; opacity:0.7; margin-bottom:4px;">ADVERTISEMENT</div>
                <div style="font-size:12px; font-weight:bold; color:#1a73e8;">🍀 오늘의 행운을 잡으세요 🍀</div>
            </div>
            """
            components.html(ad_html, height=80)

if __name__ == "__main__":
    main()