import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS誓約書作成", page_icon="🏍️")

# 日本語フォント（平成角ゴシック）の登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

# 郵便番号から住所を取得する関数
def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            res = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}")
            data = res.json()
            if data["results"]:
                result = data["results"][0]
                return f"{result['address1']}{result['address2']}{result['address3']}"
        except:
            return ""
    return ""

st.title("二輪車安全運転練習会 申込フォーム")

# セッション状態（入力保持）の初期化
if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 1. 開催日の選択
st.subheader("【開催日】")
col_y, col_m, col_d = st.columns(3)
with col_y:
    selected_year = st.selectbox("年", list(range(2026, 2051)), index=0)
with col_m:
    selected_month = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
with col_d:
    selected_day = st.selectbox("日", list(range(1, 32)), index=datetime.now().day - 1)

event_date_str = f"令和{selected_year - 2018}年 {selected_month}月 {selected_day}日"

# 2. 住所検索
st.subheader("【住所検索】")
zip_input = st.text_input("郵便番号（7桁・ハイフンなし）を入力してEnter", max_chars=7)
if st.button("住所を検索する"):
    st.session_state.auto_addr = get_address(zip_input)
    if not st.session_state.auto_addr:
        st.error("住所が見つかりませんでした。")

# 3. メインフォーム
with st.form("entry_form"):
    address = st.text_input("住所（番地まで入力してください）", value=st.session_state.auto_addr)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("氏名")
        blood_type = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with col2:
        phone = st.text_input("電話番号")
        
    emergency_contact = st.text_input("緊急連絡先")
    
    st.divider()
    st.subheader("未成年の場合のみ入力")
    parent_address = st.text_input("親権者 住所")
    parent_name = st.text_input("親権者 氏名")
    parent_phone = st.text_input("親権者 電話")

    st.divider()
    st.error("【重要：誓約事項】※必ずご確認ください")
    st.write("私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約します。")
    st.markdown("**:red[※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した場合、自己負担で賠償となります。(教習車・信号機等は数百万円の賠償となります)]**")
    
    agree = st.checkbox("上記の内容を全て確認し、誓約いたします")
    submitted = st.form_submit_button("誓約書PDFを作成する")

# PDF生成処理
if submitted:
    if not agree:
        st.error("誓約事項への同意が必要です。")
    elif not name:
        st.error("氏名は必須です。")
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # ヘッダー
        p.setFont("HeiseiKakuGo-W5", 16)
        p.drawString(70, 800, "件名:二輪車安全運転練習会")
        p.setFont("HeiseiKakuGo-W5", 12)
        p.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
        p.drawString(70, 760, f"開催日:{event_date_str}")
        p.drawString(70, 740, "会場名:島根県運転免許センター")
        
        p.setFont("HeiseiKakuGo-W5", 14)
        p.drawCentredString(300, 700, "誓   約   書")
        
        # 誓約文面（前半：黒文字）
        p.setFont("HeiseiKakuGo-W5", 11)
        text_y = 670
        lines = [
            "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)",
            "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失",
            "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約",
            "します。"
        ]
        for line in lines:
            p.drawString(70, text_y, line)
            text_y -= 20
        
        # 誓約文面（後半：赤文字・改行・強調）
        p.setFillColor(colors.red) # ここから赤字
        text_y -= 10 # 少し隙間を空ける
        warning_lines = [
            "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した",
            "場合、自己負担で賠償となります。",
            "(教習車・信号機等は数百万円の賠償となります)"
        ]
        for line in warning_lines:
            p.drawString(70, text_y, line)
            text_y -= 20
        
        p.setFillColor(colors.black) # 黒字に戻す
        
        # 日付と署名欄
        today = datetime.now()
        p.drawString(70, text_y - 20, f"令和  {today.year-2018} 年  {today.month} 月  {today.day} 日")
        
        p.setFont("HeiseiKakuGo-W5", 12)
        y_info = text_y - 60
        p.drawString(70, y_info, "参加者署名")
        p.drawString(90, y_info - 30, f"住所: {address}")
        p.drawString(90, y_info - 60, f"氏名: {name}")
        p.drawString(350, y_info - 60, f"血液型: {blood_type}")
        p.drawString(90, y_info - 90, f"電話: {phone}")
        p.drawString(90, y_info - 120, f"緊急連絡先: {emergency_contact}")
        
        y_parent = y_info - 170
        p.drawString(70, y_parent, "親権者署名(未成年参加者は必須)")
        p.drawString(90, y_parent - 30, f"住所: {parent_address}")
        p.drawString(90, y_parent - 60, f"氏名: {parent_name}")
        p.drawString(90, y_parent - 90, f"電話: {parent_phone}")
        
        p.showPage()
        p.save()
        
        st.success("PDFが作成されました。")
        st.download_button(label="誓約書をダウンロード", data=buffer.getvalue(), file_name=f"GTS誓約書_{name}.pdf", mime="application/pdf")
