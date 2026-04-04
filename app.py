import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
import io
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# 日本語フォント（平成角ゴシック）の登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

st.title("二輪車安全運転練習会 参加申込")
st.subheader("主催：GTS（グランドツアー山陰）")

# 入力フォーム
with st.form("entry_form"):
    st.info("島根県運転免許センターでの練習会用。入力内容はPDF作成後に消去されます。")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("氏名", placeholder="島根 太郎")
        blood_type = st.selectbox("血液型", ["", "A", "B", "O", "AB"], index=0)
    with col2:
        phone = st.text_input("電話番号", placeholder="090-0000-0000")
        
    address = st.text_input("住所", placeholder="島根県...")
    emergency_contact = st.text_input("緊急連絡先（氏名・続柄・電話）")

    st.warning("【誓約事項】\n私は、この練習会に参加するに当たり、主催者の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約します。\n\n※原則として参加車両は任意保険への加入をお願いします。教習所内の施設（教習車・信号機等）を破壊した場合、自己負担（数百万円単位）での賠償となります。")
    
    agree = st.checkbox("上記の誓約内容を理解し、同意します")

    submitted = st.form_submit_button("誓約書PDFを作成する")

# PDF生成処理
if submitted:
    if not agree:
        st.error("誓約事項への同意が必要です。")
    elif not name or not phone or not address:
        st.error("氏名・住所・電話番号は必須項目です。")
    else:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # 1. タイトルと主催者
        p.setFont("HeiseiKakuGo-W5", 18)
        p.drawCentredString(300, 800, "二輪車安全運転練習会 誓約書")
        p.setFont("HeiseiKakuGo-W5", 12)
        p.drawString(70, 770, "主催者: GTS (グランドツアー山陰)")
        p.drawString(70, 750, "会場名: 島根県運転免許センター")
        
        # 2. 誓約文面（OCR資料に基づき忠実に再現）
        p.setFont("HeiseiKakuGo-W5", 11)
        text_box = p.beginText(70, 710)
        lines = [
            "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。",
            "また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、",
            "損害賠償を要求しないことを誓約します。",
            "",
            "※原則として参加車両は任意保険への加入をお願いします。教習所内の施設を破壊した場合、",
            "  自己負担で賠償となります。(教習車・信号機等は数百万円の賠償となります)"
        ]
        for line in lines:
            text_box.textLine(line)
        p.drawText(text_box)
        
        # 3. 参加者情報
        p.setFont("HeiseiKakuGo-W5", 12)
        y = 580
        p.drawString(70, y, f"作成日: {datetime.now().strftime('%Y年 %m月 %d日')}")
        p.drawString(70, y-40, f"住所: {address}")
        p.drawString(70, y-70, f"氏名: {name}")
        p.drawString(350, y-70, f"血液型: {blood_type} 型")
        p.drawString(70, y-100, f"電話: {phone}")
        p.drawString(70, y-130, f"緊急連絡先: {emergency_contact}")
        
        # 署名欄の枠（「印」は削除しました）
        p.rect(65, y-80, 300, 25) 
        p.setFont("HeiseiKakuGo-W5", 8)
        p.drawString(70, y-88, "参加者署名（デジタル入力済み）")
        
        p.showPage()
        p.save()
        
        st.success("誓約書PDFが作成されました。")
        st.download_button(
            label="PDFをダウンロードして保存",
            data=buffer.getvalue(),
            file_name=f"GTS誓約書_{name}.pdf",
            mime="application/pdf"
        )
