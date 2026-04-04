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
            data = res.json()
            if data["results"]:
                r = data["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. 誓約事項の文言（一字一句一致） ---
# 誓約文全文
S_TEXT_1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)"
S_TEXT_2 = "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失"
S_TEXT_3 = "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約"
S_TEXT_4 = "します。"

# 警告事項（赤字）
W_TEXT_1 = "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した"
W_TEXT_2 = "場合、自己負担で賠償となります。"
W_TEXT_3 = "(教習車・信号機等は数百万円の賠償となります)"

# 個人情報（フッター）
P_TEXT_1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の"
P_TEXT_2 = "目的には使用いたしません。"

# --- 3. メイン画面 ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 開催日
st.subheader("【開催日】")
now_dt = datetime.now()
c1, c2, c3 = st.columns(3)
with c1:
    sel_y = st.selectbox("年", [2026, 2027], index=0)
with c2:
    idx_m = now_dt.month - 1
    sel_m = st.selectbox("月", list(range(1, 13)), index=idx_m)
with c3:
    idx_d = now_dt.day - 1
    sel_d = st.selectbox("日", list(range(1, 32)), index=idx_d)

event_date = f"令和{sel_y - 2018}年 {sel_m}月 {sel_d}日"

# 住所（見出しをシンプルに）
st.subheader("【住所】")
zip_in = st.text_input("郵便番号（7桁）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力する"):
    st.session_state.auto_addr = get_address(zip_in)

# --- 4. メインフォーム ---
with st.form("main_form"):
    addr = st.text_input(
        "住所（番地まで入力）", 
        value=st.session_state.auto_addr, 
        placeholder="島根県松江市打出町◯番地"
    )
    
    col_l, col_r = st.columns(2)
    with col_l:
        u_name = st.text_input("氏名", placeholder="山田 太郎")
        u_blood = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with col_r:
        u_phone = st.text_input("電話番号", placeholder="090-0000-0000")
        
    u_emergency = st.text_input("緊急連絡先（氏名・続柄など）", placeholder="080-1111-1111（母）")
    
    st.divider()
    st.subheader("未成年の場合のみ入力")
    p_addr = st.text_input("親権者 住所", placeholder="参加者と異なる場合のみ入力")
    p_name = st.text_input("親権者 氏名", placeholder="保護者氏名")
    p_phone = st.text_input("親権者 電話", placeholder="090-2222-2222")

    st.divider()
    st.error("【重要：誓約事項】")
    st.write(f"{S_TEXT_1}{S_TEXT_2}{S_TEXT_3}{S_TEXT_4}")
    st.write(f":red[{W_TEXT_1}{W_TEXT_2}]")
    st.write(f":red[{W_TEXT_3}]")
    st.info(f"{P_TEXT_1}{P_TEXT_2}")
    
    is_agree = st.checkbox("誓約事項および個人情報の取り扱いに同意し、申し込みます")
    is_submit = st.form_submit_button("申し込む")

# --- 5. PDF生成 ---
if is_submit:
    if not is_agree:
        st.error("同意チェックが必要です。")
    elif not u_name:
        st.error("氏名は必須です。")
    else:
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        
        # ヘッダー
        pdf.setFont("HeiseiKakuGo-W5", 16)
        pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
        pdf.drawString(70, 760, f"開催日: {event_date}")
        pdf.drawString(70, 740, "会場名: 島根県運転免許センター")
        
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawCentredString(300, 700, "誓   約   書")
        
        # 誓約文面（一字一句合わせる）
        pdf.setFont("HeiseiKakuGo-W5", 11)
        pdf.drawString(70, 670, S_TEXT_1)
        pdf.drawString(70, 650, S_TEXT_2)
        pdf.drawString(70, 630, S_TEXT_3)
        pdf.drawString(70, 610, S_TEXT_4)
        
        # 警告文（赤字）
        pdf.setFillColor(colors.red)
        pdf.drawString(70, 580, W_TEXT_1)
        pdf.drawString(70, 560, W_TEXT_2)
        pdf.drawString(70, 540, W_TEXT_3)
        
        # 記入日（黒字）
        pdf.setFillColor(colors.black)
        t_now = datetime.now()
        dt_txt = f"令和  {t_now.year - 2018} 年  {t_now.month} 月  {t_now.day} 日"
        pdf.drawString(70, 500, dt_txt)
        
        # 署名欄
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 460, "参加者署名")
        pdf.drawString(90, 430, f"住所: {addr}")
        pdf.drawString(90, 400
