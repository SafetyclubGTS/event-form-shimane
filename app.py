import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
import io
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS誓約書作成", page_icon="🏍️")

# 日本語フォントの登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

st.title("二輪車安全運転練習会 申込フォーム")

# 入力フォーム
with st.form("entry_form"):
    st.info("資料に基づき、誓約書の文言を正確に反映したPDFを作成します。")
    
    # 開催情報入力
    event_date = st.text_input("開催日（例：令和8年5月10日）", placeholder="令和  年  月  日")
    
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
    parent_name = st.text_input("親権者氏名")
    parent_address = st.text_input("親権者住所")
    parent_phone = st.text_input("親権者電話")

    st.divider()
    st.warning("以下の誓約内容を必ずご確認ください。")
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
        p.drawString(70, 760, f"開催日:{event_date if event_date else '令和    年   月   日'}")
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
            text_y -= 20
        
        # 3. 日付と署名欄
