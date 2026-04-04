import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# --- 1. 基本設定 ---
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            u = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            res = requests.get(u)
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. 誓約書の文言（一字一句間違いなく定義） ---
S1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)"
S2 = "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失"
S3 = "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約"
S4 = "します。"

W1 = "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した"
W2 = "場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"

P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の"
P2 = "目的には使用いたしません。"

# --- 3. アプリ画面 ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

st.subheader("【開催日】")
n = datetime.now()
c1, c2, c3 = st.columns(3)
with c1:
    sy = st.selectbox("年", [2026, 2027], index=0)
with c2:
    sm = st.selectbox("月", list(range(1, 13)), index=(n.month - 1))
with c3:
    sd = st.selectbox("日", list(range(1, 32)), index=(n.day - 1))

ev_date = f"令和{sy - 2018}年 {sm}月 {sd}日"

st.subheader("【住所】")
z_in = st.text_input("郵便番号（7桁）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力"):
    st.session_state.auto_addr = get_address(z_in)

# --- 4. フォーム入力 ---
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
    st.write("未成年の場合のみ入力")
    pa = st.text_input("親権者 住所")
    pn = st.text_input("親権者 氏名")
    pp = st.text_input("親権者 電話")

    st.divider()
    st.error("【重要：誓約事項】")
    st.write(f"{S1}{S2}{S3}{S4}")
    st.write(f":red[{W1}{W2}]")
    st.write(f":red[{W3}]")
    
    agree = st.checkbox("誓約事項に同意して申し込む")
    submit = st.form_submit_button("申し込む")

# --- 5. PDF生成 ---
if submit:
    if not agree:
        st.error("同意チェックが必要です。")
    elif not u_na:
        st.error("氏名は必須です。")
    else:
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        
        # 文字列を事前に作成（カッコ内の複雑な処理を排除）
        title_txt = "件名: GTS二輪車安全運転練習会"
        host_txt = "主催者: GTS (グランドツアー山陰)"
        date_txt = f"開催日: {ev_date}"
        place_txt = "会場名: 島根県運転免許センター"
        
        pdf.setFont("HeiseiKakuGo-W5", 16)
        pdf.drawString(70, 800, title_txt)
        pdf.setFont("HeiseiKakuGo-W5", 12)
