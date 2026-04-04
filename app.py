import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import io

# ページ設定
st.set_page_config(page_title="GTS 申し込みフォーム", page_icon="🏍️")

st.title("Safetyclub GTS 参加申込書")
st.write("必要事項を入力して、申込書（PDF）を作成してください。")

# 入力項目
with st.form("entry_form"):
    name = st.text_input("氏名（漢字）")
    address = st.text_input("住所")
    emergency_contact = st.text_input("緊急連絡先（電話番号）")
    bike_model = st.text_input("車両名")
    
    submitted = st.form_submit_button("PDFを作成する")

if submitted:
    if not name or not emergency_contact:
        st.error("氏名と緊急連絡先は必須入力です。")
    else:
        # PDF生成の準備
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # 日本語フォントの設定（標準のHeiseiKakuGo-W5を使用）
        p.setFont("HeiseiKakuGo-W5", 16)
        
        # 内容の書き込み
        p.drawString(100, 800, "Safetyclub GTS 参加申込書")
        p.setFont("HeiseiKakuGo-W5", 12)
        p.drawString(100, 750, f"氏名: {name}")
        p.drawString(100, 730, f"住所: {address}")
        p.drawString(100, 710, f"緊急連絡先: {emergency_contact}")
        p.drawString(100, 690, f"車両名: {bike_model}")
        p.drawString(100, 650, "-------------------------------------------")
        p.drawString(100, 630, "※当日、受付にこのPDFを提示または提出してください。")
        
        p.showPage()
        p.save()
        
        # ダウンロードボタンの表示
        st.success("PDFが作成されました！下のボタンから保存してください。")
        st.download_button(
            label="申込書をダウンロード",
            data=buffer.getvalue(),
            file_name=f"GTS_entry_{name}.pdf",
            mime="application/pdf"
        )
