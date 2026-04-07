import streamlit as st
import io, json, base64, re, requests
from datetime import datetime, timezone, timedelta

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# =========================
# 設定
# =========================
GAS_URL = "https://script.google.com/macros/s/AKfycbyvuFXNBjT8jj3jq7c8O2kUKykTWz0R_32gril1xRsaRFDivIjsy_qccpusQ5b7DJAKKA/exec"

pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
JST = timezone(timedelta(hours=9))

# =========================
# 誓約文（変更禁止）
# =========================
S1 = "私は、主催者の指示を守り、自己の判断と責任において安全運転に努めます。"
S2 = "現在、走行に支障のある疾患や負傷はなく、体調万全である事を確認の上で参加します。"
S3 = "事故（車両破損・負傷等）は全て自己負担とし、理由の如何を問わず主催者に責任を追及しません。"

W1 = "※任意保険未加入車両での参加は固くお断りいたします。"
W2 = "施設・機材（信号機・教習車等）を損壊した場合は、実費での全額賠償となります。"
W3 = "【重要】未成年の方は、必ず以下の「親権者署名」欄も入力してください。"

P1 = "※取得した個人情報は、運営および緊急連絡以外の目的には使用いたしません。"

# =========================
# ユーティリティ
# =========================
def is_valid_zip(z): return re.fullmatch(r"\d{7}", z)
def is_valid_phone(p): return re.fullmatch(r"[\d\-]{10,15}", p.replace(" ", ""))

def safe_filename(s):
    return re.sub(r'[\\/:*?"<>|]', "_", s)

def to_reiwa(dt):
    y = dt.year - 2018
    return f"令和{y if y>1 else '元'}年 {dt.month}月 {dt.day}日"

def get_address(zipcode):
    if not is_valid_zip(zipcode): return ""
    try:
        r = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}", timeout=5)
        d = r.json()
        if d.get("results"):
            a = d["results"][0]
            return f"{a['address1']}{a['address2']}{a['address3']}"
    except:
        pass
    return ""

# =========================
# PDF生成（署名欄なし）
# =========================
def create_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    jp = ParagraphStyle(name='JP', fontName='HeiseiKakuGo-W5', fontSize=11, leading=16)
    title = ParagraphStyle(name='Title', fontName='HeiseiKakuGo-W5', fontSize=16, alignment=1)
    red = ParagraphStyle(name='Red', fontName='HeiseiKakuGo-W5', fontSize=10, textColor=colors.red)

    story = []

    story.append(Paragraph("GTS二輪車安全運転練習会 誓約書", title))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"開催日：{data['date_jp']}", jp))
    story.append(Spacer(1, 10))

    story.append(Paragraph("【誓約事項】", jp))
    story.append(Paragraph(f"1. {S1}", jp))
    story.append(Paragraph(f"2. {S2}", jp))
    story.append(Paragraph(f"3. {S3}", jp))

    story.append(Spacer(1, 10))
    story.append(Paragraph(W1, red))
    story.append(Paragraph(W2, red))
    story.append(Paragraph(W3, red))

    story.append(Spacer(1, 20))

    table = Table([
        ["署名日", data["sign"]],
        ["住所", data["addr"]],
        ["氏名", f"{data['name']} (血液型:{data['blood']})"],
        ["連絡先", f"本人:{data['phone']} / 緊急:{data['emergency']}"],
    ], colWidths=[30*mm, 140*mm])

    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black)]))
    story.append(table)

    if data["p_name"]:
        story.append(Spacer(1, 15))
        story.append(Paragraph("【親権者署名】 ※未成年の場合必須", jp))
        p_table = Table([
            ["住所", data["p_addr"]],
            ["氏名", data["p_name"]],
        ], colWidths=[30*mm, 140*mm])
        p_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black)]))
        story.append(p_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph(P1, ParagraphStyle(name='Small', fontName='HeiseiKakuGo-W5', fontSize=8)))

    doc.build(story)
    return buf.getvalue()

# =========================
# UI
# =========================
st.set_page_config(page_title="GTS申込", page_icon="🏍️")
st.title("🏍️ GTS練習会 申込")

if "addr_input" not in st.session_state:
    st.session_state.addr_input = ""

c1, c2 = st.columns([2,1])
with c1:
    zipc = st.text_input("郵便番号", placeholder="6900000")
with c2:
    st.write("")
    if st.button("住所取得"):
        st.session_state.addr_input = get_address(zipc)

with st.form("form"):
    ev_date = st.date_input("開催日", value=datetime.now(JST))
    age = st.number_input("年齢", 0, 120)

    addr = st.text_input("住所", value=st.session_state.addr_input)
    u_name = st.text_input("氏名")
    blood = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    u_phone = st.text_input("電話番号")
    u_emer = st.text_input("緊急連絡先")

    st.info("未成年のみ入力")
    p_addr = st.text_input("親権者住所")
    p_name = st.text_input("親権者氏名")

    st.markdown(f"1. {S1}\n2. {S2}\n3. {S3}")
    st.warning(f"{W1}\n\n{W2}\n\n{W3}")

    agree = st.checkbox("同意する")
    submit = st.form_submit_button("送信")

# =========================
# 送信処理
# =========================
if submit:

    if not agree or not u_name or not addr or not u_phone:
        st.error("必須項目を入力してください")

    elif not is_valid_phone(u_phone):
        st.error("電話番号形式エラー")

    elif age < 18 and (not p_name or not p_addr):
        st.error("未成年は親権者情報が必要です")

    else:
        now = datetime.now(JST)

        data = {
            "date": ev_date.strftime("%Y-%m-%d"),
            "date_jp": to_reiwa(ev_date),
            "sign": to_reiwa(now),
            "addr": addr,
            "name": u_name,
            "blood": blood,
            "phone": u_phone,
            "emergency": u_emer,
            "p_addr": p_addr,
            "p_name": p_name
        }

        pdf = create_pdf(data)
        fname = f"誓約書_{safe_filename(u_name)}_{now.strftime('%Y%m%d%H%M')}.pdf"

        try:
            payload = {
                "fileName": fname,
                "pdfData": base64.b64encode(pdf).decode(),
                "evDate": data["date"],
                "uName": u_name
            }

            res = requests.post(
                GAS_URL,
                data=json.dumps(payload),
                headers={"Content-Type":"application/json"},
                timeout=20
            )

            if res.status_code == 200:
                try:
                    result = res.json()
                    if result.get("status") == "ok":
                        st.success("申込完了！保存されました")
                    else:
                        st.warning("送信完了（保存結果不明）PDFを保存してください")
                except:
                    st.warning("応答不正。PDFを保存してください")
            else:
                st.error(f"サーバーエラー: {res.status_code}")

        except:
            st.error("通信エラー")

        st.download_button("PDF保存", pdf, fname)
