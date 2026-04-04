import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# --- 1. フォント・基本設定 ---
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            res = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}")
            data = res.json()
            if data["results"]:
                r = data["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. PDF作成関数 (エラー防止のため独立) ---
def create_pdf(event_date, addr, u_name, u_blood, u_phone, u_emergency, p_addr, p_name, p_phone):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    pdf.setFont("HeiseiKakuGo-W5", 16)
    pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
    pdf.setFont("HeiseiKakuGo-W5", 12)
    pdf.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
    pdf.drawString(70, 760, f"開催日: {event_date}")
    pdf.drawString(70, 740, "会場名: 島根県運転免許センター")
    pdf.setFont("HeiseiKakuGo-W5", 14)
    pdf.drawCentredString(300, 700, "誓   約   書")
    pdf.setFont("HeiseiKakuGo-W5", 11)
    pdf.drawString(70, 670, "私は、この練習会に参加するに当たり、主催者の指示を守ります。")
    pdf.drawString(70, 650, "また受講中の事故等の損失は自己負担とし、主催者に賠償を要求しないことを誓約します。")
    pdf.setFillColor(colors.red)
    pdf.drawString(70, 610, "※原則として参加車両は任意保険への加入をお願いします。")
    pdf.drawString(70, 590, "※施設を破壊した場合、自己負担で賠償となります。")
    pdf.setFillColor(colors.black)
    today = datetime.now()
    dt_str = f"令和 {today.year-2018} 年 {today.month} 月 {today.day} 日"
    pdf.drawString(70, 550, dt_str)
    pdf.setFont("HeiseiKakuGo-W5", 12)
    pdf.drawString(70, 500, "参加者署名")
    pdf.drawString(90, 470, f"住所: {addr}")
    pdf.drawString(90, 440, f"氏名: {u_name}")
    pdf.drawString(350, 440, f"血液型: {u_blood}")
    pdf.drawString(90, 410, f"電話: {u_phone}")
    pdf.drawString(90, 380, f"緊急連絡先: {u_emergency}")
    pdf.drawString(70, 320, "親権者署名(未成年参加者は必須)")
    pdf.drawString(90, 290, f"住所: {p_addr}")
    pdf.drawString(90, 260, f"氏名: {p_name}")
    pdf.drawString(90, 230, f"電話: {p_phone}")
    pdf.setFont("HeiseiKakuGo-W5", 9)
    pdf.drawString(70, 50, "※取得した個人情報は、運営および緊急連絡以外には使用いたしません。")
    pdf.showPage()
    pdf.save()
    return buf.getvalue()

# --- 3. メイン画面 ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

st.subheader("【開催日】")
c1, c2, c3 = st.columns(3)
with c1:
    sy = st.selectbox("年", [2026, 2027], index=0)
with c2:
    sm = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
with c3:
    sd = st.selectbox("日", list(range(1, 32)), index=datetime.now().day -
