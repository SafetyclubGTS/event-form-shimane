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
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. 誓約書の文言（一字一句再現） ---
S1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)"
S2 = "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失"
S3 = "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約"
S4 = "します。"

W1 = "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した"
W2 = "場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"

P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の"
P2 = "目的には使用いたしません。"

# --- 3. アプリ画面 ---
# タイトルを大きく表示
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 開催日（サブヘッダーの大きさに合わせる）
st.subheader("【開催日】")
n = datetime.now()
c1, c2, c3 = st.columns(3)
with c1:
    sy = st.selectbox("年", [2026, 2027], index=0)
with c2:
    sm = st.selectbox("月", list(range(1, 13)), index=(n.month - 1))
with c3:
    sd = st.selectbox("日", list(range(1, 32)), index=(n.day - 1))

ev_date = f"令和{sy - 2018}年 {sm}月 {sd}日"

# 住所検索
st.subheader("【住所・氏名・電話番号・血液型・緊急時の連絡先】")
z_in = st.text_input("郵便番号（7桁・ハイフンなし）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力する"):
    st.session_state.auto_addr = get_address(z_in)

# --- 4. メインフォーム（文字サイズと入力例を調整） ---
with st.form("main_form"):
    # 全ての項目に詳細な placeholder（薄い入力例）を追加
    u_ad = st.text_input(
        "住所（番地まで正確に入力してください）", 
        value=st.session_state.auto_addr, 
        placeholder="島根県松江市打出町◯番地"
    )
    
    cl, cr = st.columns(2)
    with cl:
        u_na = st.text_input("氏名", placeholder="山田 太郎")
        u_bl = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with cr:
        u_ph = st.text_input("電話番号", placeholder="090-0000-0000")
        u_em = st.text_input("緊急連絡先（氏名・続柄など）", placeholder="080-1111-1111（母）")

    st.divider()
    st.subheader("【未成年の場合のみ入力】")
    pa = st.text_input("親権者 住所", placeholder="参加者と住所が異なる場合のみ入力")
    pn = st.text_input("親権者 氏名", placeholder="保護者の氏名を記入")
    pp = st.text_input("親権者 電話番号", placeholder="090-2222-2222")

    st.divider()
    st.error("【重要：誓約事項】")
    st.write(f"{S1}{S2}{S3}{S4}")
    st.write(f":red[{W1}{W2}]")
    st.write(f":red[{W3}]")
    
    st.info(f"{P1}{P2}")
    
    agree = st.checkbox("誓約事項および個人情報の取り扱いに同意し、申し込みます")
    
    # 送信ボタン
    submit = st.form_submit_button("上記の内容で申し込む（PDF作成）")

# --- 5. PDF生成処理 ---
if submit:
    if not agree:
        st.error("同意チェックが必要です。")
    elif not u_na:
        st.error("氏名は必須です。")
    else:
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        
        # ヘッダー情報の準備
        title_t = "件名: GTS二輪車安全運転練習会"
        host_t = "主催者: GTS (グランドツアー山陰)"
        date_t = f"開催日: {ev_date}"
        place_t = "会場名: 島根県運転免許センター"
        
        pdf.setFont("HeiseiKakuGo-W5", 16)
        pdf.drawString(70, 800, title_t)
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 780, host_t)
        pdf.drawString(70, 760, date_t)
        pdf.drawString(70, 740, place_t)
        
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawCentredString(300, 700, "誓   約   書")
        
        # 誓約文の描画
        pdf.setFont("HeiseiKakuGo-W5", 11)
        pdf.drawString(70, 670, S1)
        pdf.drawString(70, 650, S2)
        pdf.drawString(70, 630, S3)
        pdf.drawString(70, 610, S4)
        
        # 赤字警告の描画
        pdf.setFillColor(colors.red)
        pdf.drawString(70, 580, W1)
        pdf.drawString(70, 560, W2)
        pdf.drawString(70, 540, W3)
        
        # 署名欄
        pdf.setFillColor(colors.black)
        t = datetime.now()
        y_r = t.year - 2018
        now_t = f"令和 {y_r} 年 {t.month} 月 {t.day} 日"
        pdf.drawString(70, 500, now_t)
        
        pdf.setFont("HeiseiKakuGo-W5", 12)
        pdf.drawString(70, 460, "参加者署名")
        
        # 変数化して描画（カッコのエラーを防止）
        d_ad = f"住所: {u_ad}"
        d_na = f"氏名: {u_na}"
        d_bl = f"血液型: {u_bl}"
        d_ph = f"電話: {u_ph}"
        d_em = f"緊急連絡先: {u_em}"
        
        pdf.drawString(90, 430, d_ad)
        pdf.drawString(90, 400, d_na)
        pdf.drawString(350, 400, d_bl)
        pdf.drawString(90, 370, d_ph)
        pdf.drawString(90, 340, d_em)
        
        # 親権者欄
        pdf.drawString(70, 290, "親権者署名(未成年参加者は必須)")
        d_pad = f"住所: {pa}"
        d_pna = f"氏名: {pn}"
        d_pph = f"電話: {pp}"
        pdf.drawString(90, 260, d_pad)
        pdf.drawString(90, 230, d_pna)
        pdf.drawString(90, 200, d_pph)
        
        # フッター個人情報
        pdf.setFont("HeiseiKakuGo-W5", 9)
        pdf.drawString(70, 50, f"{P1}{P2}")
        
        pdf.showPage()
        pdf.save()
        
        st.success("申込手続きが完了しました。")
        st.download_button(
            label="誓約書PDFを保存する", 
            data=buf.getvalue(), 
            file_name=f"GTS誓約書_{u_na}.pdf", 
            mime="application/pdf"
        )
