import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns
import re
import time
from collections import Counter
from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

import gensim.corpora as corpora
from gensim.models import LdaModel, CoherenceModel

st.set_page_config(
    page_title="Topic Modeling: LDA vs NMF",
    page_icon="\U0001F4F0",
    layout="wide",
    initial_sidebar_state="expanded",
)

UTM_LOGO_B64 = ""

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-header {
    background: linear-gradient(135deg, #0f2342 0%, #1a3a6b 50%, #2E75B6 100%);
    padding: 2.2rem 2rem; border-radius: 14px; margin-bottom: 1.8rem;
    text-align: center; color: white;
    box-shadow: 0 4px 20px rgba(46,117,182,0.3);
}
.main-header h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.4rem; letter-spacing: -0.3px; }
.main-header .sub { font-size: 0.92rem; opacity: 0.85; margin: 0.15rem 0; }
.main-header .author { font-size: 0.78rem; opacity: 0.65; margin-top: 0.6rem; }
.metric-card {
    background: white; border-radius: 12px; padding: 1.3rem 1rem;
    border-left: 4px solid #2E75B6;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    text-align: center; height: 100%;
}
.metric-card .val { font-size: 1.9rem; font-weight: 700; color: #2E75B6; line-height: 1.1; }
.metric-card .lbl { font-size: 0.78rem; color: #666; margin-top: 0.3rem; line-height: 1.4; }
.metric-green .val { color: #2e7d32; }
.metric-green      { border-left-color: #2e7d32; }
.metric-orange .val{ color: #e65100; }
.metric-orange     { border-left-color: #e65100; }
.metric-purple .val{ color: #6a1b9a; }
.metric-purple     { border-left-color: #6a1b9a; }
.section-header {
    background: linear-gradient(90deg, #f0f4ff, #f8f9ff);
    border-radius: 8px; padding: 0.8rem 1.2rem;
    border-left: 4px solid #2E75B6; margin: 1.5rem 0 1rem 0;
    font-weight: 700; font-size: 1.05rem; color: #1e3a5f;
}
.info-box {
    background: #f0f7ff; border: 1px solid #b3d1f5;
    border-radius: 10px; padding: 1.1rem 1.4rem; margin-bottom: 1.2rem;
    color: #1e3a5f; font-size: 0.93rem; line-height: 1.75;
}
.info-box b { color: #1a5fa8; }
.stProgress > div > div { background-color: #2E75B6 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>PERBANDINGAN LATENT DIRICHLET ALLOCATION DENGAN NON NEGATIVE MATRIX FACTORIZATION UNTUK PEMODELAN TOPIK BERITA</h1>
    <div class="sub">Perbandingan LDA dan NMF &nbsp;</div>
</div>
""", unsafe_allow_html=True)

COL_ID       = "id_berita"
COL_JUDUL    = "judul"
COL_ISI      = "isi_berita"
COL_KATEGORI = "kategori"
RANDOM_SEED  = 42
np.random.seed(RANDOM_SEED)

with st.sidebar:
    st.markdown("## Konfigurasi")
    st.markdown("---")
    st.markdown("**Parameter Model Terbaik**")
    n_topics = st.slider("Jumlah Topik (K)", min_value=2, max_value=8, value=4)
    n_top_words = st.slider("Kata Dominan per Topik", min_value=5, max_value=20, value=10)
    max_feat = st.select_slider("Max Features TF-IDF", options=[1000, 3000, 5000, 8000, 10000], value=10000)
    st.markdown("**Parameter LDA**")
    lda_passes = st.slider("LDA Passes", min_value=5, max_value=30, value=20)
    lda_iterations = st.slider("LDA Iterations", min_value=10, max_value=100, value=50)
    lda_alpha = st.selectbox("Alpha LDA", options=["0.1"], index=0)
    lda_eta = st.select_slider("Eta LDA", options=[0.001, 0.005, 0.01, 0.05, 0.1], value=0.01)
    st.markdown("**Parameter NMF**")
    nmf_init = st.selectbox("Init NMF", options=["random"], index=0)
    nmf_iter = st.slider("Max Iter NMF", min_value=100, max_value=500, value=200)

BLUE   = "#2E75B6"
ORANGE = "#ED7D31"
GREEN  = "#2e7d32"

def set_ax_style(ax, bg="#f8f9ff"):
    ax.set_facecolor(bg)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)

def plot_k_optimal_static():
    k_vals        = [2, 3, 4, 5, 6, 7, 8]
    lda_cvs       = [0.4484, 0.6126, 0.6012, 0.6301, 0.6139, 0.6091, 0.5864]
    nmf_cvs       = [0.6971, 0.7934, 0.7645, 0.7465, 0.7680, 0.7921, 0.7656]
    log_perp_lda  = [7.7355, 7.6340, 7.5664, 7.4932, 7.4676, 7.4453, 7.4225]
    recon_err_nmf = [67.4821, 62.1045, 60.2670, 59.8832, 58.4410, 57.2098, 56.4991]
    chosen_k      = 4
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4))
    fig.patch.set_facecolor("#f8f9ff")
    ax1.plot(k_vals, lda_cvs, "o-", color=BLUE,   lw=2, ms=7, label="LDA")
    ax1.plot(k_vals, nmf_cvs, "s-", color=ORANGE, lw=2, ms=7, label="NMF")
    ax1.axvline(chosen_k, color="red", ls="--", alpha=0.65, label=f"K={chosen_k} dipilih")
    ax1.set_title("Topic Coherence (Cv) vs K", fontweight="bold")
    ax1.set_xlabel("Jumlah Topik (K)"); ax1.set_ylabel("Coherence Cv")
    ax1.set_xticks(k_vals); ax1.legend(fontsize=9); set_ax_style(ax1)
    for k, v in zip(k_vals, lda_cvs):
        ax1.annotate(f"{v:.4f}", (k, v), textcoords="offset points", xytext=(-4, 9), ha="center", fontsize=7.5, color=BLUE)
    for k, v in zip(k_vals, nmf_cvs):
        ax1.annotate(f"{v:.4f}", (k, v), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=7.5, color=ORANGE)
    ax2.plot(k_vals, log_perp_lda, "o-", color=BLUE, lw=2, ms=7, label="Log-Perplexity LDA")
    ax2.axvline(chosen_k, color="red", ls="--", alpha=0.65, label=f"K={chosen_k} dipilih")
    ax2.set_title("Log-Perplexity LDA vs K\n(\u2193 semakin kecil = semakin baik)", fontweight="bold")
    ax2.set_xlabel("Jumlah Topik (K)"); ax2.set_ylabel("Log-Perplexity (positif)")
    ax2.set_xticks(k_vals); ax2.legend(fontsize=9); set_ax_style(ax2)
    for k, v in zip(k_vals, log_perp_lda):
        ax2.annotate(f"{v:.4f}", (k, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=7.5, color=BLUE)
    ax3.plot(k_vals, recon_err_nmf, "s-", color=ORANGE, lw=2, ms=7, label="Reconstruction Error NMF")
    ax3.axvline(chosen_k, color="red", ls="--", alpha=0.65, label=f"K={chosen_k} dipilih")
    ax3.set_title("Reconstruction Error NMF vs K\n(\u2193 semakin kecil = semakin baik)", fontweight="bold")
    ax3.set_xlabel("Jumlah Topik (K)"); ax3.set_ylabel("Reconstruction Error \u2016X \u2212 WH\u2016")
    ax3.set_xticks(k_vals); ax3.legend(fontsize=9); set_ax_style(ax3)
    for k, v in zip(k_vals, recon_err_nmf):
        ax3.annotate(f"{v:.4f}", (k, v), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=7.5, color=ORANGE)
    plt.tight_layout()
    return fig

STATIC = {
    "lda_cv"        : 0.4830,
    "nmf_cv"        : 0.7645,
    "log_perp_lda"  : 7.5664,
    "perplexity_lda": 1932.30,
    "waktu_lda"     : 63.96,
    "waktu_nmf"     : 0.22,
    "stem_results"  : {
        "Dengan Stemming": {"LDA_Coherence": 0.4830, "NMF_Coherence": 0.7645},
        "Tanpa Stemming" : {"LDA_Coherence": 0.4751, "NMF_Coherence": 0.8181},
    },
}

tab3 = st.container()
with tab3:
    st.markdown('<div class="section-header">Pencarian Jumlah Topik Optimal (K)</div>', unsafe_allow_html=True)
    k_data = {
        "K": [2, 3, 4, 5, 6, 7, 8],
        "LDA Coherence (Cv)": [0.4484, 0.6126, 0.6012, 0.6301, 0.6139, 0.6091, 0.5864],
        "NMF Coherence (Cv)": [0.6971, 0.7934, 0.7645, 0.7465, 0.7680, 0.7921, 0.7656],
        "Log-Perplexity LDA": [7.7355, 7.6340, 7.5664, 7.4932, 7.4676, 7.4453, 7.4225],
        "Reconstruction Error NMF": [67.4821, 62.1045, 60.2670, 59.8832, 58.4410, 57.2098, 56.4991],
        "Keterangan": ["\u2014", "NMF Cv tertinggi (0.7934)", "K dipilih", "LDA Cv tertinggi (0.6301)", "\u2014", "\u2014", "\u2014"],
    }
    df_k = pd.DataFrame(k_data).set_index("K")
    st.dataframe(df_k, use_container_width=True)
    st.pyplot(plot_k_optimal_static(), use_container_width=True)

    st.markdown("#### Perbandingan Dengan vs Tanpa Stemming (Baseline)")
    df_stem = pd.DataFrame({
        "Pipeline": ["Dengan Stemming", "Tanpa Stemming"],
        "LDA Cv": [STATIC["stem_results"]["Dengan Stemming"]["LDA_Coherence"], STATIC["stem_results"]["Tanpa Stemming"]["LDA_Coherence"]],
        "NMF Cv": [STATIC["stem_results"]["Dengan Stemming"]["NMF_Coherence"], STATIC["stem_results"]["Tanpa Stemming"]["NMF_Coherence"]],
    }).set_index("Pipeline")
    st.dataframe(df_stem, use_container_width=True)

    st.markdown("#### Waktu Komputasi Model Final (K=4)")
    bl1, bl2, bl3 = st.columns(3)
    for col_m, val, lbl in [
        (bl1, f"{STATIC['waktu_lda']:.2f} detik", "Waktu Latih LDA"),
        (bl2, f"{STATIC['waktu_nmf']:.2f} detik", "Waktu Latih NMF"),
        (bl3, f"{STATIC['waktu_lda']/STATIC['waktu_nmf']:.0f}x lebih cepat", "NMF vs LDA"),
    ]:
        col_m.markdown(f'<div class="metric-card"><div class="val" style="font-size:1.2rem;">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)