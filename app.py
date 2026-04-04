import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
import base64
import json
from datetime import datetime

# --- 【最新】デプロイ済みのGASウェブアプリURL ---
GAS_URL = "https://script.google.com/macros/s/AKfycbxB94Sxkdwg44Apb36p-Ibrne9e5nYDtpgiSImuXjYrl5Tp1L14mVQKYVsjVCn5zUGD/exec"

# --- 1. 基本設定 ---
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# PDF用日本語フォントの登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    """郵便番号から住所を自動取得する外部API連携"""
    if len(zipcode) == 7:
        try:
            u = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            res = requests.get(u, timeout=5)
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. 誓約書の文言（原本の完全復元） ---
S1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。"
S2 = "また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし、"
S3 = "主催者に責任を追及したり、損害賠償を要求しないことを誓約します。"

W1 = "※原則として参加車両は任意保険への加入をお願いします。"
W2 = "教習所内の施設を破壊した場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"

P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の"
P2 = "目的には使用いたしません。"

# --- 3. アプリ画面UI ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 開催日入力
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

# 基本情報入力
st.subheader("【住所・氏名・電話番号・血液型・緊急時の連絡先】")
z_in = st.text_input("郵便番号（7桁・ハイフンなし）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力する"):
    st.session_state.auto_addr = get_address(z_in)

with st.form("main_form"):
    u_ad = st.text_input(
        "住所（番地まで正確に入力してください）", 
        value=st.session_state.auto_addr, 
        placeholder="島根県松江市打出町◯番地"
    )
    
    cl, cr = st.columns(2)
    with cl:
        u_na = st.text_input("氏名", placeholder="山田 太郎")
        u_bl = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with cr:
        u_ph = st.text_input("電話番号", placeholder="090-0000-0000")
        u_em = st.text_input("緊急連絡先（氏名・続柄など）", placeholder="080-1111-1111（母）")

    st.divider()
    st.subheader("【未成年の場合のみ入力】")
    pa = st.text_input("親権者 住所", placeholder="参加者と住所が異なる場合のみ入力")
    pn = st.text_input("親権者 氏名", placeholder="保護者の氏名を記入")
    pp = st.text_input("親権者 電話番号", placeholder="090-2222-2222")

    st.divider()
    st.error("【重要：誓約事項】")
    st.write(S1)
    st.write(S2)
    st.write(S3)
    st.write(f":red[{W1}]")
    st.write(f":red[{W2}]")
    st.write(f":red[{W3}]")
    
    st.info(f"{P1}{P2}")
    
    agree = st.checkbox("誓約事項および個人情報の取り扱いに同意し、申し込みます")
    submit = st.form_submit_button("上記の内容で申し込む（PDF作成・自動保存）")

# --- 4. PDF生成 & Googleドライブ送信処理 ---
if submit:
    if not agree:
        st.error("同意チェックが必要です。")
    elif not u_na:
        st.error("氏名は必須です。")
    else:
        # タイムスタンプと申込IDの生成
        now = datetime.now()
        t_str = now.strftime("%Y-%m-%d %H:%M:%S")
        e_id = now.strftime("%Y%m%d-%H%M%S")

        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        
        # ヘッダー描画
        pdf.setFont("HeiseiKakuGo-W5", 16)
        pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
        pdf.drawString(70, 760, f"開催日: {ev_date}")
        pdf.drawString(70, 740, "会場名: 島根県運転免許センター")
        
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawCentredString(300, 700, "誓   約   書")
        
        # 誓約文の描画
        pdf.setFont("HeiseiKakuGo-W5", 11)
        pdf.drawString(70, 670, S1)
        pdf.drawString(70, 650, S2)
        pdf.drawString(70, 630, S3)
        
        # 注意書き（赤字）
        pdf.setFillColor(colors.red)
        pdf.drawString(70, 590, W1)
        pdf.drawString(70, 570, W2)
        pdf.drawString(70, 550, W3)
        
        # 署名欄と日付
        pdf.setFillColor(colors.black)
        y_r = now.year - 2018
        pdf.drawString(70, 500, f"令和 {y_r} 年 {now.month} 月 {now.day} 日")
        
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 460, "参加者署名")
        pdf.drawString(90, 430, f"住所: {u_ad}")
        pdf.drawString(90, 400, f"氏名: {u_na}")
        pdf.drawString(350, 400, f"血液型: {u_bl}")
        pdf.drawString(90, 370, f"電話: {u_ph}")
        pdf.drawString(90, 340, f"緊急連絡先: {u_em}")
        
        # 親権者欄
        pdf.drawString(70, 290, "親権者署名(未成年参加者は必須)")
        pdf.drawString(90, 260, f"住所: {pa}")
        pdf.drawString(90, 230, f"氏名: {pn}")
        pdf.drawString(90,
