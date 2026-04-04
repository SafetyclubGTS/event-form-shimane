import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# ページ設定
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# 日本語フォント（平成角ゴシック）の登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

# 郵便番号から住所を取得する関数
def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            res = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}")
            data = res.json()
            if data["results"]:
                result = data["results"][0]
                return f"{result['address1']}{result['address2']}{result['address3']}"
        except:
            return ""
    return ""

# タイトル（会と申の間で改行）
st.title("二輪車安全運転練習会\n申込フォーム")

# セッション状態（入力保持）の初期化
if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 1. 開催日の選択
st.subheader("【開催日】")
col_y, col_m, col_d = st.columns(3)
with col_y:
    selected_year = st.selectbox("年", list(range(2026, 2051)), index=0)
with col_m:
    selected_month = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
with col_d:
    selected_day = st.selectbox("日", list(range(1, 32)), index=datetime.now().day - 1)

event_date_str = f"令和{selected_year - 2018}年 {selected_month}月 {selected_day}日"

# 2. 住所検索
st.subheader("【住所検索】")
zip_input = st.text_input("郵便番号（7桁・ハイフンなし）を入力してEnter", max_chars=7)
if st.button("住所を検索する"):
    st.session_state.auto_addr = get_address(zip_input)
    if not st.session_state.auto_addr:
        st.error("住所が見つかりませんでした。")

# 3. メインフォーム
with st.form("entry_form"):
    address = st.text_input("住所（番地まで入力してください）", value=st.session_state.auto_addr)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("氏名")
        blood_type = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with col2:
        phone = st.text_input("電話番号")
        
    emergency_contact = st.text_input("緊急連絡先")
    
    st.divider()
    st.subheader("未成年の場合のみ入力")
    parent_address = st.text_input("親権者 住所")
    parent_name = st.text_input("親権者 氏名")
    parent_phone = st.text_input("親権者 電話")

    st.divider()
    st.error("【重要：誓約事項】※必ずご確認ください")
    
    st.write("""
    私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。
    また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、
    損害賠償を要求しないことを誓約します。
    """)
    
    st.markdown("**:red[※原則として参加車両は任意保険への加入をお願いします、]**")
    st.markdown("**:red[教習所内の施設を破壊した場合、自己負担で賠償となります。]**")
    st.markdown("
