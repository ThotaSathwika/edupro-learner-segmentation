import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from utils import load_data, recommend, learning_path, NUM_FEATURES

st.set_page_config(page_title="EduPro · Learner Intelligence", page_icon="🎓", layout="wide")

# ---------------- Design system ----------------
NEON = ["#A78BFA", "#22D3EE", "#F472B6", "#FBBF24", "#34D399", "#FB7185", "#60A5FA"]
SEG_META = {
    "Multi-Domain Power Learners": {"icon": "🚀", "color": "#A78BFA",
                                    "tag": "Explore everything, learn non-stop"},
    "Career-Focused Paid Learners": {"icon": "🎯", "color": "#22D3EE",
                                     "tag": "Invest in targeted, career-ready skills"},
    "Free-Course Samplers": {"icon": "🌱", "color": "#F472B6",
                             "tag": "Testing the waters with free courses"},
}
SEG_COLORS = {k: v["color"] for k, v in SEG_META.items()}
SHORT = {"Multi-Domain Power Learners": "🚀 Power Learners", "Career-Focused Paid Learners": "🎯 Career-Focused",
         "Free-Course Samplers": "🌱 Free Samplers"}
SHORT_COLORS = {SHORT[k]: v for k, v in SEG_COLORS.items()}
LEVEL_ORDER = {"CourseLevel": ["Beginner", "Intermediate", "Advanced"]}
LEVEL_COLORS = {"Beginner": "#34D399", "Intermediate": "#FBBF24", "Advanced": "#FB7185"}

pio.templates["edupro"] = go.layout.Template(layout=dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Poppins, sans-serif", color="#C7CBE6", size=13),
    title=dict(font=dict(size=17, color="#FFFFFF"), x=0.01),
    colorway=NEON,
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.08)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.22),
    margin=dict(l=10, r=10, t=55, b=50),
    hoverlabel=dict(bgcolor="#1B2150", bordercolor="#A78BFA", font=dict(color="#fff")),
))
pio.templates.default = "plotly_dark+edupro"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
html, body, [class*="css"], .stMarkdown, p, label, span, div { font-family: 'Poppins', sans-serif; }
.stApp {
  background:
    radial-gradient(900px 500px at 8% -10%, rgba(167,139,250,.28), transparent 60%),
    radial-gradient(800px 500px at 100% 0%, rgba(34,211,238,.20), transparent 60%),
    radial-gradient(700px 600px at 50% 110%, rgba(244,114,182,.16), transparent 60%),
    #070B1A;
  background-attachment: fixed;
}
.block-container { padding-top: 1.6rem; max-width: 1350px; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(20,24,60,.95), rgba(9,12,30,.95));
  border-right: 1px solid rgba(167,139,250,.18);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
  padding: .65rem .9rem; margin: .18rem 0; border-radius: 14px; width: 100%;
  border: 1px solid transparent; transition: all .25s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  background: rgba(167,139,250,.12); border-color: rgba(167,139,250,.35); transform: translateX(4px);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(90deg, rgba(167,139,250,.35), rgba(34,211,238,.18));
  border-color: rgba(167,139,250,.6); box-shadow: 0 0 18px rgba(167,139,250,.25);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-selected="true"] {
  background: linear-gradient(90deg, rgba(167,139,250,.35), rgba(34,211,238,.18));
  border-color: rgba(167,139,250,.6); box-shadow: 0 0 18px rgba(167,139,250,.25);
}
section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:not([data-testid="stMarkdownContainer"]) { display: none; }
section[data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-size: 1rem; font-weight: 500; }
.brand { font-weight: 800; font-size: 1.6rem; letter-spacing: -.5px;
  background: linear-gradient(90deg,#A78BFA,#22D3EE,#F472B6); -webkit-background-clip: text; color: transparent; }
.brand-sub { color:#8E93B8; font-size:.8rem; margin-top:-6px; }

.hero { position: relative; padding: 2.1rem 2.2rem; border-radius: 26px; margin-bottom: 1.4rem; overflow: hidden;
  background: linear-gradient(135deg, rgba(167,139,250,.20), rgba(34,211,238,.10) 55%, rgba(244,114,182,.14));
  border: 1px solid rgba(255,255,255,.10); backdrop-filter: blur(14px); }
.hero:after { content:""; position:absolute; width:320px; height:320px; right:-80px; top:-120px; border-radius:50%;
  background: radial-gradient(circle, rgba(34,211,238,.35), transparent 70%); animation: float 7s ease-in-out infinite; }
@keyframes float { 0%,100% { transform: translateY(0) } 50% { transform: translateY(25px) } }
.hero h1 { font-size: 2.35rem; font-weight: 800; line-height: 1.15; margin: 0;
  background: linear-gradient(90deg,#fff 0%,#C4B5FD 35%,#67E8F9 65%,#F9A8D4 100%); background-size: 200% auto;
  -webkit-background-clip: text; color: transparent; animation: shine 6s linear infinite; }
@keyframes shine { to { background-position: 200% center; } }
.hero p { color:#B7BCE0; margin:.55rem 0 0; font-size:1.02rem; max-width: 820px; }
.pill { display:inline-block; padding:.22rem .7rem; border-radius:999px; font-size:.75rem; font-weight:600;
  background: rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); color:#E0E3FF; margin:0 .35rem .6rem 0; }

.kpi-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(170px,1fr)); gap: 14px; margin-bottom: 1.2rem; }
.kpi { padding: 1.05rem 1.15rem; border-radius: 20px; background: rgba(255,255,255,.045);
  border: 1px solid rgba(255,255,255,.09); backdrop-filter: blur(10px); transition: all .3s ease; position: relative; overflow:hidden; }
.kpi:hover { transform: translateY(-4px); border-color: var(--c); box-shadow: 0 10px 30px -10px var(--c); }
.kpi:before { content:""; position:absolute; left:0; top:0; height:3px; width:100%; background: linear-gradient(90deg,var(--c),transparent); }
.kpi .ico { font-size:1.35rem; }
.kpi .lbl { color:#9AA0C8; font-size:.78rem; text-transform:uppercase; letter-spacing:1px; margin-top:.25rem; }
.kpi .val { font-size:1.75rem; font-weight:800; color:#fff; line-height:1.2; }
.kpi .sub { color: var(--c); font-size:.78rem; font-weight:600; }

.card { padding: 1.3rem 1.4rem; border-radius: 22px; background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.09); backdrop-filter: blur(10px); height: 100%; transition: all .3s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 16px 40px -18px var(--c); border-color: var(--c); }
.seg-ico { font-size: 2.3rem; }
.seg-name { font-weight: 800; font-size: 1.12rem; color: #fff; margin-top: .3rem; }
.seg-tag { color: #A3A8CF; font-size: .86rem; margin-bottom: .8rem; }
.bar { height: 8px; border-radius: 99px; background: rgba(255,255,255,.07); overflow: hidden; margin: .25rem 0 .7rem; }
.bar > span { display:block; height:100%; border-radius:99px; background: linear-gradient(90deg, var(--c), #fff0); }
.row { display:flex; justify-content:space-between; color:#C9CDEB; font-size:.84rem; }
.row b { color:#fff; }

.section { font-size: 1.35rem; font-weight: 800; color: #fff; margin: 1.6rem 0 .6rem; display:flex; align-items:center; gap:.5rem; }
.section:after { content:""; flex:1; height:1px; background: linear-gradient(90deg, rgba(167,139,250,.5), transparent); margin-left:.6rem; }

.rec { display:flex; gap: 1rem; align-items:center; padding: .95rem 1.15rem; border-radius: 18px; margin-bottom: .7rem;
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08); transition: all .25s ease; }
.rec:hover { background: rgba(167,139,250,.10); border-color: rgba(167,139,250,.45); transform: translateX(6px); }
.rank { min-width: 44px; height: 44px; border-radius: 14px; display:flex; align-items:center; justify-content:center;
  font-weight:800; color:#0B0F24; background: linear-gradient(135deg,#A78BFA,#22D3EE); }
.rec-body { flex: 1; }
.rec-title { color:#fff; font-weight:600; font-size:1.02rem; }
.chip { display:inline-block; font-size:.72rem; padding:.12rem .55rem; border-radius:99px; margin:.25rem .3rem 0 0;
  border:1px solid; font-weight:600; }
.match { text-align:right; min-width: 120px; }
.match .pct { font-size:1.3rem; font-weight:800; color:#fff; }
.match .small { color:#9AA0C8; font-size:.72rem; }

.path { display:flex; align-items:stretch; gap: 0; overflow-x:auto; padding: .6rem 0 1rem; }
.step { flex: 1; min-width: 165px; padding: 1rem; border-radius: 18px; background: rgba(255,255,255,.05);
  border: 1px solid var(--c); box-shadow: 0 0 22px -12px var(--c); }
.step .n { font-size:.7rem; color: var(--c); font-weight:800; letter-spacing:1.5px; }
.step .t { color:#fff; font-weight:600; margin:.25rem 0; }
.step .l { color:#A3A8CF; font-size:.8rem; }
.arrow { display:flex; align-items:center; padding: 0 .5rem; color:#6B71A3; font-size:1.4rem; }

.profile { display:flex; gap:1.2rem; align-items:center; padding: 1.3rem 1.5rem; border-radius: 24px; margin: .6rem 0 1rem;
  background: linear-gradient(120deg, rgba(255,255,255,.06), rgba(255,255,255,.02)); border:1px solid var(--c); }
.avatar { width: 74px; height: 74px; border-radius: 22px; display:flex; align-items:center; justify-content:center; font-size:2.2rem;
  background: radial-gradient(circle at 30% 30%, var(--c), #1B2150); box-shadow: 0 0 30px -6px var(--c); }
.p-id { color:#fff; font-size:1.5rem; font-weight:800; }
.p-seg { color: var(--c); font-weight:600; }
.p-meta { color:#A3A8CF; font-size:.88rem; }

div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"] { background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.08); border-radius: 20px; padding: .5rem; }
div.stButton > button { border-radius: 14px; border: 1px solid rgba(167,139,250,.6); font-weight: 600;
  background: linear-gradient(90deg, rgba(167,139,250,.25), rgba(34,211,238,.18)); color: #fff; transition: all .25s; }
div.stButton > button:hover { box-shadow: 0 0 22px rgba(167,139,250,.5); transform: translateY(-2px); border-color:#22D3EE; color:#fff; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 12px; padding: .45rem 1rem; background: rgba(255,255,255,.04); }
.stTabs [aria-selected="true"] { background: linear-gradient(90deg, rgba(167,139,250,.35), rgba(34,211,238,.2)); }
.foot { color:#6B71A3; font-size:.78rem; text-align:center; margin-top:2.5rem; }
</style>
""", unsafe_allow_html=True)


# ---------------- Data ----------------
@st.cache_data
def get_data():
    users, courses, tx = load_data()
    feat = pd.read_csv("outputs/learner_features.csv")
    res = json.load(open("outputs/results.json"))
    prof = pd.read_csv("outputs/segment_profiles.csv", index_col=0)
    return users, courses, tx, feat, res, prof


users, courses, tx, feat, res, prof = get_data()
rev_share = (feat.groupby("segment").total_spend.sum() / feat.total_spend.sum() * 100)
seg_order = [s for s in SEG_META if s in prof.index]


# ---------------- Helpers ----------------
def kpis(items):
    html = '<div class="kpi-grid">'
    for ico, lbl, val, sub, c in items:
        html += f'<div class="kpi" style="--c:{c}"><div class="ico">{ico}</div><div class="lbl">{lbl}</div><div class="val">{val}</div><div class="sub">{sub}</div></div>'
    st.markdown(html + "</div>", unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)


def hero(title, text, pills=()):
    p = "".join(f'<span class="pill">{x}</span>' for x in pills)
    st.markdown(f'<div class="hero">{p}<h1>{title}</h1><p>{text}</p></div>', unsafe_allow_html=True)


def chip(text, color):
    return f'<span class="chip" style="color:{color};border-color:{color}55;background:{color}18">{text}</span>'


def seg_card(seg):
    m, r = SEG_META[seg], prof.loc[seg]
    share = r.learners / len(feat) * 100
    rows = [("Learners", f"{int(r.learners):,}", share), ("Revenue share", f"{rev_share[seg]:.1f}%", rev_share[seg]),
            ("Avg courses", f"{r.total_courses:.1f}", r.total_courses / prof.total_courses.max() * 100),
            ("Categories explored", f"{r.diversity_score:.1f}", r.diversity_score / prof.diversity_score.max() * 100),
            ("Paid share", f"{r.paid_share*100:.0f}%", r.paid_share * 100)]
    body = "".join(f'<div class="row"><span>{a}</span><b>{b}</b></div><div class="bar"><span style="width:{min(w,100):.0f}%"></span></div>'
                   for a, b, w in rows)
    return (f'<div class="card" style="--c:{m["color"]}"><div class="seg-ico">{m["icon"]}</div>'
            f'<div class="seg-name" style="color:{m["color"]}">{seg}</div><div class="seg-tag">{m["tag"]}</div>{body}'
            f'<div class="row"><span>Favourite topic</span><b>{r.top_category}</b></div></div>')


def show(fig, h=None):
    if h:
        fig.update_layout(height=h)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown('<div class="brand">🎓 EduPro</div><div class="brand-sub">Learner Intelligence Studio</div>', unsafe_allow_html=True)
    st.write("")
    page = st.radio("Navigate", ["🏠  Overview", "🧑‍🎓  Learner Studio", "🌌  Cluster Galaxy",
                                 "⚖️  Segment Showdown", "🧪  Model Lab"], label_visibility="collapsed")
    st.write("")
    st.markdown(f"""<div class="card" style="--c:#22D3EE;padding:1rem">
<div style="color:#9AA0C8;font-size:.75rem;letter-spacing:1px">MODEL HEALTH</div>
<div style="color:#fff;font-weight:800;font-size:1.3rem">Silhouette {res['silhouette']:.3f}</div>
<div style="color:#22D3EE;font-size:.8rem">K-Means ↔ Hierarchical ARI {res['ari_kmeans_vs_hier']:.2f}</div></div>""",
                unsafe_allow_html=True)
    st.markdown('<div class="foot">Built by Thota Sathwika<br>Machine Learning Internship · Unified Mentor</div>', unsafe_allow_html=True)


# ================= OVERVIEW =================
if page.endswith("Overview"):
    hero("Every learner is different.<br>Now EduPro knows how.",
         "Machine-learning segmentation of 3,000 learners and a cluster-aware recommender that turns behaviour into personalized learning journeys.",
         ["K-Means + Hierarchical", "Hybrid Recommender", "10,000 enrolments · 2025"])
    kpis([("👥", "Learners", f"{res['n_users']:,}", "15-35 yrs · balanced gender", "#A78BFA"),
          ("📚", "Courses", res["n_courses"], "12 categories", "#22D3EE"),
          ("🧾", "Enrolments", f"{res['n_tx']:,}", f"{res['free_tx_share']*100:.0f}% free", "#F472B6"),
          ("💰", "Revenue", f"${res['revenue']/1000:,.0f}K", "paid enrolments", "#FBBF24"),
          ("🧩", "Segments", res["k"], f"silhouette {res['silhouette']:.2f}", "#34D399")])

    section("✨ Meet the three learner tribes")
    cols = st.columns(len(seg_order))
    for c, s in zip(cols, seg_order):
        c.markdown(seg_card(s), unsafe_allow_html=True)

    section("📈 What learners do")
    a, b = st.columns([1.15, 1])
    cat = tx.groupby(["CourseCategory", "CourseLevel"]).size().reset_index(name="enrolments")
    with a:
        show(px.bar(cat, y="CourseCategory", x="enrolments", color="CourseLevel", orientation="h",
                    color_discrete_map=LEVEL_COLORS, category_orders=LEVEL_ORDER, title="Enrolments by category & level")
             .update_yaxes(categoryorder="total ascending", title=None), 470)
    with b:
        show(px.sunburst(feat, path=["segment", "pref_level"], color="segment", color_discrete_map=SEG_COLORS,
                         title="Segments → preferred level").update_traces(insidetextorientation="radial"), 470)
    a, b = st.columns(2)
    m = tx.groupby(tx.TransactionDate.dt.to_period("M").dt.to_timestamp()).agg(enrolments=("UserID", "size"),
                                                                                revenue=("Amount", "sum")).reset_index()
    with a:
        f = px.area(m, x="TransactionDate", y="enrolments", title="Monthly enrolments")
        f.update_traces(line=dict(color="#22D3EE", width=3), fillcolor="rgba(34,211,238,.18)")
        show(f.update_xaxes(title=None), 340)
    with b:
        f = px.histogram(feat, x="total_courses", nbins=16, title=f"Courses per learner · {res['single_course_share']*100:.0f}% stop after one")
        f.update_traces(marker=dict(color="#A78BFA", line=dict(color="#070B1A", width=1)))
        show(f, 340)

# ================= LEARNER STUDIO =================
elif page.endswith("Learner Studio"):
    hero("Learner Studio", "Pick a learner, see their DNA, and get a personalized learning path in one click.",
         ["Content similarity", "Peer popularity", "Rating-weighted"])

    if "uid" not in st.session_state:
        st.session_state.uid = feat.sort_values("total_courses", ascending=False).UserID.iloc[5]

    def surprise():
        st.session_state.uid = feat.UserID.sample(1).iloc[0]

    c1, c2, c3 = st.columns([1.2, 1.6, .8])
    seg_filter = c1.selectbox("Segment", ["All segments"] + seg_order)
    pool = feat if seg_filter == "All segments" else feat[feat.segment == seg_filter]
    ids = pool.UserID.tolist()
    if st.session_state.uid not in ids:
        st.session_state.uid = ids[0]
    c2.selectbox("Learner", ids, key="uid")
    c3.write(""); c3.write("")
    c3.button("🎲 Surprise me", on_click=surprise, width="stretch")

    p = feat[feat.UserID == st.session_state.uid].iloc[0]
    m = SEG_META[p.segment]
    st.markdown(f"""<div class="profile" style="--c:{m['color']}"><div class="avatar">{m['icon']}</div>
<div><div class="p-id">{p.UserID}</div><div class="p-seg">{p.segment}</div>
<div class="p-meta">{p.Gender} · {p.age} yrs · loves <b style="color:#fff">{p.pref_category}</b> · usually picks <b style="color:#fff">{p.pref_level}</b></div></div></div>""",
                unsafe_allow_html=True)
    kpis([("📚", "Courses", int(p.total_courses), f"segment avg {prof.loc[p.segment,'total_courses']:.1f}", "#A78BFA"),
          ("🧭", "Categories", int(p.diversity_score), "diversity score", "#22D3EE"),
          ("💳", "Avg spend", f"${p.avg_spend:,.0f}", f"{p.paid_share*100:.0f}% paid", "#FBBF24"),
          ("🏔️", "Depth index", f"{p.depth_index:.2f}", "0 beginner → 1 advanced", "#F472B6"),
          ("⭐", "Avg rating", f"{p.avg_rating_enrolled:.2f}", "of courses taken", "#34D399")])

    a, b = st.columns([1, 1.25])
    with a:
        dna = ["total_courses", "diversity_score", "avg_spend", "depth_index", "avg_rating_enrolled", "paid_share", "enroll_freq_per_month"]
        labels = ["Courses", "Diversity", "Spend", "Depth", "Rating", "Paid share", "Frequency"]
        q = feat[dna].rank(pct=True)
        me = q[feat.UserID == p.UserID].iloc[0].values
        segavg = q[feat.segment == p.segment].mean().values
        f = go.Figure()
        f.add_trace(go.Scatterpolar(r=np.r_[segavg, segavg[0]], theta=labels + labels[:1], name="Segment average",
                                    line=dict(color="rgba(255,255,255,.5)", dash="dot"), fill="toself", fillcolor="rgba(255,255,255,.05)"))
        f.add_trace(go.Scatterpolar(r=np.r_[me, me[0]], theta=labels + labels[:1], name=p.UserID,
                                    line=dict(color=m["color"], width=3), fill="toself", fillcolor=m["color"] + "40"))
        f.update_layout(title="🧬 Learner DNA (percentile vs all learners)",
                        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 1], showticklabels=False, gridcolor="rgba(255,255,255,.1)"),
                                   angularaxis=dict(gridcolor="rgba(255,255,255,.1)")))
        show(f, 430)
    with b:
        h = tx[tx.UserID == p.UserID].sort_values("TransactionDate")
        f = px.scatter(h, x="TransactionDate", y="CourseCategory", color="CourseLevel", size=np.maximum(h.Amount, 40),
                       color_discrete_map=LEVEL_COLORS, category_orders=LEVEL_ORDER, hover_name="CourseName", title="🗓️ Learning journey so far")
        show(f.update_yaxes(title=None).update_xaxes(title=None), 430)

    section("🎯 Your personalized recommendations")
    f1, f2, f3 = st.columns([1, 1.4, .8])
    lv = f1.multiselect("Level", ["Beginner", "Intermediate", "Advanced"])
    cat = f2.multiselect("Category", sorted(courses.CourseCategory.unique()))
    n = f3.slider("How many", 3, 10, 5)
    recs = recommend(p.UserID, tx, courses, feat, top_n=n, level=lv or None, category=cat or None)
    if recs.empty:
        st.info("No courses match these filters — try widening them.")
    else:
        top = recs.score.max()
        html = ""
        for i, r in enumerate(recs.itertuples(), 1):
            price = "FREE" if r.CoursePrice == 0 else f"${r.CoursePrice:,.0f}"
            stars = "★" * int(round(r.CourseRating)) + "☆" * (5 - int(round(r.CourseRating)))
            html += (f'<div class="rec"><div class="rank">#{i}</div><div class="rec-body"><div class="rec-title">{r.CourseName}</div>'
                     f'{chip(r.CourseCategory, "#22D3EE")}{chip(r.CourseLevel, LEVEL_COLORS[r.CourseLevel])}'
                     f'{chip(price, "#FBBF24")}<span style="color:#FBBF24;font-size:.8rem">{stars}</span> '
                     f'<span style="color:#9AA0C8;font-size:.75rem">{r.CourseRating:.2f}</span></div>'
                     f'<div class="match"><div class="pct">{r.score/top*100:.0f}%</div><div class="small">match</div>'
                     f'<div class="bar" style="--c:#A78BFA;margin:.3rem 0 0"><span style="width:{r.score/top*100:.0f}%"></span></div></div></div>')
        st.markdown(html, unsafe_allow_html=True)

        section("🛤️ Recommended learning path")
        path = learning_path(recs)
        html = '<div class="path">'
        for i, r in enumerate(path.itertuples(), 1):
            if i > 1:
                html += '<div class="arrow">➜</div>'
            html += (f'<div class="step" style="--c:{LEVEL_COLORS[r.CourseLevel]}"><div class="n">STEP {i} · {r.CourseLevel.upper()}</div>'
                     f'<div class="t">{r.CourseName}</div><div class="l">{r.CourseCategory} · {r.CourseDuration:.0f} hrs</div></div>')
        st.markdown(html + "</div>", unsafe_allow_html=True)

        with st.expander("🔍 Why these courses? (score breakdown)"):
            br = recs.assign(Content=0.40 * recs.content_sim, Peers=0.35 * recs.cluster_popularity, Rating=0.25 * recs.CourseRating / 5)
            f = px.bar(br, y="CourseName", x=["Content", "Peers", "Rating"], orientation="h",
                       color_discrete_sequence=["#A78BFA", "#22D3EE", "#FBBF24"], title="Score = 0.40·content + 0.35·peer popularity + 0.25·rating")
            show(f.update_yaxes(autorange="reversed", title=None).update_xaxes(title="score"), 360)
    with st.expander("📜 Full enrolment history"):
        st.dataframe(h[["TransactionDate", "CourseName", "CourseCategory", "CourseLevel", "CourseType", "Amount"]],
                     hide_index=True, width="stretch")

# ================= CLUSTER GALAXY =================
elif page.endswith("Cluster Galaxy"):
    hero("Cluster Galaxy", "Every dot is a learner. Rotate the 3-D galaxy, hover to inspect, and see how the tribes separate.",
         [f"k = {res['k']}", f"PCA variance {sum(res['pca_var'])*100:.0f}% (2D)"])
    from sklearn.decomposition import PCA
    from utils import scale
    X, _ = scale(feat)
    P3 = PCA(3, random_state=42).fit_transform(X)
    g = feat.assign(x=P3[:, 0], y=P3[:, 1], z=P3[:, 2])
    tab1, tab2, tab3 = st.tabs(["🌌 3-D galaxy", "🔭 Explore any two features", "🧭 Category demand"])
    with tab1:
        f = px.scatter_3d(g, x="x", y="y", z="z", color="segment", color_discrete_map=SEG_COLORS, opacity=.75,
                          hover_data=["UserID", "total_courses", "avg_spend"])
        f.update_traces(marker=dict(size=3))
        f.update_layout(scene=dict(xaxis=dict(title="PC1", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,.08)"),
                                   yaxis=dict(title="PC2", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,.08)"),
                                   zaxis=dict(title="PC3", backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,.08)"),
                                   camera=dict(eye=dict(x=1.6, y=1.4, z=.9))))
        show(f, 620)
    with tab2:
        a, b = st.columns(2)
        xf = a.selectbox("X axis", NUM_FEATURES, index=0)
        yf = b.selectbox("Y axis", NUM_FEATURES, index=4)
        show(px.scatter(feat, x=xf, y=yf, color="segment", color_discrete_map=SEG_COLORS, opacity=.65,
                        marginal_x="violin", marginal_y="violin", hover_name="UserID").update_layout(legend_title_text=""), 560)
    with tab3:
        d = tx.merge(feat[["UserID", "segment"]]).groupby(["segment", "CourseCategory"]).size().reset_index(name="n")
        d["share"] = d.n / d.groupby("segment").n.transform("sum") * 100
        piv = d.pivot(index="segment", columns="CourseCategory", values="share").rename(index=SHORT)
        f = px.imshow(piv, color_continuous_scale=["#0B0F24", "#4C1D95", "#A78BFA", "#22D3EE"], aspect="auto",
                      text_auto=".1f", title="Share of each segment's enrolments by category (%)")
        show(f.update_xaxes(title=None).update_yaxes(title=None), 380)

# ================= SEGMENT SHOWDOWN =================
elif page.endswith("Segment Showdown"):
    hero("Segment Showdown", "Put the tribes head-to-head on any behaviour and spot where the opportunities are.",
         ["Engagement", "Spend", "Depth", "Diversity"])
    pick = st.multiselect("Segments in the ring", seg_order, default=seg_order)
    cols = st.columns(max(len(pick), 1))
    for c, s in zip(cols, pick):
        c.markdown(seg_card(s), unsafe_allow_html=True)

    section("🥊 Head-to-head")
    a, b = st.columns(2)
    with a:
        z = feat.groupby("segment")[NUM_FEATURES].mean()
        z = ((z - feat[NUM_FEATURES].mean()) / feat[NUM_FEATURES].std()).loc[pick]
        f = go.Figure()
        for s in pick:
            f.add_trace(go.Scatterpolar(r=list(z.loc[s]) + [z.loc[s].iloc[0]], theta=NUM_FEATURES + NUM_FEATURES[:1], name=s,
                                        line=dict(color=SEG_COLORS[s], width=3), fill="toself", fillcolor=SEG_COLORS[s] + "30"))
        f.update_layout(title="Segment profiles (z-score)", polar=dict(bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(gridcolor="rgba(255,255,255,.1)", showticklabels=False), angularaxis=dict(gridcolor="rgba(255,255,255,.1)")))
        show(f, 470)
    with b:
        metric = st.selectbox("Compare on", NUM_FEATURES, index=NUM_FEATURES.index("total_spend"))
        show(px.violin(feat[feat.segment.isin(pick)].assign(segment=lambda d: d.segment.map(SHORT)), x="segment", y=metric,
                       color="segment", box=True, color_discrete_map=SHORT_COLORS, title=f"Distribution of {metric}").update_layout(showlegend=False)
             .update_xaxes(title=None), 400)
    a, b = st.columns(2)
    with a:
        lvl = tx.merge(feat[["UserID", "segment"]]).groupby(["segment", "CourseLevel"]).size().reset_index(name="n")
        lvl = lvl[lvl.segment.isin(pick)]
        lvl["pct"] = lvl.n / lvl.groupby("segment").n.transform("sum") * 100
        lvl["segment"] = lvl.segment.map(SHORT)
        show(px.bar(lvl, x="pct", y="segment", color="CourseLevel", orientation="h", color_discrete_map=LEVEL_COLORS,
                    category_orders=LEVEL_ORDER,
                    title="Course level mix (%)").update_yaxes(title=None).update_xaxes(title=None), 340)
    with b:
        rv = pd.DataFrame({"segment": [SHORT[s] for s in pick], "Learners %": [prof.loc[s, "learners"] / len(feat) * 100 for s in pick],
                           "Revenue %": [rev_share[s] for s in pick]}).melt("segment")
        show(px.bar(rv, x="segment", y="value", color="variable", barmode="group",
                    color_discrete_sequence=["#22D3EE", "#F472B6"], title="Learners vs revenue share (%)")
             .update_xaxes(title=None).update_yaxes(title=None), 340)

# ================= MODEL LAB =================
else:
    hero("Model Lab", "How good are the segments and the recommender? Honest numbers, clearly explained.",
         ["Silhouette", "ARI", "Hit-rate@5", "Engagement lift"])
    kpis([("🧩", "Silhouette K-Means", res["silhouette"], "higher = better separated", "#A78BFA"),
          ("🌳", "Silhouette Hierarchical", res["hier_silhouette"], "Ward linkage", "#22D3EE"),
          ("🤝", "Agreement (ARI)", res["ari_kmeans_vs_hier"], "K-Means vs Hierarchical", "#34D399"),
          ("📏", "Davies-Bouldin", res["davies_bouldin"], "lower = better", "#FBBF24"),
          ("🔗", "Intra vs inter sim.", f"{res['intra_cluster_similarity']:.2f} / {res['inter_cluster_similarity']:.2f}", "behavioural consistency", "#F472B6")])
    a, b = st.columns(2)
    with a:
        k = pd.DataFrame({"k": list(map(int, res["k_search"])), "silhouette": list(res["k_search"].values())})
        f = px.line(k, x="k", y="silhouette", markers=True, title="Choosing k: silhouette score")
        f.update_traces(line=dict(color="#A78BFA", width=3), marker=dict(size=10, color="#22D3EE"))
        f.add_annotation(x=res["k"], y=res["silhouette"], text=f"chosen k = {res['k']}", showarrow=True, arrowcolor="#F472B6",
                         font=dict(color="#F472B6"), ay=-40)
        show(f, 380)
    with b:
        e = pd.DataFrame({"model": ["Hybrid (ours)", "Popularity", "Random"],
                          "hit": [res["hit_rate@5"][x] for x in ["hybrid", "popularity", "random"]]})
        f = px.bar(e, x="model", y="hit", color="model", text_auto=".3f",
                   color_discrete_sequence=["#A78BFA", "#22D3EE", "#6B71A3"], title=f"Hit-rate@5 · leave-last-out on {res['eval_users']} learners")
        show(f.update_layout(showlegend=False).update_xaxes(title=None).update_yaxes(title=None), 380)
    kpis([("🎯", "Hit-rate@5", res["hit_rate@5"]["hybrid"], "hybrid recommender", "#A78BFA"),
          ("📌", "Precision@5", res["precision@5"]["hybrid"], "relevance", "#22D3EE"),
          ("📈", "Lift vs popularity", f"{res['engagement_lift_vs_popularity']}×", "engagement proxy", "#34D399"),
          ("🎲", "Lift vs random", f"{res['engagement_lift_vs_random']}×", "engagement proxy", "#FBBF24")])
    st.markdown("""<div class="card" style="--c:#FBBF24"><b style="color:#FBBF24">💡 Reading the numbers honestly</b><br>
<span style="color:#C9CDEB">Enrolments in this dataset are spread almost evenly across the 60 courses (140-196 each), and learners rarely return
to a category they already took (45% vs 49% expected by chance). With so little pattern in the history, any offline test shows only a modest lift.
The right next step is a live A/B test measuring click-through, enrolment and completion.</span></div>""", unsafe_allow_html=True)

