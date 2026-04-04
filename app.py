import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
import io
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# 日本語フォントの登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

st.title("Safetyclub GTS 参加申込フォーム")
st.write("各項目を入力し、一番下のボタンで申込書PDFを作成してください。")

# 入力フォーム
with st.form("entry_form"):
    st.subheader("【お客様情報】")
    name = st.text_input("氏名（フルネーム）", placeholder="島根 太郎")
    address = st.text_input("住所", placeholder="島根県松江市...")
    phone = st.text_input("電話番号", placeholder="090-0000-0000")
    
    st.subheader("【緊急時のご連絡先】")
    emergency_contact = st.text_input("緊急連絡先（氏名・続柄・電話番号）", placeholder="島根 花子（妻） 080-xxxx-xxxx")

    st.subheader("【誓約事項】")
    st.write("・練習会中の事故や怪我について、主催者に責任を問わないことに同意します。")
    st.write("・会場のルールを守り、安全運転に努めます。")
    agree = st.checkbox("上記の誓約事項に同意します")

    submitted = st.form_submit_button("申込書PDFを作成する")

# PDF生成処理
if submitted:
    if not agree:
        st.error("誓約事項への同意（チェック）が必要です。")
    elif not name or not phone or not emergency_contact:
        st.error("必須項目（氏名・電話番号・緊急連絡先）を入力してください。")
    else:
        # PDFをメモリ上に作成
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # ヘッダー
        p.setFont("HeiseiKakuGo-W5", 18)
        p.drawCentredString(300, 800, "Safetyclub GTS 参加申込書")
        
        # 作成日
        p.setFont("HeiseiKakuGo-W5", 10)
        p.drawRightString(550, 780, f"作成日: {datetime.now().strftime('%Y/%m/%d')}")
        
        # 内容の描画
        p.setFont("HeiseiKakuGo-W5", 12)
        y_position = 730
        
        content = [
            f"氏名: {name}",
            f"住所: {address}",
            f"電話番号: {phone}",
            "",
            f"緊急連絡先: {emergency_contact}",
            "",
            "------------------------------------------------------------------",
            "【誓約】上記本人は、本練習会の趣旨を理解し、安全に配慮して",
            "走行することを誓約いたします。また、万が一の事故等についても",
            "自己の責任において解決することに同意済みです。",
            "------------------------------------------------------------------"
        ]
        
        for line in content:
            p.drawString(70, y_position, line)
            y_position -= 25
        
        p.showPage()
        p.save()
        
        # ダウンロードボタンの表示
        st.success("PDFの作成が完了しました！")
        st.download_button(
            label="申込書を保存（ダウンロード）",
            data=buffer.getvalue(),
            file_name=f"GTS申込書_{name}.pdf",
            mime="application/pdf"
        )
