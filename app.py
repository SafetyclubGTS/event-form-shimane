import streamlit as st
from fpdf import FPDF
from datetime import datetime

# 画面のタイトル
st.title("イベント参加申込フォーム")
st.write("必要事項を入力して送信してください。入力内容はPDFで保存されます。")

# 入力フォームの作成
with st.form("application_form"):
    name = st.text_input("氏名")
    address = st.text_input("住所")
    tel = st.text_input("電話番号")
    emergency = st.text_input("緊急時の連絡先（氏名・続柄・電話番号）")
    
    st.markdown("---")
    st.subheader("参加規約")
    st.info("・イベント中の事故等は自己責任となります。\n・主催者は保険の範囲内で補償します。")
    agree = st.checkbox("規約に同意します")
    
    # 送信ボタン
    submit_button = st.form_submit_button("申し込む")

# ボタンが押された時の処理
if submit_button:
    if not agree:
        st.error("規約への同意が必要です。")
    elif not name or not address:
        st.warning("氏名と住所は必須項目です。")
    else:
        # PDFを生成する
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt="Event Application Form", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y/%m/%d %H:%M')}", ln=True)
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        pdf.cell(200, 10, txt=f"Address: {address}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {tel}", ln=True)
        pdf.cell(200, 10, txt=f"Emergency Contact: {emergency}", ln=True)
        pdf.cell(200, 10, txt="Agreement: Accepted", ln=True)

        # ブラウザで確認するためのダウンロードボタンを表示
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.success(f"ありがとうございます、{name}様。申し込みを受け付けました。")
        st.download_button(
            label="受領書(PDF)をダウンロード",
            data=pdf_bytes,
            file_name=f"entry_{name}.pdf",
            mime="application/pdf"
        )