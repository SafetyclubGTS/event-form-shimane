import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# --- 基本設定 ---
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

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

# タイトル
st.title("二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# --- 1. 開催日 ---
st.subheader("【開催日】")
c_y, c_m, c_d = st.columns(3)
with c_y:
    sel_y = st.selectbox("年", list(range(2026, 2051)), index=0)
with c_m:
    sel_m = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
with c_d:
    sel_d = st.selectbox("日", list(range(1, 32)), index=datetime.now().day - 1)

event_date = f"令和{sel_y - 2018}年 {sel_m}月 {sel_d}日"

# --- 2. 住所検索 ---
st.subheader("【住所検索】")
zip_in = st.text_input("郵便番号（7桁）", max_chars=7, placeholder="6900000")
if st.button("住所を検索する"):
    st.session_state.auto_addr = get_address(zip_in)
    if not st.session_state.auto_addr:
        st.error("住所が見つかりませんでした。")

# --- 3. メインフォーム（記入例を追加） ---
with st.form("main_form"):
    # placeholder= で薄い文字の記入例を表示
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
    
    st.write("""
    私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。
    また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、
    損害賠償を要求しないことを誓約します。
    """)
    
    st.markdown("**:red[※原則として参加車両は任意保険への加入をお願いします]**")
    st.markdown("**:red[※教習所内の施設を破壊した場合、自己負担で賠償となります]**")
    st.markdown("**:red[(教習車・信号機等は数百万円の賠償となります)]**")
    
    st.info("【個人情報の取り扱い】ご入力いただいた情報は、運営および緊急連絡以外の目的には使用しません。")
    
    is_agree = st.checkbox("誓約事項および個人情報の取り扱いに同意し、申し込みます")
    is_submit = st.form_submit_button("申し込む")

# --- 4. PDF生成 ---
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
        pdf.drawString(70, 800, "件名:二輪車安全運転練習会")
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
        pdf.drawString(70, 760, f"開催日: {event_date}")
        pdf.drawString(70, 740, "会場名: 島根県運転免許センター")
        
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawCentredString(300, 700, "誓   約   書")
        
        # 誓約文面
        pdf.setFont("HeiseiKakuGo-W5", 11)
        cy = 670
        pdf.drawString(70, cy, "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)")
        pdf.drawString(70, cy - 20, "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失")
        pdf.drawString(70, cy - 40, "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約")
        pdf.drawString(70, cy - 60, "します。")
        
        # 警告文（赤字）
        pdf.setFillColor(colors.red)
        w1 = "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した"
        w2 = "場合、自己負担で賠償となります。"
        w3 = "(教習車・信号機等は数百万円の賠償となります)"
        pdf.drawString(70, cy - 90, w1)
        pdf.drawString(70, cy - 110, w2)
        pdf.drawString(70, cy - 130, w3)
        
        pdf.setFillColor(colors.black)
        today = datetime.now()
        dt_txt = f"令和  {today.year-2018} 年  {today.month} 月  {today.day} 日"
        pdf.drawString(70, cy - 160, dt_txt)
        
        # 署名欄
        pdf.setFont("HeiseiKakuGo-W5", 12)
        iy = cy - 210
        pdf.drawString(70, iy, "参加者署名")
        pdf.drawString(90, iy - 30, f"住所: {addr}")
        pdf.drawString(90, iy - 60, f"氏名: {u_name}")
        pdf.drawString(350, iy - 60, f"血液型: {u_blood}")
        pdf.drawString(90, iy - 90, f"電話: {u_phone}")
        pdf.drawString(90, iy - 120, f"緊急連絡先: {u_emergency}")
        
        py = iy - 170
        pdf.drawString(70, py, "親権者署名(未成年参加者は必須)")
        pdf.drawString(90, py - 30, f"住所: {p_addr}")
        pdf.drawString(90, py - 60, f"氏名: {p_name}")
        pdf.drawString(90, py - 90, f"電話: {p_phone}")
        
        pdf.setFont("HeiseiKakuGo-W5", 9)
        pol = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の目的には使用いたしません。"
        pdf.drawString(70, 50, pol)
        
        pdf.showPage()
        pdf.save()
        
        st.success("申込手続きが完了しました。")
        st.download_button(
            label="誓約書PDFを保存する", 
            data=buf.getvalue(), 
            file_name=f"GTS誓約書_{u_name}.pdf", 
            mime="application/pdf"
        )
