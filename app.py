import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# --- 1. 初期設定 ---
# フォント登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# 住所検索関数
def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            res = requests.get(url)
            data = res.json()
            if data["results"]:
                r = data["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. PDF生成関数 (計算を外に出して安全に) ---
def create_pdf(ev_date, addr, name, blood, phone, emg, pa, pn, pp):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    
    # ヘッダー設定
    pdf.setFont("HeiseiKakuGo-W5", 16)
    pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
    
    pdf.setFont("HeiseiKakuGo-W5", 12)
    pdf.drawString(70, 780, "主催者: GTS (グランドツアー山陰)")
    pdf.drawString(70, 760, f"開催日: {ev_date}")
    pdf.drawString(70, 740, "会場名: 島根県運転免許センター")
    
    pdf.setFont("HeiseiKakuGo-W5", 14)
    pdf.drawCentredString(300, 700, "誓   約   書")
    
    # 誓約内容
    pdf.setFont("HeiseiKakuGo-W5", 11)
    pdf.drawString(70, 670, "私は、この練習会に参加するに当たり、主催者の指示を守ります。")
    msg2 = "また受講中の事故等の損失は自己負担とし、主催者に賠償を要求しません。"
    pdf.drawString(70, 650, msg2)
    
    # 注意書き（赤字）
    pdf.setFillColor(colors.red)
    pdf.drawString(70, 610, "※原則として参加車両は任意保険への加入をお願いします。")
    pdf.drawString(70, 590, "※施設を破壊した場合、自己負担で賠償となります。")
    pdf.setFillColor(colors.black)
    
    # 記入日
    now = datetime.now()
    reiwa = now.year - 2018
    dt_str = f"令和 {reiwa} 年 {now.month} 月 {now.day} 日"
    pdf.drawString(70, 550, dt_str)
    
    # 署名欄
    pdf.setFont("HeiseiKakuGo-W5", 12)
    pdf.drawString(70, 500, "参加者署名")
    pdf.drawString(90, 470, f"住所: {addr}")
    pdf.drawString(90, 440, f"氏名: {name}")
    pdf.drawString(350, 440, f"血液型: {blood}")
    pdf.drawString(90, 410, f"電話: {phone}")
    pdf.drawString(90, 380, f"緊急連絡先: {emg}")
    
    # 親権者
    pdf.drawString(70, 320, "親権者署名(未成年参加者は必須)")
    pdf.drawString(90, 290, f"住所: {pa}")
    pdf.drawString(90, 260, f"氏名: {pn}")
    pdf.drawString(90, 230, f"電話: {pp}")
    
    # フッター
    pdf.setFont("HeiseiKakuGo-W5", 9)
    foot = "※取得した個人情報は、運営および緊急連絡以外には使用いたしません。"
    pdf.drawString(70, 50, foot)
    
    pdf.showPage()
    pdf.save()
    return buf.getvalue()

# --- 3. アプリ画面 ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 日付選択（計算を1行で完結させない工夫）
st.subheader("【開催日】")
now_dt = datetime.now()
today_m = now_dt.month
today_d = now_dt.day

c1, c2, c3 = st.columns(3)
with c1:
    sel_y = st.selectbox("年", [2026, 2027], index=0)
with c2:
    # indexを事前に変数化してエラー防止
    idx_m = today_m - 1
    sel_m = st.selectbox("月", list(range(1, 13)), index=idx_m)
with c3:
    # indexを事前に変数化してエラー防止
    idx_d = today_d - 1
    sel_d = st.selectbox("日", list(range(1, 32)), index=idx_d)

reiwa_y = sel_y - 2018
event_date_str = f"令和{reiwa_y}年 {sel_m}月 {sel_d}日"

# 住所入力
st.subheader("【住所】")
zip_code = st.text_input("郵便番号（7桁）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力"):
    st.session_state.auto_addr = get_address(zip_code)

# --- 4. 入力フォーム ---
with st.form("entry_form"):
    u_addr = st.text_input("住所", value=st.session_state.auto_addr, placeholder="島根県松江市...")
    
    cl, cr = st.columns(2)
    with cl:
        u_name = st.text_input("氏名", placeholder="山田 太郎")
        u_blood = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with cr:
        u_phone = st.text_input("電話番号", placeholder="090-0000-0000")
    
    u_emergency = st.text_input("緊急連絡先", placeholder="080-1111-1111（母）")
    
    st.divider()
    st.write("未成年の場合のみ入力")
    p_addr = st.text_input("親権者 住所")
    p_name = st.text_input("親権者 氏名")
    p_phone = st.text_input("親権者 電話")

    st.divider()
    st.error("【重要：誓約事項】")
    st.write("主催者の指示を遵守し、事故等の損失は自己負担とすることを誓約します。")
    st.write(":red[※任意保険への加入を推奨します。施設破壊は自己負担での賠償となります。]")
    
    is_agree = st.checkbox("同意して申し込む")
    
    # 送信ボタン
    submitted = st.form_submit_button("内容を確認してPDFを作成")

# --- 5. PDF出力 ---
if submitted:
    if not is_agree:
        st.error("同意チェックが必要です。")
    elif not u_name:
        st.error("氏名は必須です。")
    else:
        # PDFデータを取得
        pdf_out = create_pdf(
            event_date_str, u_addr, u_name, u_blood, 
            u_phone, u_emergency, p_addr, p_name, p_phone
        )
        st.success("申込手続きが完了しました！下のボタンから保存してください。")
        st.download_button(
            label="誓約書PDFを保存する",
            data=pdf_out,
            file_name=f"GTS誓約書_{u_name}.pdf",
            mime="application/pdf"
        )
