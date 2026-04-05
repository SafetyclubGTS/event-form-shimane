import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
import base64
import json
from datetime import datetime, timedelta, timezone

# --- 設定 ---
# ご提示いただいた新しいGAS URLを反映
GAS_URL = "https://script.google.com/macros/s/AKfycbyvuFXNBjT8jj3jq7c8O2kUKykTWz0R_32gril1xRsaRFDivIjsy_qccpusQ5b7DJAKKA/exec"

st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

# 日本標準時 (JST) の設定
JST = timezone(timedelta(hours=+9))

def get_address(zipcode):
    """郵便番号から住所を自動取得"""
    if len(zipcode) == 7:
        try:
            url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            res = requests.get(url, timeout=5)
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                # 市区町村・町名までを自動入力用に返す
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 誓約文（原本通り・一字一句復元） ---
S1 = "私は、この練習会に参加するに当たり,主催者(インストラクターおよび指導者等)の指示を守ります。"
S2 = "また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし、"
S3 = "主催者に責任を追及したり、損害賠償を要求しないことを誓約します。"

W1 = "※原則として参加車両は任意保険への加入をお願いします。"
W2 = "教習所内の施設を破壊した場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"

P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の目的には使用いたしません。"

st.title("GTS二輪車安全運転練習会\n申込フォーム")
if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

st.subheader("【開催日】")
# 日本時刻での現在日時を取得して初期値に設定
n = datetime.now(JST)
c1, c2, c3 = st.columns(3)
with c1:
    # 2026年から2036年までを選択可能
    sy = st.selectbox("年", list(range(2026, 2037)), index=0)
with c2:
    sm = st.selectbox("月", list(range(1, 13)), index=(n.month - 1))
with c3:
    sd = st.selectbox("日", list(range(1, 32)), index=(n.day - 1))

# GASのフォルダ名用(YYYY-MM-DD)とPDF印字用(和暦)
ev_date_folder = f"{sy}-{sm:02d}-{sd:02d}"
ev_date_jp = f"令和{sy - 2018}年 {sm}月 {sd}日"

st.subheader("【基本情報】")
z_in = st.text_input("郵便番号（7桁）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力"):
    st.session_state.auto_addr = get_address(z_in)

with st.form("main_form"):
    # 住所入力欄を分割（市区町村・町名 / 番地・建物名）
    u_ad1 = st.text_input("住所1（市区町村・町名）", value=st.session_state.auto_addr, placeholder="島根県松江市打出町")
    u_ad2 = st.text_input("住所2（番地・建物名）", placeholder="◯番地 ◯◯マンション 101号")
    
    cl, cr = st.columns(2)
    with cl:
        u_na = st.text_input("氏名", placeholder="山田 太郎")
        u_bl = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with cr:
        u_ph = st.text_input("電話番号", placeholder="090-0000-0000")
        u_em = st.text_input("緊急連絡先", placeholder="080-1111-1111（母）")
    
    st.divider()
    st.subheader("【未成年の場合のみ入力】")
    pa = st.text_input("親権者 住所", placeholder="参加者と住所が異なる場合のみ入力")
    pn = st.text_input("親権者 氏名", placeholder="保護者の氏名を記入")
    pp = st.text_input("親権者 電話番号", placeholder="090-2222-2222")
    
    st.divider()
    st.error("【重要：誓約事項】")
    st.write(S1); st.write(S2); st.write(S3)
    st.write(f":red[{W1}]"); st.write(f":red[{W2}]"); st.write(f":red[{W3}]")
    st.info(P1)
    
    agree = st.checkbox("誓約事項および個人情報の取り扱いに同意し、申し込みます")
    submit = st.form_submit_button("送信（PDF作成・自動保存）")

if submit:
    if not agree or not u_na or not u_ad1:
        st.error("氏名、住所、同意チェックは必須です。")
    else:
        # 送信時の日本時刻を取得
        now = datetime.now(JST)
        ts = now.strftime("%Y-%m-%d %H:%M:%S")
        eid = now.strftime("%Y%m%d-%H%M%S")
        full_address = f"{u_ad1}{u_ad2}" # PDF出力用に結合
        
        buf = io.BytesIO()
        pdf = canvas.Canvas(buf, pagesize=A4)
        pdf.setFont("HeiseiKakuGo-W5", 14)
        pdf.drawString(70, 800, "件名: GTS二輪車安全運転練習会")
        pdf.drawString(70, 780, f"開催日: {ev_date_jp}")
        pdf.drawCentredString(300, 720, "誓   約   書")
        
        pdf.setFont("HeiseiKakuGo-W5", 11)
        pdf.drawString(70, 680, S1); pdf.drawString(70, 660, S2); pdf.drawString(70, 640, S3)
        
        pdf.setFillColor(colors.red)
        pdf.drawString(70, 610, W1); pdf.drawString(70, 590, W2); pdf.drawString(70, 570, W3)
        
        pdf.setFillColor(colors.black)
        pdf.drawString(70, 530, f"令和 {now.year-2018} 年 {now.month} 月 {now.day} 日")
        pdf.drawString(70, 480, f"住所: {full_address}")
        pdf.drawString(70, 460, f"氏名: {u_na} (血液型: {u_bl})")
        pdf.drawString(70, 440, f"電話: {u_ph} (緊急連絡先: {u_em})")
        
        pdf.drawString(70, 380, "【親権者署名】")
        pdf.drawString(70, 360, f"住所: {pa}")
        pdf.drawString(70, 340, f"氏名: {pn} (電話: {pp})")
        
        pdf.setFont("HeiseiKakuGo-W5", 8)
        pdf.drawString(70, 60, P1)
        # 完了日時（タイムスタンプ）のみを印字
        pdf.drawString(70, 40, f"完了日時: {ts}")
        
        pdf.showPage(); pdf.save()
        pb = buf.getvalue()
        
        try:
            b64 = base64.b64encode(pb).decode('utf-8')
            f_n = f"誓約書_{u_na}_{eid}.pdf"
            # GASに送るパラメータ（ファイル名、PDF、開催日、氏名）
            p_l = {
                "fileName": f_n, 
                "pdfData": b64, 
                "evDate": ev_date_folder, 
                "uName": u_na
            }
            requests.post(GAS_URL, data=json.dumps(p_l), headers={'Content-Type': 'application/json'}, timeout=30)
            st.success("申込完了！Googleドライブへ保存されました。")
        except:
            st.error("自動保存に失敗しました。以下のボタンからPDFをダウンロードして保管してください。")
        
        st.download_button(label="PDFを保存", data=pb, file_name=f"GTS_{u_na}_{eid}.pdf", mime="application/pdf")
