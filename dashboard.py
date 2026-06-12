import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from map import render_district_map

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TN26 Election Analysis",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── AURA NOIR CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Reset & Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #131313 !important;
    color: #e5e2e1 !important;
    font-family: 'Montserrat', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0e0e0e !important;
    border-right: 1px solid #3b494c;
    min-width: 220px !important;
    max-width: 280px !important;
}

[data-testid="stSidebarNav"] {
    display: none !important;  /* hides default page nav if using multipage */
}

/* Ensure sidebar collapse button is visible */
[data-testid="collapsedControl"] {
    color: #c3f5ff !important;
    background-color: #0e0e0e !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #bac9cc !important;
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
}

/* Sidebar collapse/expand toggle button */
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    color: #c3f5ff !important;
    background-color: #1b1b1c !important;
    border: 1px solid #3b494c !important;
    border-radius: 4px !important;
}

/* The arrow icon inside it */
[data-testid="collapsedControl"] svg {
    fill: #c3f5ff !important;
    color: #c3f5ff !important;
}

/* When sidebar is collapsed, the expand button on the left edge */
[data-testid="collapsedControl"] button {
    color: #c3f5ff !important;
    background-color: #1b1b1c !important;
}

/* The floating pill/button that appears when sidebar is collapsed */
section[data-testid="stSidebar"][aria-expanded="false"] ~ div [data-testid="collapsedControl"] {
    background-color: #1b1b1c !important;
    border-color: #3b494c !important;
}

/* Nuclear option — force ALL buttons with SVG arrows visible */
button[kind="header"] {
    color: #c3f5ff !important;
    background: #1b1b1c !important;
    border: 1px solid #3b494c !important;
}
            
/* Sidebar title */
.sidebar-brand {
    font-family: 'Montserrat', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #c3f5ff !important;
    letter-spacing: -0.01em;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid #3b494c;
    margin-bottom: 1.5rem;
}
.sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.08em;
    color: #849396 !important;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
}

/* Main content area */
[data-testid="stMain"] {
    background-color: #131313 !important;
}
.block-container {
    padding: 2rem 2rem 2rem 2rem !important;
    max-width: 1800px;
}

/* Page header */
.page-header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #3b494c;
}
.page-title {
    font-size: 32px;
    font-weight: 600;
    color: #c3f5ff;
    letter-spacing: -0.01em;
    line-height: 1.2;
    margin: 0;
}
.page-subtitle {
    font-size: 14px;
    color: #849396;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.03em;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.kpi-card {
    background: #1b1b1c;
    border: 1px solid #3b494c;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00daf3, transparent);
}
.kpi-card.gold::before { background: linear-gradient(90deg, #e9c400, transparent); }
.kpi-card.neutral::before { background: linear-gradient(90deg, #849396, transparent); }

.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.08em;
    color: #849396;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: #c3f5ff;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-value.gold { color: #ffdb3c; }
.kpi-value.neutral { color: #e5e2e1; }
.kpi-sub {
    font-size: 12px;
    color: #849396;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* Section Cards */
.section-card {
    background: #1b1b1c;
    border: 1px solid #3b494c;
    border-radius: 1px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #bac9cc;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2a2a2a;
}

/* Party chips */
.party-chip {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 500;
}

/* Data table */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.styled-table th {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #ffdb3c;
    background: #202020;
    padding: 0.6rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid #3b494c;
}
.styled-table td {
    padding: 0.55rem 0.75rem;
    color: #e5e2e1;
    border-bottom: 1px solid #2a2a2a;
}
.styled-table tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
.styled-table tr:hover td { background: rgba(0,218,243,0.05); }

/* Selectbox style */
[data-testid="stSelectbox"] > div > div {
    background: #202020 !important;
    border: 1px solid #3b494c !important;
    border-radius: 4px !important;
    color: #e5e2e1 !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Status dot */
.dot-cyan { display:inline-block; width:7px; height:7px; border-radius:50%; background:#00daf3; margin-right:6px; }
.dot-gold { display:inline-block; width:7px; height:7px; border-radius:50%; background:#e9c400; margin-right:6px; }
.dot-grey { display:inline-block; width:7px; height:7px; border-radius:50%; background:#849396; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ───────────────────────────────────────────────────────────────────────

result26 = pd.read_csv("clean_data/tn26_results.csv")
result21 = pd.read_csv("clean_data/tn21_results.csv")

result26['Lead_Party_Name'] = result26['Lead_Party_Name'].replace('AIADMK', 'ADMK')
result26['Trail_Party_Name'] = result26['Trail_Party_Name'].replace('AIADMK', 'ADMK')
result26.loc[56, 'District'] = 'Ariyalur' 
result26.loc[156, 'District'] = 'Ariyalur'

# Seat tally 2026
party_seats_26 = result26['Lead_Party_Name'].value_counts().reset_index()
party_seats_26.columns = ['Party', 'Seats']
party_seats_21 = result21['Winning Party'].value_counts().reset_index()
party_seats_21.columns = ['Party', 'Seats']

party_seats = (
    pd.merge(
        party_seats_21,
        party_seats_26,
        on="Party",
        how="outer",
        suffixes=("_2021", "_2026")
    )
    .fillna(0)
    .astype({"Seats_2021": int, "Seats_2026": int})
)
party_seats["Change"] = party_seats["Seats_2026"] - party_seats["Seats_2021"]

# Vote share 2026
vote_share = pd.read_csv('clean_data/tn26_party_vote_share.csv')

# District-level summary (top districts)
district_data = result26.groupby('District')['Lead_Party_Name'].value_counts().unstack(fill_value=0).reset_index()

# Constituency-level data (sample of notable ones)
constituency_data = result26[['Constituency', 'Lead_Party_Name', 'Trail_Party_Name', 'Margin', 'District']]
constituency_data.columns = ['Constituency', 'Winner', 'Runner', 'Margin', 'District']


# ─── PARTY COLORS ───────────────────────────────────────────────────────────────
PARTY_COLORS = {
    "TVK": "#00daf3",
    "DMK": "#e9c400",
    "ADMK": "#ff6b6b",
    "INC": "#69c0ff",
    "PMK": "#95de64",
    "BJP": "#ff8c00",
    "VCK": "#b37feb",
    "CPI": "#ff85c2",
    "CPI(M)": "#ff85c2",
    "IUML": "#36cfc9",
    "AMMK": "#ffc069",
    "DMDK": "#d3adf7",
    "NTK": "#f759ab",
    "ADMK": "#ff6b6b",
    "NOTA": "#849396",
    "Other": "#849396",
}

def party_color(p):
    return PARTY_COLORS.get(p, "#849396")

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Montserrat, sans-serif", color="#e5e2e1"),
    margin=dict(l=8, r=8, t=32, b=8),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="#3b494c",
        borderwidth=1,
        font=dict(family="JetBrains Mono", size=11, color="#bac9cc"),
    ),
)

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⬡ TN26 ELECTION</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Overview", "Seat Analysis", "Vote Share", "District Breakdown", "Constituency Explorer", "Party Analysis"],
        label_visibility="collapsed",
    )

    st.markdown('<div class="sidebar-section">Filter</div>', unsafe_allow_html=True)
    selected_party = st.selectbox("Focus Party", ["All", "TVK", "DMK", "ADMK", "INC", "PMK", "BJP", "Others"])

    st.markdown("""
    <div style="margin-top:2rem; padding-top:1rem; border-top:1px solid #3b494c;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#849396; letter-spacing:0.05em;">
            DATA SOURCE<br>
            <span style="color:#bac9cc;">TN Election Commission</span><br><br>
            ELECTION DATE<br>
            <span style="color:#bac9cc;">2026 Assembly</span><br><br>
            TOTAL SEATS<br>
            <span style="color:#c3f5ff; font-size:14px; font-weight:600;">234</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── OVERVIEW PAGE ──────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Tamil Nadu 2026 Election Results</div>
        <div class="page-subtitle">ASSEMBLY ELECTION · FINAL RESULTS · 234 CONSTITUENCIES</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Row
    st.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Winning Party</div>
            <div class="kpi-value" style="font-size:28px;">TVK</div>
            <div class="kpi-sub"><span class="dot-cyan"></span>Tamilaga Vettri Kazhagam</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Seats Won — TVK</div>
            <div class="kpi-value">108</div>
            <div class="kpi-sub">of 234 · Simple majority 118</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-label">Total Votes Cast</div>
            <div class="kpi-value gold">4.93Cr</div>
            <div class="kpi-sub"><span class="dot-gold"></span>49.3 million votes</div>
        </div>
        <div class="kpi-card neutral">
            <div class="kpi-label">Parties Winning Seats</div>
            <div class="kpi-value neutral">12</div>
            <div class="kpi-sub"><span class="dot-grey"></span>Across 38 districts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout: seat bar + vote share donut
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Seat Tally — 2026</div>', unsafe_allow_html=True)

        top = party_seats.sort_values("Seats_2026", ascending=True)
        colors = [party_color(p) for p in top["Party"]]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top["Party"],
            x=top["Seats_2026"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=top["Seats_2026"],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color="#e5e2e1"),
            hovertemplate="<b>%{y}</b><br>Seats: %{x}<extra></extra>",
        ))
        # Majority line
        fig.add_vline(x=118, line=dict(color="#ffdb3c", width=1, dash="dot"))
        fig.add_annotation(x=118, y=11.5, text="Majority 118", font=dict(color="#ffdb3c", size=10, family="JetBrains Mono"), showarrow=False, xanchor="left", xshift=4)

        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=340,
            xaxis=dict(showgrid=True, gridcolor="#2a2a2a", gridwidth=1, color="#849396", title="Seats"),
            yaxis=dict(showgrid=False, color="#e5e2e1"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Vote Share 2026</div>', unsafe_allow_html=True)

        top_vs = vote_share.head(8)
        fig2 = go.Figure(go.Pie(
            labels=top_vs["Party"],
            values=top_vs["percentage"],
            hole=0.55,
            marker=dict(colors=[party_color(p) for p in top_vs["Party"]], line=dict(color="#131313", width=2)),
            textinfo="label+percent",
            textfont=dict(family="JetBrains Mono", size=10),
            hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
        ))
        fig2.add_annotation(text="<b>Vote</b><br>Share", x=0.5, y=0.5, showarrow=False,
                            font=dict(color="#c3f5ff", size=13, family="Montserrat"))
        fig2.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Alliance summary
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Alliance Performance</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="styled-table">
        <thead>
            <tr>
                <th>Alliance / Bloc</th>
                <th>Anchor Party</th>
                <th>Seats</th>
                <th>Vote Share</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><span class="dot-cyan"></span>TVK Alliance</td>
                <td><span style="color:#00daf3; font-family:'JetBrains Mono',monospace;">TVK</span></td>
                <td><b>108</b></td>
                <td>36.1%</td>
                <td><span style="color:#00daf3; font-family:'JetBrains Mono',monospace; font-size:11px;">▲ LARGEST PARTY</span></td>
            </tr>
            <tr>
                <td><span class="dot-gold"></span>DMK Alliance</td>
                <td><span style="color:#e9c400; font-family:'JetBrains Mono',monospace;">DMK + INC + CPI + CPI(M) + VCK + IUML</span></td>
                <td><b>72</b></td>
                <td>~30.19%</td>
                <td><span style="color:#e9c400; font-family:'JetBrains Mono',monospace; font-size:11px;">▼ INCUMBENT DEFEAT</span></td>
            </tr>
            <tr>
                <td><span class="dot-grey"></span>ADMK Bloc</td>
                <td><span style="color:#ff6b6b; font-family:'JetBrains Mono',monospace;">ADMK + PMK + AMMK + DMDK + BJP</span></td>
                <td><b>54</b></td>
                <td>~24%</td>
                <td><span style="color:#849396; font-family:'JetBrains Mono',monospace; font-size:11px;">→ OPPOSITION</span></td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── SEAT ANALYSIS PAGE ─────────────────────────────────────────────────────────
elif page == "Seat Analysis":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Seat Analysis</div>
        <div class="page-subtitle">2021 vs 2026 COMPARISON · GAINS & LOSSES</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Seats Won 2021 vs 2026</div>', unsafe_allow_html=True)

        df_cmp = party_seats[party_seats["Seats_2026"] > 0].sort_values("Seats_2026", ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="2021", x=df_cmp["Party"], y=df_cmp["Seats_2021"],
                             marker_color="#849396", opacity=0.6))
        fig.add_trace(go.Bar(name="2026", x=df_cmp["Party"], y=df_cmp["Seats_2026"],
                             marker_color=[party_color(p) for p in df_cmp["Party"]]))
        fig.update_layout(**PLOTLY_LAYOUT, height=320, barmode="group",
                          xaxis=dict(showgrid=False, color="#849396"),
                          yaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Seat Change (2021→2026)</div>', unsafe_allow_html=True)

        df_ch = party_seats.sort_values("Change")
        colors_ch = ["#ff6b6b" if v < 0 else "#00daf3" for v in df_ch["Change"]]
        fig2 = go.Figure(go.Bar(
            y=df_ch["Party"], x=df_ch["Change"], orientation="h",
            marker=dict(color=colors_ch),
            text=[f"{'+' if v > 0 else ''}{v}" for v in df_ch["Change"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color="#e5e2e1"),
        ))
        fig2.add_vline(x=0, line=dict(color="#3b494c", width=1))
        fig2.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False,
                           xaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396"),
                           yaxis=dict(showgrid=False, color="#e5e2e1"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Table
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Complete Seat Breakdown</div>', unsafe_allow_html=True)

    rows = ""
    for _, r in party_seats.sort_values("Seats_2026", ascending=False).iterrows():
        chg = r["Change"]
        chg_color = "#00daf3" if chg > 0 else ("#ff6b6b" if chg < 0 else "#849396")
        chg_str = f"{'+'if chg>0 else ''}{chg}"
        dot_color = party_color(r["Party"])
        rows += f"""
        <tr>
            <td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot_color};margin-right:8px;"></span>{r['Party']}</td>
            <td style="font-family:'JetBrains Mono',monospace; color:#c3f5ff; font-weight:600;">{r['Seats_2026']}</td>
            <td style="font-family:'JetBrains Mono',monospace; color:#849396;">{r['Seats_2021']}</td>
            <td style="font-family:'JetBrains Mono',monospace; color:{chg_color}; font-weight:600;">{chg_str}</td>
        </tr>"""
    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Party</th><th>2026 Seats</th><th>2021 Seats</th><th>Change</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── VOTE SHARE PAGE ─────────────────────────────────────────────────────────────
elif page == "Vote Share":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Vote Share Analysis</div>
        <div class="page-subtitle">PARTY-WISE VOTES POLLED · 2026 ASSEMBLY ELECTION</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3], gap="medium")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Vote Share Distribution</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=vote_share["Party"],
            values=vote_share["percentage"],
            hole=0.5,
            marker=dict(colors=[party_color(p) for p in vote_share["Party"]], line=dict(color="#131313", width=2)),
            textinfo="label",
            textfont=dict(family="JetBrains Mono", size=10),
            hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Vote Share by Party</div>', unsafe_allow_html=True)
        df_vs = vote_share.sort_values("percentage", ascending=True)
        fig2 = go.Figure(go.Bar(
            y=df_vs["Party"], x=df_vs["percentage"],
            orientation="h",
            marker=dict(color=[party_color(p) for p in df_vs["Party"]]),
            text=[f"{v:.2f}%" for v in df_vs["percentage"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#e5e2e1"),
            hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>",
        ))
        fig2.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False,
                           xaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396", ticksuffix="%"),
                           yaxis=dict(showgrid=False, color="#e5e2e1"))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Detailed table
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Detailed Vote Share Table</div>', unsafe_allow_html=True)
    rows = ""
    for _, r in vote_share.iterrows():
        dot = party_color(r["Party"])
        bar_w = int(r["percentage"] / 35 * 150)
        rows += f"""
        <tr>
            <td><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{dot};margin-right:8px;"></span>{r['Party']}</td>
            <td><div style="display:flex;align-items:center;gap:8px;">
                <div style="width:{bar_w}px;height:4px;background:{dot};border-radius:2px;"></div>
                <span style="font-family:'JetBrains Mono',monospace;color:#c3f5ff;">{r['percentage']:.2f}%</span>
            </div></td>
            <td style="font-family:'JetBrains Mono',monospace;color:#bac9cc;">{r['Vote Share']:,}</td>
        </tr>"""
    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Party</th><th>Vote Share</th><th>Total Votes</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── DISTRICT BREAKDOWN PAGE ─────────────────────────────────────────────────────
elif page == "District Breakdown":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">District Breakdown</div>
        <div class="page-subtitle">PARTY PERFORMANCE ACROSS KEY DISTRICTS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Seats by District & Party (Top Districts)</div>', unsafe_allow_html=True)

    df_melt = district_data.melt(id_vars="District", var_name="Party", value_name="Seats")

    fig = go.Figure()

    parties = ["TVK", "DMK", "ADMK", "Others"]

    # Filter parties based on selection
    if selected_party == "All":
        visible_parties = parties
    else:
        visible_parties = [selected_party]

    for party in parties:
        d = df_melt[df_melt["Party"] == party]
        fig.add_trace(go.Bar(
            name=party,
            x=d["District"],
            y=d["Seats"],
            marker_color=party_color(party),
            visible=(party in visible_parties),  # show/hide based on filter
            hovertemplate=f"<b>{party}</b><br>%{{x}}: %{{y}} seats<extra></extra>",
        ))

    fig.update_layout(**PLOTLY_LAYOUT, height=360, barmode="stack",
                    xaxis=dict(showgrid=False, color="#849396"),
                    yaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396", title="Seats"))

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Heatmap
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">District Dominance Map</div>', unsafe_allow_html=True)
    
    if selected_party == "All":
        cols = ["TVK", "DMK", "ADMK"]
    else:
        cols = [selected_party]
    heat_df = district_data.set_index("District")[cols]

    fig2 = go.Figure(go.Heatmap(
        z=heat_df.values,
        x=heat_df.columns.tolist(),
        y=heat_df.index.tolist(),
        colorscale=[[0, "#1b1b1c"], [0.5, "#004f58"], [1, "#00daf3"]],
        text=heat_df.values,
        texttemplate="%{text}",
        textfont=dict(family="JetBrains Mono", size=10),
        hovertemplate="<b>%{y} — %{x}</b><br>%{z} seats<extra></extra>",
        showscale=False,
        xgap=3,   # spacing between columns
        ygap=3,   # spacing between rows
    ))

    layout = {**PLOTLY_LAYOUT, "margin": dict(l=130, r=20, t=10, b=40)}

    fig2.update_layout(
        **layout,
        height=600,
        xaxis=dict(
            color="#bac9cc",
            side="bottom",
            tickfont=dict(family="JetBrains Mono", size=12),
        ),
        yaxis=dict(
            color="#bac9cc",
            tickfont=dict(family="JetBrains Mono", size=11),
            autorange="reversed",
        ),
    )

    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # District choropleth map (Leaflet) from map.py
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">District Choropleth Map</div>', unsafe_allow_html=True)
    try:
        sel = None if selected_party == "All" else selected_party
        render_district_map(result26, selected_party=sel, height=620)
    except Exception as e:
        st.error(f"Failed to render district map: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
# ─── CONSTITUENCY EXPLORER PAGE ──────────────────────────────────────────────────
elif page == "Constituency Explorer":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Constituency Explorer</div>
        <div class="page-subtitle">RESULT DETAILS · MARGINS · HEAD-TO-HEAD</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Notable Constituencies — Victory Margins</div>', unsafe_allow_html=True)

        df_c = constituency_data.dropna(subset=["Margin"])

        # Filter by selected party
        if selected_party != "All":
            df_c = df_c[df_c["Winner"] == selected_party]

        # Top 10 big-margin winners
        df_c = df_c.sort_values("Margin", ascending=False).head(10).sort_values("Margin", ascending=True)

        colors_w = [party_color(p) for p in df_c["Winner"]]

        fig = go.Figure(go.Bar(
            y=df_c["Constituency"],
            x=df_c["Margin"],
            orientation="h",
            marker=dict(color=colors_w),
            text=[f"{int(m):,}" for m in df_c["Margin"]],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#e5e2e1"),
            hovertemplate="<b>%{y}</b><br>Margin: %{x:,}<extra></extra>",
        ))

        fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False,
                        xaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396"),
                        yaxis=dict(showgrid=False, color="#e5e2e1"))

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Closest Contests</div>', unsafe_allow_html=True)

        close = constituency_data.dropna(subset=["Margin"]).sort_values("Margin").head(5)
        rows = ""
        for _, r in close.iterrows():
            wc = party_color(r["Winner"])
            rc = party_color(r["Runner"])
            rows += f"""
            <tr>
                <td style="font-size:12px;">{r['Constituency']}</td>
                <td><span style="color:{wc};font-family:'JetBrains Mono',monospace;font-size:11px;">{r['Winner']}</span></td>
                <td><span style="color:{rc};font-family:'JetBrains Mono',monospace;font-size:11px;">{r['Runner']}</span></td>
                <td style="font-family:'JetBrains Mono',monospace;color:#ffdb3c;font-size:11px;">{int(r['Margin']):,}</td>
            </tr>"""
        st.markdown(f"""
        <table class="styled-table">
            <thead><tr><th>Constituency</th><th>Winner</th><th>Runner</th><th>Margin</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Full table
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">All Constituencies (Sample)</div>', unsafe_allow_html=True)

    # Filter by selected party
    if selected_party == "All":
        filtered = constituency_data
    else:
        filtered = constituency_data[constituency_data["Winner"] == selected_party]

    rows = ""
    for _, r in filtered.sort_values("Margin", ascending=False, na_position='last').iterrows():
        wc = party_color(r["Winner"])
        rc = party_color(r["Runner"])
        margin_str = f"{int(r['Margin']):,}" if pd.notna(r["Margin"]) else "—"
        rows += f"""
        <tr>
            <td style="font-weight:500;">{r['Constituency']}</td>
            <td style="color:#849396;font-size:12px;">{r['District']}</td>
            <td><span style="color:{wc};font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;">{r['Winner']}</span></td>
            <td><span style="color:{rc};font-family:'JetBrains Mono',monospace;font-size:11px;">{r['Runner']}</span></td>
            <td style="font-family:'JetBrains Mono',monospace;color:#c3f5ff;">{margin_str}</td>
        </tr>"""

    # Show empty state if no results
    if not rows:
        rows = f'<tr><td colspan="5" style="text-align:center;color:#849396;padding:20px;">No constituencies found for {selected_party}</td></tr>'

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr><th>Constituency</th><th>District</th><th>Winner</th><th>Runner-up</th><th>Margin</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Party wise analysis PAGE ──────────────────────────────────────────────────

# ─── PARTY WISE ANALYSIS PAGE ────────────────────────────────────────────────
# Drop-in replacement block for dashboard.py
# Paste this after the `elif page == "Constituency Explorer":` block
# Requires: result26, result21, party_seats, vote_share, constituency_data,
#           district_data, PLOTLY_LAYOUT, party_color(), selected_party

elif page == "Party Analysis":

    # ── Resolve selected party (default to TVK if "All" selected) ─────────────
    focus = selected_party if selected_party != "All" else "TVK"
    p_color = party_color(focus)

    # ── Derived data ──────────────────────────────────────────────────────────
    # Seats won
    seats_won = int(result26[result26["Lead_Party_Name"] == focus].shape[0])

    # Total votes polled by party
    total_votes_col = None
    for col in ["Total Votes", "total_votes", "Votes", "Lead_Votes", "Winner_Votes"]:
        if col in result26.columns:
            total_votes_col = col
            break

    if total_votes_col:
        party_votes = int(result26[result26["Lead_Party_Name"] == focus][total_votes_col].sum())
    else:
        # Fallback: use vote_share CSV
        vs_row = vote_share[vote_share["Party"] == focus]
        party_votes = int(vs_row["Vote Share"].values[0]) if not vs_row.empty and "Vote Share" in vs_row.columns else 0

    # Highest seat conversion district
    dist_group = result26[result26["Lead_Party_Name"] == focus].groupby("District").size()
    if not dist_group.empty:
        best_district = dist_group.idxmax()
        best_district_seats = int(dist_group.max())
        dist_total = result26[result26["District"] == best_district].shape[0]
        conversion_pct = round(best_district_seats / dist_total * 100, 1)
    else:
        best_district, best_district_seats, dist_total, conversion_pct = "—", 0, 0, 0.0

    # Vote share %
    vs_row = vote_share[vote_share["Party"] == focus]
    party_vote_pct = f"{vs_row['percentage'].values[0]:.2f}%" if not vs_row.empty else "—"

    # Seat change 2021→2026
    ps_row = party_seats[party_seats["Party"] == focus]
    seats_2021 = int(ps_row["Seats_2021"].values[0]) if not ps_row.empty else 0
    seat_change = seats_won - seats_2021
    chg_sign = "+" if seat_change > 0 else ""

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">Party Analysis</div>
        <div class="page-subtitle">
            <span style="font-family:'JetBrains Mono',monospace; color:{p_color}; font-size:13px;">
                ● {focus}
            </span>
            &nbsp;·&nbsp; IN-DEPTH PERFORMANCE BREAKDOWN · TN 2026
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Row ─────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:2px solid {p_color};">
            <div class="kpi-label">Seats Won</div>
            <div class="kpi-value" style="color:{p_color};">{seats_won}</div>
            <div class="kpi-sub" style="font-family:'JetBrains Mono',monospace;">
                of 234 &nbsp;·&nbsp;
                <span style="color:{'#00daf3' if seat_change >= 0 else '#ff6b6b'};">
                    {chg_sign}{seat_change} vs 2021
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card gold" style="border-top:2px solid #e9c400;">
            <div class="kpi-label">Votes Polled</div>
            <div class="kpi-value gold">
                {f"{party_votes/1e7:.2f}Cr" if party_votes >= 1e7 else f"{party_votes/1e5:.1f}L" if party_votes >= 1e5 else f"{party_votes:,}"}
            </div>
            <div class="kpi-sub">
                <span class="dot-gold"></span>{party_vote_pct} of total vote share
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:2px solid #849396;">
            <div class="kpi-label">Highest Seat Conversion District</div>
            <div class="kpi-value" style="font-size:22px; color:#e5e2e1; margin-top:4px;">
                {best_district}
            </div>
            <div class="kpi-sub">
                {best_district_seats} of {dist_total} seats
                &nbsp;·&nbsp; {conversion_pct}% strike rate
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:2px solid {p_color};">
            <div class="kpi-label">Party</div>
            <div class="kpi-value" style="font-size:30px; color:{p_color}; letter-spacing:-0.01em;">
                {focus}
            </div>
            <div class="kpi-sub">
                <span style="color:{p_color};">●</span>
                {'Tamil Nadu 2026 · Largest Party'
                if seats_won == result26['Lead_Party_Name'].value_counts().iloc[0]
                else 'Tamil Nadu 2026 · Assembly Election'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Row 1: District seat distribution + Win margin distribution ───────────
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Seats Won by District</div>', unsafe_allow_html=True)

        party_by_dist = (
            result26[result26["Lead_Party_Name"] == focus]
            .groupby("District")
            .size()
            .reset_index(name="Seats")
            .sort_values("Seats", ascending=True)
        )

        import re
        def hex_to_rgba(hex_color, alpha=1.0):
            hex_color = hex_color.lstrip("#")
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"rgba({r},{g},{b},{alpha})"

        fig_dist = go.Figure(go.Bar(
            y=party_by_dist["District"],
            x=party_by_dist["Seats"],
            orientation="h",
            marker=dict(
                color=party_by_dist["Seats"],
                colorscale=[[0, "#1b1b1c"], [0.4, hex_to_rgba(p_color, 0.5)], [1, p_color]],
                showscale=False,
            ),
            text=party_by_dist["Seats"],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#e5e2e1"),
            hovertemplate="<b>%{y}</b><br>%{x} seats<extra></extra>",
        ))
        fig_dist.update_layout(
            **PLOTLY_LAYOUT,
            height=max(300, len(party_by_dist) * 28),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396"),
            yaxis=dict(showgrid=False, color="#e5e2e1"),
        )
        st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Victory Margin Distribution</div>', unsafe_allow_html=True)

        margins = constituency_data[
            constituency_data["Winner"] == focus
        ]["Margin"].dropna()

        if not margins.empty:
            fig_margin = go.Figure(go.Histogram(
                x=margins,
                nbinsx=20,
                marker=dict(
                    color=p_color,
                    opacity=0.8,
                    line=dict(color="#131313", width=1),
                ),
                hovertemplate="Margin %{x:,.0f}–%{x:,.0f}<br>%{y} seats<extra></extra>",
            ))
            fig_margin.update_layout(
                **PLOTLY_LAYOUT,
                height=300,
                showlegend=False,
                xaxis=dict(showgrid=False, color="#849396", title="Margin (votes)"),
                yaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396", title="Constituencies"),
            )
            # Median line
            fig_margin.add_vline(
                x=margins.median(),
                line=dict(color="#ffdb3c", width=1, dash="dot"),
                annotation_text=f"  median {int(margins.median()):,}",
                annotation_font=dict(family="JetBrains Mono", size=10, color="#ffdb3c"),
            )
            st.plotly_chart(fig_margin, use_container_width=True, config={"displayModeBar": False})

            # Quick stats
            stats_html = f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-top:0.5rem;">
                <div style="background:#202020; border-radius:6px; padding:0.6rem 0.8rem;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#849396; text-transform:uppercase; letter-spacing:.06em;">Avg margin</div>
                    <div style="font-size:16px; font-weight:700; color:{p_color}; font-family:'JetBrains Mono',monospace;">{int(margins.mean()):,}</div>
                </div>
                <div style="background:#202020; border-radius:6px; padding:0.6rem 0.8rem;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#849396; text-transform:uppercase; letter-spacing:.06em;">Max margin</div>
                    <div style="font-size:16px; font-weight:700; color:#e9c400; font-family:'JetBrains Mono',monospace;">{int(margins.max()):,}</div>
                </div>
                <div style="background:#202020; border-radius:6px; padding:0.6rem 0.8rem;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#849396; text-transform:uppercase; letter-spacing:.06em;">Min margin</div>
                    <div style="font-size:16px; font-weight:700; color:#ff6b6b; font-family:'JetBrains Mono',monospace;">{int(margins.min()):,}</div>
                </div>
                <div style="background:#202020; border-radius:6px; padding:0.6rem 0.8rem;">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#849396; text-transform:uppercase; letter-spacing:.06em;">Seats &lt;5k margin</div>
                    <div style="font-size:16px; font-weight:700; color:#ff6b6b; font-family:'JetBrains Mono',monospace;">{int((margins < 5000).sum())}</div>
                </div>
            </div>
            """
            PARTY_NOTES = {
            "TVK": (
                f"Dominated by TVK's sweeping victory in 2026, the party showcased a mix of landslide wins and tight contests. "
                f"{best_district} was landslide territory for TVK where it secured {best_district_seats} seats out of 19 in the district.  "
                f"The average victory margin of around {int(margins.mean()):,} votes reflects a blend of strongholds and competitive battlegrounds. "  
                f"Vijay pre poll campaigned region performed exceptionally well, that made TVK to secure winning seats in that detricts"
            ), 
            "DMK": (
                f"The DMK faced a challenging election cycle in 2026, experiencing losses across several regions. "
                f"While retaining some traditional strongholds, it lost ground in key urban constituencies where voter sentiment shifted. "
                f"The average margin was around {int(margins.mean()):,} votes. "
                f"16 Ex-DMK Ministers including former Chief Minister MK Stalin lost their seats — a clear signal of anti-incumbency "
                f"driven by concerns over law and order, the drug menace, misuse of power, and corruption."
            ),
            "ADMK": (
                f"The ADMK's 2026 performance was mixed — securing wins in traditional bastions while facing stiff competition elsewhere. "
                f"With TVK's emergence, the 55-year-old party was pushed to third place in both vote share and seat count. "
                f"The average victory margin was around {int(margins.mean()):,} votes. "
                f"The BJP alliance also failed to deliver meaningful gains in seats or vote share."
            ),
        }

            note = PARTY_NOTES.get(focus, "No analysis available for this party.")

            st.markdown(stats_html + f"""
            <div style="margin-top:0.75rem;background:#202020;border-radius:6px;border-left:4px solid {p_color};padding:0.8rem;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#849396;text-transform:uppercase;letter-spacing:.08em;margin-bottom:0.4rem;">
                    Party Insight
                </div>
                <div style="color:#e5e2e1;font-size:13px;line-height:1.6;">
                    {note}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#849396; font-family:JetBrains Mono, monospace; font-size:13px; padding:2rem 0; text-align:center;">No margin data available</div>', unsafe_allow_html=True)


    # ── Row 2: Head-to-head rivalries + Closest contests ─────────────────────
    col3, col4 = st.columns([2, 3], gap="medium")

    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Main Rivals Faced</div>', unsafe_allow_html=True)

        # Where this party won, who was runner up?
        rivals_won = constituency_data[constituency_data["Winner"] == focus]["Runner"].value_counts().head(8)
        # Where this party was runner up, who beat them?
        rivals_lost = constituency_data[constituency_data["Runner"] == focus]["Winner"].value_counts().head(8)

        rivals_combined = pd.concat([
            rivals_won.rename("Won Against"),
            rivals_lost.rename("Lost To"),
        ], axis=1).fillna(0).astype(int)
        rivals_combined = rivals_combined[rivals_combined.index != focus]
        rivals_combined["Total"] = rivals_combined["Won Against"] + rivals_combined["Lost To"]
        rivals_combined = rivals_combined.sort_values("Total", ascending=False).head(6)

        if not rivals_combined.empty:
            rows_rival = ""
            for party, r in rivals_combined.iterrows():
                rc = party_color(str(party))
                won_bar = int(r["Won Against"] / (rivals_combined["Won Against"].max() or 1) * 60)
                lost_bar = int(r["Lost To"] / (rivals_combined["Lost To"].max() or 1) * 60)
                rows_rival += f"""
                <tr>
                    <td>
                        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                              background:{rc};margin-right:6px;"></span>
                        <span style="color:#e5e2e1; font-size:12px;">{party}</span>
                    </td>
                    <td>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <div style="width:{won_bar}px; height:4px; background:{p_color}; border-radius:2px;"></div>
                            <span style="font-family:'JetBrains Mono',monospace; color:{p_color}; font-size:11px;">{r['Won Against']}</span>
                        </div>
                    </td>
                    <td>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <div style="width:{lost_bar}px; height:4px; background:#ff6b6b; border-radius:2px;"></div>
                            <span style="font-family:'JetBrains Mono',monospace; color:#ff6b6b; font-size:11px;">{r['Lost To']}</span>
                        </div>
                    </td>
                </tr>"""
            st.markdown(f"""
            <table class="styled-table">
                <thead>
                    <tr>
                        <th>Party</th>
                        <th style="color:{p_color};">Won Against</th>
                        <th style="color:#ff6b6b;">Lost To</th>
                    </tr>
                </thead>
                <tbody>{rows_rival}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#849396; text-align:center; padding:1rem; font-family:JetBrains Mono, monospace; font-size:12px;">No rivalry data</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Closest Contests — Wins & Near Misses</div>', unsafe_allow_html=True)

        # Tightest wins
        tight_wins = (
            constituency_data[constituency_data["Winner"] == focus]
            .dropna(subset=["Margin"])
            .sort_values("Margin")
            .head(5)
        )
        # Near misses (where focus party was runner up, lost narrowly)
        near_miss = (
            constituency_data[constituency_data["Runner"] == focus]
            .dropna(subset=["Margin"])
            .sort_values("Margin")
            .head(5)
        )

        rows_tight = ""
        if not tight_wins.empty:
            for _, r in tight_wins.iterrows():
                rc = party_color(r["Runner"])
                rows_tight += f"""
                <tr>
                    <td style="font-size:12px;">{r['Constituency']}</td>
                    <td style="color:#849396; font-size:11px;">{r['District']}</td>
                    <td><span style="color:{rc}; font-family:'JetBrains Mono',monospace; font-size:11px;">{r['Runner']}</span></td>
                    <td style="font-family:'JetBrains Mono',monospace; color:{p_color}; font-size:11px;">✓ {int(r['Margin']):,}</td>
                </tr>"""

        rows_miss = ""
        if not near_miss.empty:
            for _, r in near_miss.iterrows():
                wc = party_color(r["Winner"])
                rows_miss += f"""
                <tr>
                    <td style="font-size:12px;">{r['Constituency']}</td>
                    <td style="color:#849396; font-size:11px;">{r['District']}</td>
                    <td><span style="color:{wc}; font-family:'JetBrains Mono',monospace; font-size:11px;">{r['Winner']}</span></td>
                    <td style="font-family:'JetBrains Mono',monospace; color:#ff6b6b; font-size:11px;">✗ {int(r['Margin']):,}</td>
                </tr>"""

        if rows_tight:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace; font-size:10px; color:{p_color}; text-transform:uppercase; letter-spacing:.06em; margin-bottom:.4rem;">Narrowest Wins</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table class="styled-table" style="margin-bottom:1rem;">
                <thead><tr><th>Constituency</th><th>District</th><th>Runner</th><th>Margin</th></tr></thead>
                <tbody>{rows_tight}</tbody>
            </table>""", unsafe_allow_html=True)

        if rows_miss:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace; font-size:10px; color:#ff6b6b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:.4rem; margin-top:.75rem;">Near Misses</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table class="styled-table">
                <thead><tr><th>Constituency</th><th>District</th><th>Winner</th><th>Margin</th></tr></thead>
                <tbody>{rows_miss}</tbody>
            </table>""", unsafe_allow_html=True)

        if not rows_tight and not rows_miss:
            st.markdown('<div style="color:#849396; text-align:center; padding:1rem; font-family:JetBrains Mono, monospace; font-size:12px;">No contest data available</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: 2021→2026 Comparison + Full constituency list ──────────────────
    col5, col6 = st.columns([1, 2], gap="medium")

    with col5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">2021 vs 2026 Performance</div>', unsafe_allow_html=True)

        cmp_df = party_seats[party_seats["Party"] == focus]
        if not cmp_df.empty:
            s21 = int(cmp_df["Seats_2021"].values[0])
            s26 = seats_won
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(
                x=["2021", "2026"],
                y=[s21, s26],
                marker=dict(
                    color=["#849396", p_color],
                    line=dict(color="#131313", width=2),
                ),
                text=[str(s21), str(s26)],
                textposition="outside",
                textfont=dict(family="JetBrains Mono", size=14, color="#e5e2e1"),
                width=0.4,
            ))
            fig_cmp.update_layout(
                **PLOTLY_LAYOUT,
                height=240,
                showlegend=False,
                xaxis=dict(showgrid=False, color="#849396"),
                yaxis=dict(showgrid=True, gridcolor="#2a2a2a", color="#849396"),
            )
            st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

            chg_color = "#00daf3" if seat_change >= 0 else "#ff6b6b"
            st.markdown(f"""
            <div style="text-align:center; margin-top:.5rem;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:11px; color:#849396;">Net seat change</span><br>
                <span style="font-size:28px; font-weight:700; color:{chg_color}; font-family:'JetBrains Mono',monospace;">
                    {chg_sign}{seat_change}
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#849396; font-size:12px; font-family:JetBrains Mono, monospace; text-align:center; padding:1rem;">No 2021 data for this party</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">All {focus} Wins — Constituency List</div>', unsafe_allow_html=True)

        party_wins = constituency_data[constituency_data["Winner"] == focus].sort_values("Margin", ascending=False, na_position="last")

        rows_all = ""
        for i, (_, r) in enumerate(party_wins.iterrows()):
            rc = party_color(r["Runner"])
            margin_str = f"{int(r['Margin']):,}" if pd.notna(r["Margin"]) else "—"
            rows_all += f"""
            <tr>
                <td style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#849396; width:28px;">{i+1}</td>
                <td style="font-size:12px; font-weight:500;">{r['Constituency']}</td>
                <td style="color:#849396; font-size:11px;">{r['District']}</td>
                <td><span style="color:{rc}; font-family:'JetBrains Mono',monospace; font-size:11px;">{r['Runner']}</span></td>
                <td style="font-family:'JetBrains Mono',monospace; color:#c3f5ff; font-size:11px;">{margin_str}</td>
            </tr>"""

        if not rows_all:
            rows_all = f'<tr><td colspan="5" style="text-align:center; color:#849396; padding:1.5rem; font-family:JetBrains Mono, monospace; font-size:12px;">No wins found for {focus}</td></tr>'

        st.markdown(f"""
        <div style="max-height:340px; overflow-y:auto; scrollbar-width:thin; scrollbar-color:#3b494c #1b1b1c;">
        <table class="styled-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Constituency</th>
                    <th>District</th>
                    <th>Runner-up</th>
                    <th>Margin</th>
                </tr>
            </thead>
            <tbody>{rows_all}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)