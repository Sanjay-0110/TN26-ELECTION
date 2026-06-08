"""
Tamil Nadu District Choropleth Map  –  Aura Noir theme
-------------------------------------------------------
Drop this file + tn_simplified.geojson into your project and call:

    from tn_district_map import render_district_map
    render_district_map(df, selected_party=None)

df must have columns: district, constituency, party, votes, winner
"""

import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path

# ── Party colours ──────────────────────────────────────────────────────────────
PARTY_COLORS = {
    "TVK":    "#00daf3",
    "DMK":    "#e9c400",
    "AIADMK": "#ff6b6b",
    "INC":    "#69c0ff",
    "PMK":    "#95de64",
    "BJP":    "#ff8c00",
    "VCK":    "#b37feb",
    "CPI":    "#ff85c2",
    "CPI(M)": "#ff85c2",
    "IUML":   "#36cfc9",
    "AMMK":   "#ffc069",
    "DMDK":   "#d3adf7",
    "NTK":    "#f759ab",
    "ADMK":   "#ff6b6b",
    "NOTA":   "#849396",
    "Other":  "#849396",
}
DEFAULT_COLOR = "#849396"

# ── GeoJSON district name → your data's spelling ──────────────────────────────
_NAME_FIXES = {
    "Kanniyakumari": "Kanyakumari",
    "The Nilgiris":  "Nilgiris",
    "Tuticorin":     "Thoothukudi",
    "Kanchipuram": "Kancheepuram",
    "Villupuram": "Viluppuram"
}

def _norm(name: str) -> str:
    return _NAME_FIXES.get(name, name)


# ── Core render function ───────────────────────────────────────────────────────
def render_district_map(
    df: pd.DataFrame,
    selected_party: str | None = None,
    height: int = 600,
):
    """
    Render an Aura-Noir styled interactive Tamil Nadu choropleth map.

    Each district is coloured by the party that won the most constituencies
    there. If `selected_party` is set, other districts are greyed out.

    Parameters
    ----------
    df             : DataFrame with columns district, constituency, party, winner
    selected_party : Highlight one party; None = show all
    height         : Map height in px
    """

    # 1. Winning row per constituency
    # Normalize input DataFrame column names to expected names ('district','party','constituency','winner')
    col_lower_map = {c.strip().lower(): c for c in df.columns}
    def _find(*names):
      for n in names:
        if n in col_lower_map:
          return col_lower_map[n]
      return None

    district_col = _find('district')
    party_col = _find('party', 'lead_party_name', 'trail_party_name', 'lead_party', 'party_name')
    const_col = _find('constituency', 'constituency_name')
    winner_col = _find('winner', 'is_winner')

    rename_map = {}
    if district_col and district_col != 'district':
      rename_map[district_col] = 'district'
    if party_col and party_col != 'party':
      rename_map[party_col] = 'party'
    if const_col and const_col != 'constituency':
      rename_map[const_col] = 'constituency'
    if winner_col and winner_col != 'winner':
      rename_map[winner_col] = 'winner'
    if rename_map:
      df = df.rename(columns=rename_map)

    # create a boolean 'winner' column if none exists but a party column does
    if 'winner' not in df.columns and 'party' in df.columns:
      df['winner'] = df['party'].astype(bool)

    winners = df[df['winner'].astype(bool)].copy()

    # 2. Seat count per district × party
    dist_party = (
        winners.groupby(["district", "party"])
        .size()
        .reset_index(name="seats")
    )

    # 3. Dominant party per district
    idx      = dist_party.groupby("district")["seats"].idxmax()
    dominant = dist_party.loc[idx].set_index("district")

    # 4. Full breakdown per district
    dist_summary = (
        winners.groupby(["district", "party"])
        .size()
        .reset_index(name="seats")
    )
    total_by_dist = winners.groupby("district").size().reset_index(name="total")

    # ── Load & colour GeoJSON ─────────────────────────────────────────────────
    geojson_path = "C:/Code Note/TN26-ELECTION/tn_simplified.geojson"
    with open(geojson_path) as f:
        geo = json.load(f)

    features_out = []
    for feat in geo["features"]:
        geo_name  = feat["properties"]["district"]
        data_name = _norm(geo_name)

        if data_name in dominant.index:
            row   = dominant.loc[data_name]
            party = row["party"]
            seats = int(row["seats"])
            tot_rows = total_by_dist[total_by_dist["district"] == data_name]["total"].values
            total = int(tot_rows[0]) if len(tot_rows) else seats
            color = PARTY_COLORS.get(party, DEFAULT_COLOR)

            bd_rows   = dist_summary[dist_summary["district"] == data_name]
            breakdown = "|".join(f"{r.party}:{r.seats}" for r in bd_rows.itertuples())

            opacity = 0.82
            border  = "#131313"
            if selected_party and party != selected_party:
                color   = "#2a2a2a"
                opacity = 0.6
                border  = "#1b1b1c"
        else:
            party     = "No data"
            seats     = 0
            total     = 0
            color     = "#1e1e1e"
            opacity   = 0.5
            border    = "#1b1b1c"
            breakdown = ""

        features_out.append({
            **feat,
            "properties": {
                "district":  data_name,
                "party":     party,
                "seats":     seats,
                "total":     total,
                "color":     color,
                "opacity":   opacity,
                "border":    border,
                "breakdown": breakdown,
            }
        })

    geo_colored = json.dumps({"type": "FeatureCollection", "features": features_out})

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_parties = dominant["party"].value_counts().reset_index()
    legend_parties.columns = ["party", "districts"]
    legend_items = "".join(
        f'''<div class="legend-row">
              <div class="legend-dot" style="background:{PARTY_COLORS.get(p, DEFAULT_COLOR)}"></div>
              <span class="legend-party">{p}</span>
              <span class="legend-count">{d}d</span>
            </div>'''
        for p, d in zip(legend_parties["party"], legend_parties["districts"])
    )

    # ── HTML/Leaflet ──────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
  /* ── Reset ── */
  * {{ margin:0; padding:0; box-sizing:border-box; }}

  body {{
    background:#131313;
    font-family:'Montserrat', sans-serif;
  }}

  #map {{
    width:100%;
    height:{height}px;
    background:#131313;
  }}

  /* ── Popup wrapper ── */
  .leaflet-popup-content-wrapper {{
    background:#1b1b1c;
    border:1px solid #3b494c;
    border-radius:4px;
    box-shadow:0 8px 32px rgba(0,0,0,0.7);
    padding:0;
  }}
  .leaflet-popup-content {{
    margin:0;
    line-height:1;
  }}
  .leaflet-popup-tip-container {{ display:none; }}
  .leaflet-popup-close-button {{ display:none !important; }}

  /* ── Popup inner ── */
  .popup-inner {{
    min-width:200px;
    padding:14px 16px;
  }}
  .popup-district {{
    font-family:'Montserrat', sans-serif;
    font-size:14px;
    font-weight:700;
    color:#c3f5ff;
    letter-spacing:-0.01em;
    margin-bottom:8px;
  }}
  .popup-badge {{
    display:inline-block;
    padding:2px 10px;
    border-radius:9999px;
    font-family:'JetBrains Mono', monospace;
    font-size:11px;
    font-weight:500;
    color:#000;
    margin-bottom:10px;
  }}
  .popup-divider {{
    height:1px;
    background:#2a2a2a;
    margin:8px 0;
  }}
  .popup-meta {{
    font-family:'JetBrains Mono', monospace;
    font-size:10px;
    letter-spacing:0.05em;
    text-transform:uppercase;
    color:#849396;
    margin-bottom:3px;
  }}
  .popup-meta span {{
    color:#e5e2e1;
    font-weight:600;
    font-size:11px;
  }}
  .breakdown-label {{
    font-family:'JetBrains Mono', monospace;
    font-size:9px;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:#849396;
    margin:8px 0 4px 0;
  }}
  .breakdown-row {{
    display:flex;
    align-items:center;
    gap:6px;
    margin-bottom:3px;
  }}
  .breakdown-dot {{
    width:6px; height:6px;
    border-radius:50%;
    flex-shrink:0;
  }}
  .breakdown-text {{
    font-family:'JetBrains Mono', monospace;
    font-size:10px;
    color:#bac9cc;
  }}

  /* ── Legend ── */
  #legend {{
    position:absolute;
    bottom:20px;
    right:12px;
    z-index:1000;
    background:rgba(27,27,28,0.95);
    border:1px solid #3b494c;
    border-radius:4px;
    padding:12px 14px;
    max-height:280px;
    overflow-y:auto;
    backdrop-filter:blur(8px);
    scrollbar-width:thin;
    scrollbar-color:#3b494c transparent;
  }}
  .legend-title {{
    font-family:'JetBrains Mono', monospace;
    font-size:9px;
    font-weight:500;
    letter-spacing:0.08em;
    text-transform:uppercase;
    color:#849396;
    margin-bottom:10px;
    padding-bottom:6px;
    border-bottom:1px solid #2a2a2a;
  }}
  .legend-row {{
    display:flex;
    align-items:center;
    gap:7px;
    margin-bottom:6px;
  }}
  .legend-dot {{
    width:9px; height:9px;
    border-radius:2px;
    flex-shrink:0;
  }}
  .legend-party {{
    font-family:'JetBrains Mono', monospace;
    font-size:11px;
    color:#e5e2e1;
    flex:1;
  }}
  .legend-count {{
    font-family:'JetBrains Mono', monospace;
    font-size:10px;
    color:#849396;
  }}

  /* ── Zoom controls ── */
  .leaflet-control-zoom {{
    border:none !important;
    box-shadow:none !important;
  }}
  .leaflet-control-zoom a {{
    background:#1b1b1c !important;
    color:#bac9cc !important;
    border:1px solid #3b494c !important;
    border-radius:4px !important;
    width:28px !important;
    height:28px !important;
    line-height:28px !important;
    font-size:16px !important;
    margin-bottom:3px !important;
    display:block !important;
    text-align:center;
    transition:background 0.15s;
  }}
  .leaflet-control-zoom a:hover {{
    background:#232323 !important;
    color:#c3f5ff !important;
  }}
  .leaflet-control-attribution {{ display:none; }}

  /* district label tooltip */
  .dist-label {{
    background:transparent;
    border:none;
    box-shadow:none;
    font-family:'JetBrains Mono', monospace;
    font-size:9px;
    color:#849396;
    white-space:nowrap;
    pointer-events:none;
  }}
</style>
</head>
<body>
<div id="map"></div>
<div id="legend">
  <div class="legend-title">Party · Districts</div>
  {legend_items}
</div>

<script>
const PARTY_COLORS = {json.dumps(PARTY_COLORS)};
const geojsonData  = {geo_colored};

const map = L.map('map', {{
  center:[11.0, 78.6],
  zoom:7,
  zoomControl:true,
  attributionControl:false,
  preferCanvas:true,
}});

// Carto dark (no labels) — matches #131313 base
L.tileLayer(
  'https://{{s}}.basemaps.cartocdn.com/dark_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png',
  {{ maxZoom:12, minZoom:5 }}
).addTo(map);

let activeLayer = null;

function baseStyle(feat) {{
  return {{
    fillColor:   feat.properties.color,
    fillOpacity: feat.properties.opacity,
    color:       feat.properties.border,
    weight:      1.2,
    opacity:     1,
  }};
}}

function hoverStyle(feat) {{
  return {{
    fillColor:   feat.properties.color,
    fillOpacity: Math.min(feat.properties.opacity + 0.12, 1),
    color:       '#3b494c',
    weight:      2,
    opacity:     1,
  }};
}}

function activeStyle(feat) {{
  return {{
    fillColor:   feat.properties.color,
    fillOpacity: 1,
    color:       '#c3f5ff',
    weight:      2.5,
    opacity:     1,
  }};
}}

function buildPopup(p) {{
  const bdColor = PARTY_COLORS[p.party] || '#849396';

  let bdHtml = '';
  if (p.breakdown) {{
    const rows = p.breakdown.split('|').map(s => {{
      const [party, seats] = s.split(':');
      const col = PARTY_COLORS[party] || '#849396';
      return `<div class="breakdown-row">
                <div class="breakdown-dot" style="background:${{col}}"></div>
                <span class="breakdown-text">${{party}} &nbsp;·&nbsp; ${{seats}} seat${{seats!='1'?'s':''}}</span>
              </div>`;
    }}).join('');
    bdHtml = `<div class="breakdown-label">Seat breakdown</div>${{rows}}`;
  }}

  return `<div class="popup-inner">
    <div class="popup-district">${{p.district}}</div>
    <div class="popup-badge" style="background:${{bdColor}}">${{p.party}}</div>
    <div class="popup-meta">Leading seats &nbsp;<span>${{p.seats}}</span></div>
    <div class="popup-meta">Total seats &nbsp;<span>${{p.total}}</span></div>
    ${{bdHtml ? '<div class="popup-divider"></div>' + bdHtml : ''}}
  </div>`;
}}

function onEachFeature(feat, layer) {{
  const p = feat.properties;

  layer.on('mouseover', function() {{
    if (layer !== activeLayer) layer.setStyle(hoverStyle(feat));
  }});

  layer.on('mouseout', function() {{
    if (layer !== activeLayer) layer.setStyle(baseStyle(feat));
  }});

  layer.on('click', function(e) {{
    if (activeLayer && activeLayer !== layer) {{
      activeLayer.setStyle(baseStyle(activeLayer.feature));
      activeLayer.closePopup();
    }}
    activeLayer = layer;
    layer.setStyle(activeStyle(feat));

    layer.bindPopup(buildPopup(p), {{
      closeButton: false,
      offset: [0, 0],
      className: 'aura-popup',
    }}).openPopup(e.latlng);
  }});

  map.on('click', function(e) {{
    if (!e.originalEvent._layerClick) {{
      if (activeLayer) {{
        activeLayer.setStyle(baseStyle(activeLayer.feature));
        activeLayer.closePopup();
        activeLayer = null;
      }}
    }}
  }});

  layer.on('click', function(e) {{ e.originalEvent._layerClick = true; }});
}}

const geoLayer = L.geoJSON(geojsonData, {{
  style:          baseStyle,
  onEachFeature:  onEachFeature,
}}).addTo(map);

// fit bounds to TN
map.fitBounds(geoLayer.getBounds(), {{ padding:[16,16] }});
</script>
</body>
</html>"""

    components.html(html, height=height, scrolling=False)


# ── Standalone demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import random
    random.seed(42)

    st.set_page_config(page_title="TN District Map", layout="wide")

    # Aura Noir page chrome
    st.markdown("""
    <style>
    html,body,[data-testid="stAppViewContainer"]{background:#131313!important;color:#e5e2e1!important;font-family:'Montserrat',sans-serif}
    [data-testid="stMain"]{background:#131313!important}
    .block-container{padding:2rem!important;max-width:1800px}
    #MainMenu,footer,header{visibility:hidden}
    [data-testid="stToolbar"]{display:none}
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #3b494c">
      <div style="font-size:28px;font-weight:700;color:#c3f5ff;letter-spacing:-0.01em">Tamil Nadu District Map</div>
      <div style="font-size:12px;color:#849396;margin-top:4px;font-family:'JetBrains Mono',monospace;letter-spacing:.03em">
        District coloured by dominant party · click a district for details
      </div>
    </div>""", unsafe_allow_html=True)

    parties = ["DMK","ADMK","BJP","INC","VCK","PMK","TVK","NTK"]
    weights = [0.38, 0.25,    0.07, 0.10, 0.06, 0.05, 0.07, 0.02]
    districts = [
        "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore",
        "Dharmapuri","Dindigul","Erode","Kallakurichi","Kanniyakumari",
        "Karur","Krishnagiri","Madurai","Mayiladuthurai","Nagapattinam",
        "Namakkal","Nilgiris","Perambalur","Pudukkottai","Ramanathapuram",
        "Ranipet","Salem","Sivaganga","Tenkasi","Thanjavur",
        "Theni","Thiruvallur","Thiruvarur","Tiruchirappalli","Tirunelveli",
        "Tirupattur","Tiruppur","Tiruvannamalai","Thoothukudi","Vellore",
        "Viluppuram","Virudhunagar",
    ]

    # rows = []
    # for dist in districts:
    #     n = random.randint(3, 12)
    #     wp = random.choices(parties, weights=weights)[0]
    #     for i in range(n):
    #         p = wp if i == 0 else random.choices(parties, weights=weights)[0]
    #         rows.append(dict(district=dist, constituency=f"{dist}_{i+1}",
    #                          party=p, votes=random.randint(30000,120000), winner=(i==0)))

    df = pd.read_csv("C:/Code Note/TN26-ELECTION/clean_data/tn26_results.csv")
    # print(df.head())
    df['Lead_Party_Name'] = df['Lead_Party_Name'].replace('AIADMK', 'ADMK')
    df.loc[56, 'District'] = 'Ariyalur' 
    df.loc[156, 'District'] = 'Ariyalur'
    print(df.loc[56])
    print(df.loc[156])
    all_parties = sorted(df['Lead_Party_Name'].unique())

    # print(all_parties)

    col1, col2 = st.columns([5, 1])
    with col2:
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#849396;margin-bottom:6px">Filter party</div>', unsafe_allow_html=True)
        choice = st.selectbox("", ["All parties"] + all_parties, label_visibility="collapsed")

    selected = None if choice == "All parties" else choice
    render_district_map(df, selected_party=selected, height=620)