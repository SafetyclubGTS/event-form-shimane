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
# 誓約文（絶対固定）
# =========================
PLEDGE_TEXT = """私は、この練習会に参加するに当たり,主催者(インストラクターおよび指導者等)の指示を守ります。
また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし、
主催者に責任を追及したり、損害賠償を要求しないことを誓約します。
※原則として参加車両は任意保険への加入をお願いします。
教習所内の施設を破壊した場合、自己負担で賠償となります。
(教習車・信号機等は数百万円の賠償となります)"""

P1 = "※本フォームで取得した個人情報は、本練習会の運営及び緊急時の連絡以外の目的には使用いたしません。"

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

def to_reiwa_datetime(dt):
    y = dt.year - 2018
    era = f"令和{y if y>1 else '元'}年"
    return f"{era} {dt.month}月 {dt.day}日 {dt.hour}時{dt.minute}分{dt.second}秒"

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
# PDF生成
# =========================
def create_pdf(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=15*mm, bottomMargin=15*mm)

    jp = ParagraphStyle(name='JP', fontName='HeiseiKakuGo-W5', fontSize=11, leading=16, wordWrap='CJK')
    title = ParagraphStyle(name='Title', fontName='HeiseiKakuGo-W5', fontSize=16, alignment=1)

    story = []

    story.append(Paragraph("GTS二輪車安全運転練習会 誓約書", title))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"開催日：{data['date_jp']}", jp))
    story.append(Spacer(1, 10))

    story.append(Paragraph("【誓約事項】", jp))

    for line in PLEDGE_TEXT.split("\n"):
        story.append(Paragraph(line, jp))

    story.append(Spacer(1, 20))

    table = Table([
        [Paragraph("署名日", jp), Paragraph(data["sign"], jp)],
        [Paragraph("住所", jp), Paragraph(data["addr"], jp)],
        [Paragraph("氏名", jp), Paragraph(f"{data['name']} (血液型:{data['blood']})", jp)],
        [Paragraph("連絡先", jp), Paragraph(f"本人:{data['phone']} / 緊急:{data['emergency']}", jp)],
    ], colWidths=[30*mm, 140*mm])

    table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black)]))
    story.append(table)

    if data["p_name"]:
        story.append(Spacer(1, 15))
        story.append(Paragraph("【親権者署名】 ※未成年の場合必須", jp))
        p_table = Table([
            [Paragraph("住所", jp), Paragraph(data["p_addr"], jp)],
            [Paragraph("氏名", jp), Paragraph(data["p_name"], jp)],
        ], colWidths=[30*mm, 140*mm])
        p_table.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.black)]))
        story.append(p_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph(P1, ParagraphStyle(name='Small', fontName='HeiseiKakuGo-W5', fontSize=8)))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"送信日時：{data['timestamp']}（日本標準時）",
                           ParagraphStyle(name='Small2', fontName='HeiseiKakuGo-W5', fontSize=8)))

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

    addr1 = st.text_input("住所（市区町村・町名）", value=st.session_state.addr_input)
    addr2 = st.text_input("番地")
    addr3 = st.text_input("建物名・部屋番号")

    u_name = st.text_input("氏名")
    blood = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    u_phone = st.text_input("電話番号")
    u_emer = st.text_input("緊急連絡先")

    is_minor = st.checkbox("未成年（18歳未満）の方はこちらにチェック")

    st.info("未成年の方のみ入力してください")
    p_addr = st.text_input("親権者住所")
    p_name = st.text_input("親権者氏名")

    st.subheader("誓約事項")
    st.text(PLEDGE_TEXT)

    agree = st.checkbox("上記誓約事項に同意します")
    submit = st.form_submit_button("送信")

# =========================
# 送信処理
# =========================
if submit:

    if not agree or not u_name or not addr1 or not addr2 or not u_phone:
        st.error("必須項目を入力してください")

    elif not is_valid_phone(u_phone):
        st.error("電話番号形式エラー")

    elif is_minor and (not p_name or not p_addr):
        st.error("未成年は親権者情報が必要です")

    else:
        now = datetime.now(JST)

        full_addr = f"{addr1} {addr2} {addr3}".strip()

        data = {
            "date": ev_date.strftime("%Y-%m-%d"),
            "date_jp": to_reiwa(ev_date),
            "sign": to_reiwa(now),
            "timestamp": to_reiwa_datetime(now),
            "addr": full_addr,
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

            res = requests.post(GAS_URL, data=json.dumps(payload),
                                headers={"Content-Type":"application/json"}, timeout=20)

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
