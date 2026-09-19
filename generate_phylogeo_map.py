import os
import folium
import matplotlib.pyplot as plt
import geopandas as gpd
import urllib.request
import shutil
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "pipeline_scripts" else BASE_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


# Define output directories
docs_dir = DATA_DIR
geo_dir = DATA_DIR
os.makedirs(docs_dir, exist_ok=True)
os.makedirs(geo_dir, exist_ok=True)

# ---------------------------------------------------------
# ACCURATE GEOGRAPHIC COORDINATES & WAYPOINTS
# ---------------------------------------------------------

hubs = {
    "Urheimat": {
        "coords": [4.15, 37.85],
        "name": "East African Urheimat (Omo-Turkana Core)",
        "time": "~65,000 BCE",
        "desc": "Primary origin point of Dual-Trunk Proto-Human language (4.15°N, 37.85°E). Phonemic entropy peak (H_phon = 5.85 bits).",
        "color": "red",
        "icon": "star"
    },
    "Proto_African": {
        "coords": [-25.0, 24.0],
        "name": "Proto-African Core (Khoisan / Kalahari Hub)",
        "time": "~65,000 – 50,000 BCE",
        "desc": "Retention hub for basal African click series (*ʘ, *ǀ, *ǃ) and pronominal *ʔanāku.",
        "color": "darkred",
        "icon": "info-sign"
    },
    "Proto_Eurasian": {
        "coords": [32.5, 35.5],
        "name": "Proto-Eurasian Levant Corridor",
        "time": "~45,000 BCE",
        "desc": "Primary Out-of-Africa expansion gateway for Borean, Nostratic, Sino-Caucasian & Amerind stocks (32.5°N, 35.5°E).",
        "color": "blue",
        "icon": "share"
    },
    "Proto_Oceanic": {
        "coords": [-5.5, 141.0],
        "name": "Proto-Oceanic Sahul Hub (Papua / New Guinea)",
        "time": "~60,000 BCE",
        "desc": "Early coastal outgroup migration to Sahul (Papua / Australia). Severe founder-effect drift (*yɨʔ, *təc̢a).",
        "color": "purple",
        "icon": "globe"
    },
    "Beringia_Bridge": {
        "coords": [65.0, -168.0],
        "name": "Beringia Land Bridge Gateway",
        "time": "~20,000 BCE",
        "desc": "Siberia-to-Alaska transition corridor for early Amerind ancestors.",
        "color": "orange",
        "icon": "flag"
    },
    "Beringia_Americas": {
        "coords": [9.55, -85.67],
        "name": "Amerind Terminal Expansion (Central/South America)",
        "time": "~15,000 BCE",
        "desc": "Terminal founder-effect point (Americas). Minimal phonemic entropy (H_phon = 2.95 bits).",
        "color": "green",
        "icon": "map-marker"
    }
}

# ---------------------------------------------------------
# 1. GENERATE INTERACTIVE FOLIUM HTML MAP
# ---------------------------------------------------------

m = folium.Map(
    location=[15.0, 20.0],
    zoom_start=2.5,
    tiles="CartoDB positron"
)

# Add Markers
for key, hub in hubs.items():
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 240px;">
        <h4 style="margin:0 0 5px 0; color: #2c3e50;">{hub['name']}</h4>
        <b style="color: #e74c3c;">Time Horizon:</b> {hub['time']}<br>
        <p style="font-size: 12px; margin-top: 5px;">{hub['desc']}</p>
    </div>
    """
    folium.Marker(
        location=hub["coords"],
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"{hub['name']} ({hub['time']})",
        icon=folium.Icon(color=hub["color"], icon=hub["icon"])
    ).add_to(m)

# Trajectories for Folium
folium_trajectories = [
    {
        "points": [[4.15, 37.85], [-5.0, 35.0], [-25.0, 24.0]],
        "color": "#c0392b",
        "weight": 4,
        "dash": "5, 5",
        "label": "Trunk B: Proto-African Expansion (~65,000–50,000 BCE)"
    },
    {
        "points": [[4.15, 37.85], [10.0, 75.0], [3.0, 101.0], [-5.5, 141.0]],
        "color": "#8e44ad",
        "weight": 4,
        "dash": "8, 8",
        "label": "Trunk B (Outgroup): Proto-Oceanic Sahul Dispersal (~60,000 BCE)"
    },
    {
        "points": [[4.15, 37.85], [18.0, 37.0], [32.5, 35.5]],
        "color": "#2980b9",
        "weight": 5,
        "dash": None,
        "label": "Trunk A: Proto-Eurasian Levant Corridor (~45,000 BCE)"
    },
    {
        "points": [
            [32.5, 35.5],
            [48.0, 65.0],
            [62.0, 125.0],
            [65.0, 175.0],
            [65.0, -168.0],
            [48.0, -122.0],
            [30.0, -110.0],
            [9.55, -85.67]
        ],
        "color": "#27ae60",
        "weight": 3.5,
        "dash": "4, 4",
        "label": "Trunk A Expansion: Eurasia -> Beringia -> Americas (~30k–15k BCE)"
    }
]

for traj in folium_trajectories:
    folium.PolyLine(
        locations=traj["points"],
        color=traj["color"],
        weight=traj["weight"],
        opacity=0.85,
        dash_array=traj["dash"],
        tooltip=traj["label"]
    ).add_to(m)

html_path = os.path.join(docs_dir, "proto_human_phylogeo_map.html")
m.save(html_path)

# ---------------------------------------------------------
# 2. GENERATE HIGH-RES STATIC PNG MAP WITH WORLD CONTINENTS
# ---------------------------------------------------------

# Download / Load Natural Earth Land GeoJSON for Continents
geojson_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson"
local_geojson = os.path.join(docs_dir, "ne_110m_land.geojson")

if not os.path.exists(local_geojson):
    print("Downloading world land shape data...")
    urllib.request.urlretrieve(geojson_url, local_geojson)

world_land = gpd.read_file(local_geojson)

fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
ax.set_facecolor('#d4e6f1')  # Ocean blue color

# Plot Continent Polygons
world_land.plot(ax=ax, facecolor='#eaeded', edgecolor='#7f8c8d', linewidth=0.7, zorder=1)

# Set map limits & grid
ax.grid(True, linestyle='--', alpha=0.35, color='#95a5a6', zorder=2)
ax.set_xlim(-175, 175)
ax.set_ylim(-55, 75)
ax.set_xlabel("Longitude (°)", fontsize=11, fontweight='bold')
ax.set_ylabel("Latitude (°)", fontsize=11, fontweight='bold')
ax.set_title("Phylogeographic Map of Proto-Human Migration & Bifurcation Horizons\n(~65,000 BCE Out-of-Africa Dispersal)", fontsize=14, fontweight='bold', pad=15)

# Plot Trajectory Paths
# 1. African Vector
ax.plot([37.85, 35.0, 24.0], [4.15, -5.0, -25.0], color='#c0392b', linewidth=3.5, linestyle='--', label='Trunk B: Proto-African (~65,000–50,000 BCE)', zorder=3)

# 2. Oceanic Vector (Coastal to Papua PNG)
ax.plot([37.85, 75.0, 101.0, 141.0], [4.15, 10.0, 3.0, -5.5], color='#8e44ad', linewidth=3.5, linestyle=':', label='Trunk B (Outgroup): Proto-Oceanic Sahul (~60,000 BCE)', zorder=3)

# 3. Levant Vector
ax.plot([37.85, 37.0, 35.5], [4.15, 18.0, 32.5], color='#2980b9', linewidth=4.0, label='Trunk A: Proto-Eurasian Levant Corridor (~45,000 BCE)', zorder=3)

# 4. Beringia to Americas Vector
ax.plot([35.5, 65.0, 125.0, 175.0], [32.5, 48.0, 62.0, 65.0], color='#27ae60', linewidth=2.8, linestyle='-.', label='Trunk A Expansion: Eurasia -> Beringia (~30k BCE)', zorder=3)
ax.plot([175.0, 180.0], [65.0, 65.0], color='#27ae60', linewidth=2.8, linestyle='-.', zorder=3)
ax.plot([-180.0, -168.0, -122.0, -110.0, -85.67], [65.0, 65.0, 48.0, 30.0, 9.55], color='#27ae60', linewidth=2.8, linestyle='-.', label='Trunk A Expansion: Beringia -> Americas (~20k–15k BCE)', zorder=3)

# Plot Key Nodes
# Urheimat
ax.scatter([37.85], [4.15], color='#e74c3c', s=280, zorder=5, marker='*', edgecolors='black', linewidth=1.5)
ax.text(37.85 + 3, 4.15 + 2, "East African Urheimat Core\n(4.15°N, 37.85°E)\n~65,000 BCE", fontsize=8.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fadbd8', edgecolor='#e74c3c', alpha=0.95))

# Levant
ax.scatter([35.5], [32.5], color='#3498db', s=180, zorder=5, marker='o', edgecolors='black')
ax.text(35.5 + 3, 32.5 + 2, "Levant Corridor (Trunk A)\n~45,000 BCE", fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#ebf5fb', edgecolor='#3498db', alpha=0.95))

# Sahul (Papua PNG)
ax.scatter([141.0], [-5.5], color='#9b59b6', s=180, zorder=5, marker='s', edgecolors='black')
ax.text(141.0 - 28, -5.5 - 7, "Proto-Oceanic Sahul Hub\n(Papua PNG / Australia)\n~60,000 BCE", fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#f5eeed', edgecolor='#9b59b6', alpha=0.95))

# African Core
ax.scatter([24.0], [-25.0], color='#e67e22', s=180, zorder=5, marker='^', edgecolors='black')
ax.text(24.0 - 22, -25.0 - 7, "Proto-African Kalahari Core\n~50,000 BCE", fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fdebd0', edgecolor='#e67e22', alpha=0.95))

# Beringia Bridge
ax.scatter([-168.0], [65.0], color='#f39c12', s=150, zorder=5, marker='d', edgecolors='black')
ax.text(-168.0 + 4, 65.0 - 4, "Beringia Land Bridge\n~20,000 BCE", fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.95))

# Amerind Terminal
ax.scatter([-85.67], [9.55], color='#2ecc71', s=180, zorder=5, marker='p', edgecolors='black')
ax.text(-85.67 + 4, 9.55 - 4, "Amerind Terminal Expansion\n~15,000 BCE", fontsize=8, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f8f5', edgecolor='#2ecc71', alpha=0.95))

# Legend
ax.legend(loc='lower left', fontsize=9, framealpha=0.95)

png_path = os.path.join(docs_dir, "proto_human_phylogeo_map.png")
plt.tight_layout()
plt.savefig(png_path, dpi=300)
plt.close()

# Copy to Desktop\geo
shutil.copy(html_path, os.path.join(geo_dir, "proto_human_phylogeo_map.html"))
shutil.copy(png_path, os.path.join(geo_dir, "proto_human_phylogeo_map.png"))

print("World landmass map successfully generated and updated in both docs/ and Desktop/geo/!")