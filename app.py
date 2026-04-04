import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import io
import requests
from datetime import datetime

# --- 基本設定 ---
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    if len(zipcode) == 7:
        try:
            res = requests.get(f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}")
            data = res.json()
            if data["results"]:
                r = data["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# タイトル
st.title("二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# --- 1. 開催日 ---
st.subheader("【開催日】")
c_y, c_m, c_d = st.columns(3)
with c_y:
    sel_y = st.selectbox("年", list(range(2026, 2051)), index=0)
with c_m:
    sel_m = st.selectbox("月", list(range(1, 13)), index=datetime.now().month - 1)
with c_d:
    sel_d = st.selectbox("日", list(range(1, 32)), index=datetime.now().day - 1)

event_date = f"令和{sel_y - 2018}年 {sel_m}月 {sel_d}日"

# --- 2. 住所 ---
st.subheader("【住所】")
zip_in = st.text_input("郵便番号（7桁・ハイフンなし）", max_chars=7, placeholder="6900000")
if st.button("住所を自動入力する"):
    st.session_state.auto_addr = get_address(zip_in)
    if not st.session_state.auto_addr:
        st.error("住所が見つかりませんでした。")

# --- 3. メインフォーム ---
with st.form("main_form"):
    addr = st.text_input(
        "住所（番地まで入力）", 
        value=st.session_state.auto_addr, 
        placeholder="島根県松江市打出町◯番地"
    )
    
    col_l, col_r = st.columns(2)
    with col_l:
        u_name = st.text_input("氏名", placeholder="山田 太郎")
        u_blood = st.selectbox("血液型", ["", "A", "B", "O", "AB"])
    with col_r:
        u_phone = st.text_input("電話番号", placeholder="090-0000-0000")
        
    u_emergency = st.text_input("緊急連絡先（氏名・続柄など）", placeholder="080-1111-1111（母）")
    
    st.divider()
    st.subheader("未成年の場合のみ入力")
    p_addr = st.text_input("親権者 住所", placeholder="参加者と異なる場合のみ入力")
    p_name = st.text_input("親権者 氏名", placeholder="保護者氏名")
    p_phone = st.text_input("親権者 電話", placeholder="090-2222-2222")

    st.divider()
    st.error("【重要：誓約事項】")
    
    # 安全な三連引用符
    st.write("""
    私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)の指示を守ります。
    また、受講中に物損事故等が発生した場合、それに伴う損失は全て自己負担とし主催者に責任を追及したり、
    損害賠償を要求しないことを誓約します。
    """)
    
    # 警告文（変数に入れてから表示することでエラーを回避）
    warn_1 = "※原則として参加車両は任意保険への加入をお願いします"
    warn_2 = "※教習所内の施設を破壊した場合、自己負担で賠償となります"
    warn_3 = "※(教習車・信号機等は数百万円の賠償となります)"
    
    st.write(f":red[{warn_1}]")
    st.write(f":red[{warn_2}]")
    st.write(f":red[{warn_3}]")
    
    st.info("【個人情報の取り扱い】ご入力いただいた情報は、運営および緊急連絡以外の目的には使用しません。")
    
    is_agree = st.checkbox
