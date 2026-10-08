import os
import inspect
from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st

import engine
from llm import generate_variance_commentary
from verifier import verify_commentary
from report_export import create_excel_report

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="BudgetSense AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Theme: Navy + Indigo + White corporate FP&A look
# ----------------------------------------------------------------------------
THEME_CSS = """
<style>

/* ---------- Global ---------- */
.stApp { background-color: #F5F7FB; }
header[data-testid="stHeader"] { background: #F5F7FB; }
.block-container {
    max-width: 1500px;
    padding: 4rem 2.2rem 4rem 2.2rem;
}
[data-testid="stMain"] p { color: #475569; }
h1, h2, h3 { color: #172554 !important; letter-spacing: -0.3px; }
hr { border-color: #E2E8F0 !important; }
.stCaption { color: #64748B !important; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: #0F172A; border-right: 1px solid #1E293B; }
[data-testid="stSidebar"] > div:first-child { background: #0F172A; }
[data-testid="stSidebar"][aria-expanded="true"] { min-width: 290px; max-width: 290px; }

.bs-brand-title { color: #FFFFFF; font-size: 1.45rem; font-weight: 800; letter-spacing: -0.4px; }
.bs-brand-sub {
    color: #94A3B8; font-size: 0.72rem; letter-spacing: 0.12em;
    text-transform: uppercase; margin-top: 2px;
}
.bs-side-label {
    color: #64748B; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin: 1.5rem 0 0.55rem 0;
}
.bs-nav a {
    display: block; color: #CBD5E1 !important; text-decoration: none !important;
    padding: 0.55rem 0.75rem; border-radius: 8px;
    font-size: 0.9rem; font-weight: 500; margin-bottom: 2px;
}
.bs-nav a:hover { background: #4338CA; color: #FFFFFF !important; }
.bs-nav .ico { display: inline-block; width: 1.5rem; color: #818CF8; }
.bs-nav a:hover .ico { color: #FFFFFF; }

[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: #4338CA; color: #FFFFFF; border: none;
    border-radius: 10px; font-weight: 650; padding: 0.6rem 1rem;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #3730A3; color: #FFFFFF; }
[data-testid="stSidebar"] .stButton > button p { color: #FFFFFF !important; }

[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: transparent; border: none; padding: 0; height: auto; min-height: 0;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: #1E293B; border: 1px dashed #475569; border-radius: 12px;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background: #EEF2FF !important; border: 1px solid #C7D2FE !important;
    border-radius: 9px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
    color: #3730A3 !important;
}

.bs-status-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.3rem 0; font-size: 0.85rem; }
.bs-status-dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.bs-status-name { color: #E2E8F0; font-weight: 600; }
.bs-status-val { color: #94A3B8; margin-left: auto; font-size: 0.78rem; }

/* ---------- Header ---------- */
.bs-anchor { scroll-margin-top: 70px; }
.bs-header {
    background: linear-gradient(135deg, #172554 0%, #1E3A8A 55%, #4338CA 100%);
    padding: 1.5rem 2rem; border-radius: 16px; margin-bottom: 1.2rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 10px 30px rgba(23, 37, 84, 0.12);
}
.bs-header-eyebrow {
    color: #A5B4FC; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
}
.bs-header-title { color: #FFFFFF; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.6px; }
.bs-header-subtitle { color: #DCE4FF; font-size: 0.95rem; margin-top: 0.15rem; }
.bs-live {
    display: flex; align-items: center; gap: 0.5rem;
    background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.18);
    color: #E0E7FF; padding: 0.4rem 0.85rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; white-space: nowrap;
}
.bs-live-dot { width: 8px; height: 8px; border-radius: 50%; background: #22C55E; }

/* ---------- KPI cards ---------- */
.bs-kpi {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 1.1rem 1.25rem; box-shadow: 0 4px 14px rgba(15,23,42,0.04);
    min-height: 128px;
}
.bs-kpi-accent { width: 28px; height: 3px; background: #4338CA; border-radius: 2px; margin-bottom: 0.65rem; }
.bs-kpi-label {
    color: #64748B; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.bs-kpi-value { color: #172554; font-size: 1.85rem; font-weight: 800; margin-top: 0.2rem; line-height: 1.2; }
.bs-kpi-note { color: #64748B; font-size: 0.78rem; margin-top: 0.3rem; }

/* ---------- Status strip ---------- */
.bs-strip {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 0.85rem 1.25rem; margin-top: 1rem;
    display: flex; gap: 2.5rem; flex-wrap: wrap;
    box-shadow: 0 4px 14px rgba(15,23,42,0.03);
}
.bs-strip-label {
    color: #64748B; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.bs-strip-value { color: #172554; font-size: 0.95rem; font-weight: 650; margin-top: 2px; }

/* ---------- Section titles ---------- */
.bs-section-title { color: #172554; font-size: 1.4rem; font-weight: 750; letter-spacing: -0.3px; margin-top: 1.8rem; }
.bs-section-sub { color: #64748B; font-size: 0.9rem; margin: 0.2rem 0 0.9rem 0; }
.bs-card-title { color: #172554; font-size: 0.98rem; font-weight: 700; }
.bs-card-sub { color: #64748B; font-size: 0.8rem; margin-bottom: 0.3rem; }

/* ---------- Cards / containers ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(15,23,42,0.035);
}
[data-testid="stExpander"] {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
}
[data-testid="stAlert"] { border-radius: 10px; }
[data-testid="stDataFrame"] {
    border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0;
}

/* ---------- Watchlist ---------- */
.bs-watch {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
    box-shadow: 0 4px 14px rgba(15,23,42,0.035); overflow: hidden;
}
.bs-watch-row {
    display: flex; align-items: center; gap: 0.9rem;
    padding: 0.95rem 1.3rem; border-bottom: 1px solid #EEF2F7;
}
.bs-watch-row:last-child { border-bottom: none; }
.bs-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.bs-watch-main { flex: 1; }
.bs-watch-name { color: #0F172A; font-size: 1rem; font-weight: 650; }
.bs-watch-sub { color: #64748B; font-size: 0.82rem; margin-top: 2px; }
.bs-watch-val { font-size: 1.15rem; font-weight: 800; white-space: nowrap; }

/* ---------- AI insight cards ---------- */
.bs-insight {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 4px solid #4338CA;
    border-radius: 12px; padding: 1.1rem 1.3rem; margin-top: 0.9rem;
    box-shadow: 0 4px 14px rgba(15,23,42,0.035);
}
.bs-insight-top { display: flex; justify-content: space-between; align-items: center; }
.bs-tag {
    background: #EEF2FF; color: #4338CA; font-size: 0.68rem; font-weight: 800;
    letter-spacing: 0.1em; padding: 0.2rem 0.55rem; border-radius: 6px;
}
.bs-insight-var { font-size: 0.95rem; font-weight: 800; }
.bs-insight-title { color: #172554; font-size: 1.1rem; font-weight: 700; margin: 0.55rem 0 0.5rem 0; }
.bs-insight-text { color: #334155; font-size: 0.95rem; line-height: 1.65; }
.bs-verify {
    display: inline-block; margin-top: 0.8rem; padding: 0.3rem 0.7rem;
    border-radius: 999px; font-size: 0.8rem; font-weight: 700;
}
.bs-verify.ok { background: #DCFCE7; color: #166534; }
.bs-verify.bad { background: #FEE2E2; color: #991B1B; }
.bs-issue { color: #991B1B; font-size: 0.82rem; margin-top: 0.4rem; }
.bs-placeholder {
    background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 12px;
    padding: 1rem 1.2rem; color: #64748B; font-size: 0.9rem; margin-top: 0.9rem;
}

/* ---------- Empty state ---------- */
.bs-empty {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
    padding: 2.4rem 2rem 1.6rem 2rem; text-align: center; margin-top: 1.2rem;
    box-shadow: 0 4px 14px rgba(15,23,42,0.035);
}
.bs-empty-title { color: #172554; font-size: 1.5rem; font-weight: 800; }
.bs-empty-text { color: #64748B; font-size: 0.95rem; margin-top: 0.4rem; }

/* ---------- Inputs and buttons (main area) ---------- */
[data-testid="stTextArea"] textarea {
    background-color: #FFFFFF !important; color: #172554 !important;
    border: 1px solid #D9E2F0 !important; border-radius: 12px !important;
    padding: 12px !important; font-size: 0.9rem !important; line-height: 1.5 !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #94A3B8 !important; opacity: 1 !important; }
[data-testid="stTextArea"] textarea:focus {
    border-color: #6366F1 !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.12) !important;
}

[data-testid="stMain"] .stButton > button {
    border-radius: 10px; border: 1px solid #CBD5E1; background: #FFFFFF;
    color: #1E3A8A; font-weight: 650; padding: 0.6rem 1.1rem;
}
[data-testid="stMain"] .stButton > button:hover { border-color: #6366F1; color: #4338CA; }

button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background: #4338CA !important; color: #FFFFFF !important; border: none !important;
    box-shadow: 0 6px 16px rgba(67,56,202,0.20);
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background: #3730A3 !important; color: #FFFFFF !important;
}
button[kind="primary"] p, [data-testid="stBaseButton-primary"] p { color: #FFFFFF !important; }

[data-testid="stDownloadButton"] > button {
    width: 100% !important; height: 54px !important;
    background: #4338CA !important; color: #FFFFFF !important;
    border: none !important; border-radius: 12px !important;
    font-size: 1rem !important; font-weight: 700 !important;
    box-shadow: 0 6px 16px rgba(67,56,202,0.18) !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #3730A3 !important; }
[data-testid="stDownloadButton"] > button p,
[data-testid="stDownloadButton"] > button span { color: #FFFFFF !important; }

/* ---------- Main-area uploader ---------- */
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF; border: 1px dashed #A5B4FC;
    border-radius: 14px; padding: 0.9rem 1rem;
}
[data-testid="stMain"] [data-testid="stFileUploaderDropzone"] button {
    background: #EEF2FF; color: #3730A3; border: 1px solid #C7D2FE;
    border-radius: 9px; font-weight: 650;
} 

</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
SAMPLE_PATH = os.path.join("data", "BudgetSense_Final_Clean_Dataset.xlsx")
REQUIRED_COLUMNS = ["Period", "Department", "Line_Item", "Line_Type", "Budget", "Actual"]

# The app looks for your engine function under these names (first match is used).
ENGINE_FUNCTION_CANDIDATES = [
    "analyze_budget",
    "analyze_variance",
    "analyze_budget_variance",
    "run_analysis",
    "analyze",
    "analyse",
    "calculate_variance",
    "process_data",
    "run_engine",
]

COLOR_RED = "#DC2626"
COLOR_GREEN = "#16A34A"
COLOR_AMBER = "#F59E0B"

# ----------------------------------------------------------------------------
# Session state (keeps data across Streamlit reruns)
# ----------------------------------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "data_source" not in st.session_state:
    st.session_state.data_source = ""
if "last_upload_id" not in st.session_state:
    st.session_state.last_upload_id = None
if "ai_results" not in st.session_state:
    st.session_state.ai_results = []
if "load_error" not in st.session_state:
    st.session_state.load_error = None

# Simple status flags shown in the sidebar (updated as the script progresses)
SYS = {"validation": "ready", "analysis": "ready"}


# ----------------------------------------------------------------------------
# Helper functions: data
# ----------------------------------------------------------------------------
def read_uploaded_file(uploaded_file):
    """Read an uploaded CSV or Excel file into a DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def set_data(df, source):
    """Store a new dataset and clear any old AI results."""
    st.session_state.df = df
    st.session_state.data_source = source
    st.session_state.ai_results = []


def load_sample():
    """Button callback: load the bundled sample dataset."""
    try:
        set_data(pd.read_excel(SAMPLE_PATH), "Sample dataset")
        st.session_state.load_error = None
    except Exception as e:
        st.session_state.load_error = (
            f"Could not load the sample dataset at '{SAMPLE_PATH}': {e}"
        )


def run_engine(df):
    """Call the financial engine, whatever the function is named."""
    for func_name in ENGINE_FUNCTION_CANDIDATES:
        func = getattr(engine, func_name, None)
        if callable(func):
            return func(df)

    public_functions = [
        n for n, obj in inspect.getmembers(engine, inspect.isfunction)
        if not n.startswith("_")
    ]
    raise RuntimeError(
        "Could not find the analysis function in engine.py. "
        f"Functions found: {public_functions}. "
        "Add the correct name to ENGINE_FUNCTION_CANDIDATES at the top of app.py."
    )


def validate_dataframe(df):
    """Return a list of problems found in the uploaded data (empty list = OK)."""
    problems = []

    if df is None or df.empty:
        return ["The file is empty."]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        problems.append(f"Missing required columns: {', '.join(missing)}")
        return problems

    for col in ["Budget", "Actual"]:
        converted = pd.to_numeric(df[col], errors="coerce")
        bad_rows = int(converted.isna().sum())
        if bad_rows > 0:
            problems.append(f"Column '{col}' has {bad_rows} missing or non-numeric value(s).")

    for col in ["Period", "Department", "Line_Item", "Line_Type"]:
        blank = int(df[col].isna().sum())
        if blank > 0:
            problems.append(f"Column '{col}' has {blank} blank value(s).")

    if not problems:
        valid_types = {"revenue", "cost"}
        found_types = set(df["Line_Type"].astype(str).str.strip().str.lower().unique())
        invalid = found_types - valid_types
        if invalid:
            problems.append(
                "Line_Type must be 'Revenue' or 'Cost'. "
                f"Unexpected value(s): {', '.join(sorted(invalid))}"
            )

    return problems


# ----------------------------------------------------------------------------
# Helper functions: formatting and HTML
# ----------------------------------------------------------------------------
def H(html):
    """Collapse a multi-line HTML snippet to one line so Markdown can't break it."""
    return "".join(line.strip() for line in html.strip().splitlines())


def fmt_m(value):
    return f"₹{value / 1_000_000:,.2f}M"


def _sign(value):
    return "+" if value > 0 else "-" if value < 0 else ""


def fmt_signed_m(value):
    return f"{_sign(value)}₹{abs(value) / 1_000_000:,.2f}M"


def fmt_signed_inr(value):
    return f"{_sign(value)}₹{abs(value):,.0f}"


def fmt_pct(value):
    return "N/A" if pd.isna(value) else f"{value:,.2f}%"


def status_color(status):
    if status == "Unfavourable":
        return COLOR_RED
    if status == "Favourable":
        return COLOR_GREEN
    return COLOR_AMBER


def section_header(title, subtitle, anchor):
    return H(
        f"""<div id="{anchor}" class="bs-anchor"></div>
        <div class="bs-section-title">{title}</div>
        <div class="bs-section-sub">{subtitle}</div>"""
    )


def kpi_card(label, value, note):
    return H(
        f"""<div class="bs-kpi">
        <div class="bs-kpi-accent"></div>
        <div class="bs-kpi-label">{label}</div>
        <div class="bs-kpi-value">{value}</div>
        <div class="bs-kpi-note">{note}</div>
        </div>"""
    )


def card_title(title, subtitle=""):
    sub = f'<div class="bs-card-sub">{subtitle}</div>' if subtitle else ""
    return H(f'<div class="bs-card-title">{title}</div>{sub}')


def style_chart(fig, height, y_title):
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial", color="#334155", size=12),
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            title=dict(text=""), font=dict(color="#334155", size=12),
        ),
        xaxis=dict(
            title=dict(text=""), showgrid=False, linecolor="#CBD5E1",
            tickfont=dict(color="#475569", size=11),
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color="#475569", size=12)),
            showgrid=True, gridcolor="#E2E8F0",
            zeroline=True, zerolinecolor="#94A3B8",
            tickfont=dict(color="#475569", size=11), tickformat="~s",
        ),
    )
    return fig


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        H(
            """<div class="bs-brand">
            <div class="bs-brand-title">BudgetSense AI</div>
            <div class="bs-brand-sub">Financial Intelligence</div>
            </div>"""
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="bs-side-label">Navigation</div>', unsafe_allow_html=True)
    st.markdown(
        H(
            """<div class="bs-nav">
            <a href="#overview"><span class="ico">▣</span>Executive Overview</a>
            <a href="#analysis"><span class="ico">▣</span>Financial Analysis</a>
            <a href="#watchlist"><span class="ico">▣</span>Variance Watchlist</a>
            <a href="#departments"><span class="ico">▣</span>Department Performance</a>
            <a href="#insights"><span class="ico">▣</span>AI Insights</a>
            <a href="#report"><span class="ico">▣</span>Management Report</a>
            </div>"""
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="bs-side-label">Data Source</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload Dataset",
        type=["xlsx", "csv"],
        label_visibility="collapsed",
        help="Upload an Excel or CSV budget-versus-actual dataset.",
        key="upload_sidebar",
    )
    st.button(
        "📊  Use Sample Data",
        key="sample_sidebar",
        on_click=load_sample,
        use_container_width=True,
    )

    st.markdown('<div class="bs-side-label">System Status</div>', unsafe_allow_html=True)
    status_slot = st.empty()


def render_status():
    """Draw the sidebar status panel from the current app state."""
    ai_done = bool(st.session_state.ai_results)

    validation_map = {
        "ready": ("Ready", "#22C55E"),
        "passed": ("Passed", "#22C55E"),
        "failed": ("Issues found", COLOR_RED),
    }
    analysis_map = {
        "ready": ("Ready", "#22C55E"),
        "complete": ("Complete", "#22C55E"),
        "failed": ("Failed", COLOR_RED),
    }

    rows = [
        ("AI Engine", "Insights generated" if ai_done else "Ready", "#22C55E"),
        ("Validation", *validation_map[SYS["validation"]]),
        ("Analysis Engine", *analysis_map[SYS["analysis"]]),
    ]

    html = "".join(
        f'<div class="bs-status-row">'
        f'<span class="bs-status-dot" style="background:{color}"></span>'
        f'<span class="bs-status-name">{name}</span>'
        f'<span class="bs-status-val">{value}</span></div>'
        for name, value, color in rows
    )
    status_slot.markdown(html, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Handle a newly uploaded file (only once per file)
# ----------------------------------------------------------------------------
if uploaded_file is not None:
    upload_id = (uploaded_file.name, uploaded_file.size)
    if st.session_state.last_upload_id != upload_id:
        st.session_state.last_upload_id = upload_id
        try:
            set_data(read_uploaded_file(uploaded_file), f"Uploaded file: {uploaded_file.name}")
            st.session_state.load_error = None
        except Exception as e:
            st.session_state.df = None
            st.session_state.load_error = f"Could not read the file: {e}"
else:
    st.session_state.last_upload_id = None

df = st.session_state.df

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    H(
        """<div id="overview" class="bs-anchor"></div>
        <div class="bs-header">
        <div>
        <div class="bs-header-eyebrow">Financial Control Room</div>
        <div class="bs-header-title">BudgetSense AI</div>
        <div class="bs-header-subtitle">AI-powered financial variance intelligence for management decision support.</div>
        </div>
        <div class="bs-live"><span class="bs-live-dot"></span>SYSTEM READY</div>
        </div>"""
    ),
    unsafe_allow_html=True,
)

if st.session_state.load_error:
    st.error(st.session_state.load_error)

# ----------------------------------------------------------------------------
# Empty state (no dataset loaded)
# ----------------------------------------------------------------------------
if df is None:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi_card("Total Budget", "—", "Load a dataset to begin"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("Total Actual", "—", "Load a dataset to begin"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Total Variance", "—", "Load a dataset to begin"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Departments", "—", "Load a dataset to begin"), unsafe_allow_html=True)

    st.markdown(
        H(
            """<div class="bs-empty">
            <div class="bs-empty-title">Financial Control Room</div>
            <div class="bs-empty-text">No dataset loaded yet.</div>
            <div class="bs-empty-text">Upload a budget-vs-actual dataset below, or use the sample dataset to activate financial analysis.</div>
            </div>"""
        ),
        unsafe_allow_html=True,
    )

        # Spacer between the Financial Control Room box and the upload row
    st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

    up_col, sample_col = st.columns([2.2, 1], vertical_alignment="center")
    with up_col:
        main_file = st.file_uploader(
            "Upload your Budget vs Actual dataset",
            type=["xlsx", "csv"],
            key="upload_main",
            label_visibility="collapsed",
        )
    with sample_col:
        st.button(
            "📊  Use Sample Data",
            key="sample_main",
            on_click=load_sample,
            use_container_width=True,
        )

    if main_file is not None:
        try:
            set_data(read_uploaded_file(main_file), f"Uploaded file: {main_file.name}")
        except Exception as e:
            st.error(f"Could not read the file: {e}")
        else:
            st.session_state.load_error = None
            st.rerun()

    render_status()
    st.stop()

# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------
problems = validate_dataframe(df)
if problems:
    SYS["validation"] = "failed"
    render_status()
    st.error("❌ Data validation failed. Please fix the following and upload again:")
    for p in problems:
        st.warning(p)
    st.stop()

SYS["validation"] = "passed"

# ----------------------------------------------------------------------------
# Run the financial engine
# ----------------------------------------------------------------------------
try:
    result = run_engine(df)
except Exception as e:
    SYS["analysis"] = "failed"
    render_status()
    st.error(f"The financial engine could not process this data: {e}")
    st.stop()

SYS["analysis"] = "complete"

data = result["data"]
top_variances = result["top_variances"]

# ----------------------------------------------------------------------------
# KPI cards (existing calculations, unchanged)
# ----------------------------------------------------------------------------
total_budget = data["Budget"].sum()
total_actual = data["Actual"].sum()
total_variance = total_actual - total_budget
variance_percentage = (total_variance / total_budget * 100) if total_budget != 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        kpi_card("Total Budget", fmt_m(total_budget), "Sum of all budget lines"),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card("Total Actual", fmt_m(total_actual), "Sum of all actual lines"),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card(
            "Total Variance",
            fmt_signed_m(total_variance),
            f"{_sign(variance_percentage)}{abs(variance_percentage):.2f}% vs budget",
        ),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        kpi_card("Departments", f"{data['Department'].nunique()}", "Included in this analysis"),
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Data source / status strip
# ----------------------------------------------------------------------------
strip_items = [
    ("Data Source", escape(st.session_state.data_source)),
    ("Rows Analysed", f"{len(data):,}"),
    ("Periods", f"{data['Period'].nunique()}"),
    ("Validation", "✓ Passed"),
]
strip_html = "".join(
    f'<div><div class="bs-strip-label">{label}</div>'
    f'<div class="bs-strip-value">{value}</div></div>'
    for label, value in strip_items
)
st.markdown(f'<div class="bs-strip">{strip_html}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Department summary (existing calculation, unchanged)
# ----------------------------------------------------------------------------
department_summary = (
    data.groupby("Department")
    .agg(Budget=("Budget", "sum"), Actual=("Actual", "sum"))
    .reset_index()
)
department_summary["Variance"] = department_summary["Actual"] - department_summary["Budget"]
department_summary["Variance_%"] = department_summary.apply(
    lambda r: (r["Variance"] / r["Budget"] * 100) if r["Budget"] != 0 else float("nan"),
    axis=1,
)

# ----------------------------------------------------------------------------
# Financial analysis: two charts side by side
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "Financial Analysis",
        "Budget against actual spend and the resulting variance, by department.",
        "analysis",
    ),
    unsafe_allow_html=True,
)

chart_left, chart_right = st.columns(2)

with chart_left:
    with st.container(border=True):
        st.markdown(card_title("Budget vs Actual", "By department"), unsafe_allow_html=True)
        chart_data = department_summary.melt(
            id_vars="Department",
            value_vars=["Budget", "Actual"],
            var_name="Measure",
            value_name="Amount",
        )
        fig_budget_actual = px.bar(
            chart_data,
            x="Department",
            y="Amount",
            color="Measure",
            barmode="group",
            color_discrete_map={"Budget": "#64748B", "Actual": "#4338CA"},
        )
        style_chart(fig_budget_actual, height=420, y_title="Amount (₹)")
        st.plotly_chart(fig_budget_actual, width="stretch")

with chart_right:
    with st.container(border=True):
        st.markdown(
            card_title("Variance by Department", "Actual − Budget"),
            unsafe_allow_html=True,
        )
        fig_variance = px.bar(
            department_summary,
            x="Department",
            y="Variance",
            text="Variance",
        )
        fig_variance.update_traces(
            marker_color="#4338CA",
            texttemplate="%{y:.2s}",
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#172554", size=11),
        )
        style_chart(fig_variance, height=420, y_title="Variance (₹)")
        st.plotly_chart(fig_variance, width="stretch")

# ----------------------------------------------------------------------------
# Department performance table
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "Department Performance",
        "Budget, actual and variance for each department.",
        "departments",
    ),
    unsafe_allow_html=True,
)

dept_display = department_summary.copy()
dept_display["Budget"] = dept_display["Budget"].map(lambda v: f"₹{v:,.0f}")
dept_display["Actual"] = dept_display["Actual"].map(lambda v: f"₹{v:,.0f}")
dept_display["Variance"] = dept_display["Variance"].map(fmt_signed_inr)
dept_display["Variance_%"] = dept_display["Variance_%"].map(fmt_pct)
st.dataframe(dept_display, width="stretch", hide_index=True)

# ----------------------------------------------------------------------------
# Variance watchlist (Top 3 material variances)
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "⚠ Variance Watchlist",
        "Top 3 material variances, ranked by absolute rupee impact, not by percentage.",
        "watchlist",
    ),
    unsafe_allow_html=True,
)

watch_rows = ""
for _, row in top_variances.iterrows():
    status = row["Status"]
    color = status_color(status)
    if status == "Unfavourable":
        label = "Material unfavourable variance"
    elif status == "Favourable":
        label = "Favourable variance"
    else:
        label = escape(str(status))

    watch_rows += (
        '<div class="bs-watch-row">'
        f'<div class="bs-dot" style="background:{color}"></div>'
        '<div class="bs-watch-main">'
        f'<div class="bs-watch-name">{escape(str(row["Department"]))} — {escape(str(row["Line_Item"]))}</div>'
        f'<div class="bs-watch-sub">{label} · {escape(str(row["Line_Type"]))} · {fmt_pct(row["Variance_%"])}</div>'
        "</div>"
        f'<div class="bs-watch-val" style="color:{color}">{fmt_signed_inr(row["Variance"])}</div>'
        "</div>"
    )
st.markdown(f'<div class="bs-watch">{watch_rows}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# AI management insights (notes + generation + results)
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "🤖 AI Management Insights",
        "AI-generated explanations for the most material financial variances. "
        "The Python engine supplies the figures; the AI writes the narrative.",
        "insights",
    ),
    unsafe_allow_html=True,
)

analyst_notes = {}

with st.container(border=True):
    st.markdown(
        card_title(
            "Analyst Notes",
            "Add known business drivers. If no driver is provided, the AI will not invent one.",
        ),
        unsafe_allow_html=True,
    )

    note_cols = st.columns(len(top_variances))
    for index, (_, row) in enumerate(top_variances.iterrows()):
        note_key = f"note_{row['Department']}_{row['Line_Item']}_{index}"
        with note_cols[index]:
            analyst_notes[note_key] = st.text_area(
                f"{row['Department']} — {row['Line_Item']}",
                placeholder="Example: Campaign launched earlier than planned.",
                height=90,
                key=note_key,
            )

    generate_ai = st.button("✨ Generate AI Commentary", type="primary")

    if generate_ai:
        st.session_state.ai_results = []

        progress_bar = st.progress(0, text="Starting AI commentary generation...")
        status_box = st.empty()
        results_for_display = []
        total_items = len(top_variances)

        for index, (_, row) in enumerate(top_variances.iterrows()):
            note_key = f"note_{row['Department']}_{row['Line_Item']}_{index}"
            note = analyst_notes.get(note_key, "")

            variance_pct = row["Variance_%"]
            if pd.isna(variance_pct):
                variance_pct = 0.0

            status_box.info(
                f"🤖 Generating commentary {index + 1} of {total_items}: "
                f"{row['Department']} — {row['Line_Item']}"
            )

            try:
                commentary = generate_variance_commentary(
                    department=row["Department"],
                    line_item=row["Line_Item"],
                    line_type=row["Line_Type"],
                    budget=row["Budget"],
                    actual=row["Actual"],
                    variance=row["Variance"],
                    variance_pct=variance_pct,
                    status=row["Status"],
                    analyst_note=note,
                )

                verification = verify_commentary(
                    commentary=commentary,
                    variance=row["Variance"],
                    variance_pct=variance_pct,
                )

                results_for_display.append(
                    {
                        "department": row["Department"],
                        "line_item": row["Line_Item"],
                        "commentary": commentary,
                        "verification": verification,
                    }
                )

            except Exception as e:
                results_for_display.append(
                    {
                        "department": row["Department"],
                        "line_item": row["Line_Item"],
                        "commentary": "",
                        "verification": {"passed": False, "issues": [str(e)]},
                    }
                )

            progress_bar.progress(
                (index + 1) / total_items,
                text=f"Processed {index + 1} of {total_items}",
            )

        st.session_state.ai_results = results_for_display
        progress_bar.empty()
        status_box.success("✅ AI commentary generation and verification completed.")

# Lookup so each insight card can show its variance figure
top_lookup = {
    (str(r["Department"]), str(r["Line_Item"])): r for _, r in top_variances.iterrows()
}

if st.session_state.ai_results:
    for item in st.session_state.ai_results:
        source_row = top_lookup.get((str(item["department"]), str(item["line_item"])))

        var_html = ""
        if source_row is not None:
            color = status_color(source_row["Status"])
            var_html = (
                f'<span class="bs-insight-var" style="color:{color}">'
                f'{fmt_signed_inr(source_row["Variance"])} · {fmt_pct(source_row["Variance_%"])}</span>'
            )

        commentary_html = escape(item["commentary"]).replace("\n", "<br>") if item["commentary"] else ""
        text_html = f'<div class="bs-insight-text">{commentary_html}</div>' if commentary_html else ""

        verification = item["verification"]
        if verification["passed"]:
            verify_html = (
                '<div class="bs-verify ok">✓ Verified against financial calculations</div>'
            )
        else:
            issues = "".join(
                f'<div class="bs-issue">• {escape(str(issue))}</div>'
                for issue in verification.get("issues", [])
            )
            verify_html = (
                '<div class="bs-verify bad">✗ Verification failed — review the AI commentary</div>'
                f"{issues}"
            )

        st.markdown(
            '<div class="bs-insight">'
            '<div class="bs-insight-top">'
            '<span class="bs-tag">AI INSIGHT</span>'
            f"{var_html}"
            "</div>"
            f'<div class="bs-insight-title">{escape(str(item["department"]))} — {escape(str(item["line_item"]))}</div>'
            f"{text_html}"
            f"{verify_html}"
            "</div>",
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<div class="bs-placeholder">No commentary generated yet. '
        "Add optional analyst notes above, then click <b>Generate AI Commentary</b>.</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# Detailed analysis
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "Detailed Financial Analysis",
        "Line-by-line budget, actual, variance and status for the full dataset.",
        "detail",
    ),
    unsafe_allow_html=True,
)

display_columns = [
    "Period", "Department", "Line_Item", "Line_Type",
    "Budget", "Actual", "Variance", "Variance_%", "Status",
]
with st.expander("Show detailed variance table", expanded=False):
    st.dataframe(data[display_columns], width="stretch", hide_index=True)

# ----------------------------------------------------------------------------
# Management report (export)
# ----------------------------------------------------------------------------
st.markdown(
    section_header(
        "📄 Management Report",
        "Generate a management-ready Excel report containing financial analysis, "
        "material variances, AI commentary and detailed data.",
        "report",
    ),
    unsafe_allow_html=True,
)

with st.container(border=True):
    try:
        report_file = create_excel_report(
            data=data,
            department_summary=department_summary,
            top_variances=top_variances,
            ai_results=st.session_state.ai_results,
            analyst_notes=analyst_notes,
            data_source=st.session_state.data_source,
        )

        st.download_button(
            label="📊 Download Management Report",
            data=report_file,
            file_name="BudgetSense_AI_Management_Report.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not create the management report: {e}")

# Final refresh of the sidebar status panel
render_status()