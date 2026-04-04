import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
import io
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS誓約書作成", page_icon="🏍️")

# 日本語フォント（平成角ゴシック）の登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

st.title("二輪車安全運転練習会 申込フォーム")

# 入力フォーム
with st.form("entry_form"):
    st.info("資料に基づき、誓約書の文言を正確に反映したPDFを作成します。")
    
    # 開催日の選択（プルダウン方式）
    st.write("【開催日】")
    col_y, col_m, col_d = st.columns(3)
    with col_y:
        selected_year = st.selectbox("年", list(range(2026, 2051)), index=0)
    with col_m:
        selected_month = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
    with col_d:
        selected_day = st.selectbox("日", list(range(1, 32)), index=datetime.now().day - 1)
    
    event_date_str = f"令和{selected_year - 2018}年 {selected_month}月 {selected_day}日"
    
    # 個人情報入力
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("氏名")
        blood_type = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with col2:
        phone = st.text_input("電話番号")
        
    address = st.text_input("住所")
    emergency_contact = st.text_input("緊急連絡先")
    
    st.divider()
    st.subheader("未成年の場合のみ入力")
    parent_address = st.text_input("住所（親権者）")
    parent_name = st.text_input("氏名（親権者）")
    parent_phone = st.text_input("電話（親権者）")

    st.divider()
    st.warning("以下の誓約内容を必ずご確認ください。")
    # 資料の文言を一字一句表示
    st.write("""
    私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)
    の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失
    は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約
    します。
    ※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した
    場合、自己負担で賠償となります。(教習車・信号機等は数百万円の賠償となります)
    """)
    
    agree = st.checkbox("上記の内容を全て確認し、誓約いたします")

    submitted = st.form_submit_button("誓約書PDFを作成する")

# PDF生成処理
if submitted:
    if not agree:
        st.error("誓約事項への同意（チェック）が必要です。")
    elif not name:
        st.error("氏名の入力は必須です。")
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # 1. ヘッダー情報
        p.setFont("HeiseiKakuGo-W5", 16)
        p.drawString(70, 800, "件名:二輪車安全運転練習会")
        p.setFont("HeiseiKakuGo-W5", 12)
        p.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
        p.drawString(70, 760, f"開催日:{event_date_str}")
        p.drawString(70, 740, "会場名:島根県運転免許センター")
        
        # 2. 誓約文言（一字一句再現）
        p.setFont("HeiseiKakuGo-W5", 14)
        p.drawCentredString(300, 700, "誓   約   書")
        
        p.setFont("HeiseiKakuGo-W5", 11)
        text_y = 670
        誓約文 = [
            "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)",
            "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失",
            "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約",
            "します。",
            "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した",
            "場合、自己負担で賠償となります。(教習車・信号機等は数百万円の賠償となります)"
        ]
        for line in 誓約文:
            p.drawString(70, text_y, line)
