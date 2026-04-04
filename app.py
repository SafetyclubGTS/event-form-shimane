import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io, requests, base64, json
from datetime import datetime

# --- 設定 ---
GAS_URL = "https://script.google.com/macros/s/AKfycbxB94Sxkdwg44Apb36p-Ibrne9e5nYDtpgiSImuXjYrl5Tp1L14mVQKYVsjVCn5zUGD/exec"
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            res = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}", timeout=5)
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except: return ""
    return ""

# --- 誓約文（原本通り） ---
S1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。"
S2 = "また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし、"
S3 = "主催者に責任を追及したり、損害賠償を要求しないことを誓約します。"
W1 = "※原則として参加車両は任意保険への加入をお願いします。"
W2 = "教習所内の施設を破壊した場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"
P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の目的には使用いたしません。"

st.title("GTS二輪車安全運転練習会\n申込フォーム")
if "auto_addr" not in st.session_state: st.session_state.auto_addr = ""

st.subheader("【開催日】")
n = datetime.now()
c1, c2, c3 = st.columns(3)
with c1: sy = st.selectbox("年", [2026, 2027], index=0)
with c2: sm = st.selectbox("月", list(range(1, 13)), index=(n.month - 1))
with c3: sd = st.selectbox("日", list(range(1, 32)), index=(n.day - 1))
ev_date = f"令和{sy - 2018}年 {sm}月 {sd}日"

st.subheader("【基本情報】")
z_in = st.text_input("郵便番号（7桁）", max_chars=7)
if st.button("住所を自動入力"): st.session_state.auto_addr = get_address(z_in)

with st.form("main_form"):
    u_ad = st.text_input("住所", value=st.session_state.auto_addr)
    cl, cr = st.columns(2)
    with cl:
        u_na = st.text_input("氏名")
        u_bl = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with cr:
        u_ph = st.text_input("電話番号")
        u_em = st.text_input("緊急連絡先")
    
    st.divider()
    st.subheader("【未成年の場合】")
    pa, pn, pp = st.text_input("親権者 住所"), st.text_input("親権者 氏名"), st.text_input("親権者 電話番号")
    
    st.divider()
    st.error("【誓約事項】")
    st.write(f"{S1}\n{S2}\n{S3}")
    st.write(f":red[{W1}]\n:red[{W2}]\n:red[{W3}]")
    st.info(P1)
    
    agree = st.checkbox("同意して申し込む")
    submit = st.form_submit_button("送信（PDF作成・保存）")

if submit:
    if not agree or not u_na:
        st.error("入力不備があります。")
    else:
        now = datetime.now()
        t_str, e_id = now.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y%m%d-%H%M%S")
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
        pdf.drawString(70, 780, f"開催日: {ev_date}")
        pdf.drawCentredString(300, 720, "誓   約   書")
        pdf.setFont("HeiseiKakuGo-W5", 11)
        pdf.drawString(70, 680, S1)
        pdf.drawString(70, 660, S2)
        pdf.drawString(70, 640, S3)
        pdf.setFillColor(colors.red)
        pdf.drawString(70, 610, W1)
        pdf.drawString(70, 590, W2)
        pdf.drawString(70, 570, W3)
        pdf.setFillColor(colors.black)
        pdf.drawString(70, 530, f"令和 {now.year-2018} 年 {now.month} 月 {now.day} 日")
        pdf.drawString(70, 480, f"住所: {u_ad}")
        pdf.drawString(70, 460, f"氏名: {u_na}  (血液型: {u_bl})")
        pdf.drawString(70, 440, f"電話: {u_ph}  (緊急連絡先: {u_em})")
        pdf.drawString(70, 380, "【親権者署名】")
        pdf.drawString(70, 360, f"住所: {pa}")
        pdf.drawString(70, 340, f"氏名: {pn}  (電話: {pp})")
        pdf.setFont("HeiseiKakuGo-W5", 8)
        pdf.drawString(70, 60, P1)
        # タイムスタンプ
        pdf.drawString(70, 40, f"【システム記録】 ID: {e_id} / 日時: {t_str} / 同意済み")
        pdf.showPage()
        pdf.save()
        p_bytes = buf.getvalue()
        
        try:
            p_b64 = base64.b64encode(p_bytes).decode('utf-8')
            res = requests.post(GAS_URL, data=json.dumps({"fileName": f"誓約書_{u_na}_{e_id}.pdf", "
