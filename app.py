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
from datetime import datetime

# --- 【最新】デプロイ済みのGASウェブアプリURL ---
GAS_URL = "https://script.google.com/macros/s/AKfycbxB94Sxkdwg44Apb36p-Ibrne9e5nYDtpgiSImuXjYrl5Tp1L14mVQKYVsjVCn5zUGD/exec"

# --- 1. 基本設定 ---
st.set_page_config(page_title="GTS参加申込", page_icon="🏍️")

# PDF用日本語フォントの登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    """郵便番号から住所を自動取得する外部API連携"""
    if len(zipcode) == 7:
        try:
            u = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
            res = requests.get(u, timeout=5)
            d = res.json()
            if d["results"]:
                r = d["results"][0]
                return f"{r['address1']}{r['address2']}{r['address3']}"
        except:
            return ""
    return ""

# --- 2. 誓約書の文言（原本再現） ---
S1 = "私は、この練習会に参加するに当たり、主催者(インストラクターおよび指導者等)"
S2 = "の指示を守ります。また、受講中に物損事故等が発生した場合、それに伴う損失"
S3 = "は全て自己負担とし主催者に責任を追及したり、損害賠償を要求しないことを誓約"
S4 = "します。"

W1 = "※原則として参加車両は任意保険への加入をお願いします、教習所内の施設を破壊した"
W2 = "場合、自己負担で賠償となります。"
W3 = "(教習車・信号機等は数百万円の賠償となります)"

P1 = "※本フォームで取得した個人情報は、本練習会の運営および緊急時の連絡以外の"
P2 = "目的には使用いたしません。"

# --- 3. アプリ画面UI ---
st.title("GTS二輪車安全運転練習会\n申込フォーム")

if "auto_addr" not in st.session_state:
    st.session_state.auto_addr = ""

# 開催日入力
st.subheader("【開催日】")
n = datetime.now()
c1, c2, c3 = st.columns(3)
with c1:
    sy = st.selectbox("年", [2026, 2027], index=0)
with c2:
    sm = st.selectbox("月", list(range(1, 13)), index=(n.month - 1))
with c3:
    sd = st.selectbox("日", list(range(1
