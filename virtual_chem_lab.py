"""
Virtual Chemistry Lab — University Level
Run: streamlit run virtual_chem_lab.py
Requires: streamlit, anthropic
Install : pip install streamlit anthropic
"""

import streamlit as st
import json
import math
import time
import random
import anthropic

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VChem Lab",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
}

/* Dark lab theme */
.stApp {
    background: #0b0f1a;
    color: #d4e0f7;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { color: #c9d8f0 !important; }

/* Headers */
h1 { font-size: 2rem !important; font-weight: 700; color: #7dd3fc !important; letter-spacing: -0.5px; }
h2 { font-size: 1.4rem !important; color: #93c5fd !important; }
h3 { font-size: 1.1rem !important; color: #bfdbfe !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af);
    color: white;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    box-shadow: 0 0 16px rgba(59,130,246,0.4);
    transform: translateY(-1px);
}

/* Cards */
.lab-card {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}
.reaction-box {
    background: #071428;
    border: 1px solid #164e63;
    border-radius: 10px;
    padding: 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: #67e8f9;
    margin: 8px 0;
}
.theory-box {
    background: #0d1f3c;
    border-left: 4px solid #3b82f6;
    border-radius: 6px;
    padding: 16px;
    margin: 10px 0;
    color: #bfdbfe;
    font-size: 14px;
    line-height: 1.7;
}
.chat-msg-user {
    background: #1e3a5f;
    border-radius: 10px 10px 2px 10px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 13px;
    color: #e0f2fe;
}
.chat-msg-ai {
    background: #112240;
    border: 1px solid #1e3a8a;
    border-radius: 10px 10px 10px 2px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 13px;
    color: #bae6fd;
}
.badge {
    display:inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px;
}
.badge-acid   { background:#7f1d1d; color:#fca5a5; border:1px solid #ef4444; }
.badge-base   { background:#1e3a5f; color:#93c5fd; border:1px solid #3b82f6; }
.badge-salt   { background:#1e3e2f; color:#86efac; border:1px solid #22c55e; }
.badge-ox     { background:#4c1d95; color:#c4b5fd; border:1px solid #8b5cf6; }
.badge-ind    { background:#1c1917; color:#fcd34d; border:1px solid #f59e0b; }

/* Beaker SVG wrapper */
.beaker-wrap { display:flex; justify-content:center; align-items:flex-end; }

/* Quiz */
.quiz-opt {
    background: #0f2240;
    border: 1px solid #1e4080;
    border-radius: 8px;
    padding: 10px 16px;
    margin: 5px 0;
    cursor: pointer;
    transition: background 0.15s;
    color: #bfdbfe;
    font-size: 14px;
}
.correct { border-color:#22c55e !important; background:#0d3321 !important; color:#86efac !important; }
.wrong   { border-color:#ef4444 !important; background:#3b0a0a !important; color:#fca5a5 !important; }

/* selectbox label overrides */
label { color: #93c5fd !important; font-size: 13px !important; }

/* scrollbar */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#0b0f1a; }
::-webkit-scrollbar-thumb { background:#1e3a5f; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHEMICAL DATABASE
# ─────────────────────────────────────────────
CHEMICALS = {
    # ── Acids ──────────────────────────────────
    "HCl (Hydrochloric Acid)":       {"color":"#e8f4fd","hex":"#dbeafe","type":"acid","formula":"HCl","molar_mass":36.46,"pka":-7,"density":1.19,"description":"Strong acid, fully dissociates. Fumes in air."},
    "H₂SO₄ (Sulfuric Acid)":         {"color":"#fef9c3","hex":"#fef08a","type":"acid","formula":"H2SO4","molar_mass":98.08,"pka":-3,"density":1.84,"description":"Strong diprotic acid. Highly corrosive, dehydrating agent."},
    "HNO₃ (Nitric Acid)":            {"color":"#fef3c7","hex":"#fde68a","type":"acid","formula":"HNO3","molar_mass":63.01,"pka":-1.4,"density":1.51,"description":"Strong oxidizing acid. Reacts with metals, produces NO₂."},
    "CH₃COOH (Acetic Acid)":         {"color":"#f0fdf4","hex":"#dcfce7","type":"acid","formula":"CH3COOH","molar_mass":60.05,"pka":4.76,"density":1.05,"description":"Weak acid. pKa 4.76. Vinegar constituent."},
    "H₃PO₄ (Phosphoric Acid)":       {"color":"#f0f9ff","hex":"#e0f2fe","type":"acid","formula":"H3PO4","molar_mass":98.00,"pka":2.15,"density":1.88,"description":"Triprotic weak acid. pKa1=2.15, pKa2=7.20, pKa3=12.35."},
    "HF (Hydrofluoric Acid)":         {"color":"#ecfeff","hex":"#a5f3fc","type":"acid","formula":"HF","molar_mass":20.01,"pka":3.17,"density":1.15,"description":"Weak acid but extremely corrosive. pKa 3.17."},
    "HClO₄ (Perchloric Acid)":       {"color":"#f8fafc","hex":"#e2e8f0","type":"acid","formula":"HClO4","molar_mass":100.46,"pka":-10,"density":1.67,"description":"Strongest common acid. Powerful oxidizer."},
    "H₂C₂O₄ (Oxalic Acid)":         {"color":"#f0fdf4","hex":"#bbf7d0","type":"acid","formula":"H2C2O4","molar_mass":90.03,"pka":1.25,"density":1.90,"description":"Diprotic organic acid. Reducing agent. Used in titrations with KMnO₄."},

    # ── Bases ──────────────────────────────────
    "NaOH (Sodium Hydroxide)":       {"color":"#f0f9ff","hex":"#bae6fd","type":"base","formula":"NaOH","molar_mass":40.00,"pkb":-0.56,"density":2.13,"description":"Strong base. Fully dissociates. Caustic. Absorbs CO₂ from air."},
    "KOH (Potassium Hydroxide)":     {"color":"#eff6ff","hex":"#bfdbfe","type":"base","formula":"KOH","molar_mass":56.11,"pkb":-0.5,"density":2.12,"description":"Strong base. Similar to NaOH but more soluble."},
    "Ca(OH)₂ (Calcium Hydroxide)":  {"color":"#f8fafc","hex":"#e2e8f0","type":"base","formula":"Ca(OH)2","molar_mass":74.09,"pkb":2.37,"density":2.21,"description":"Slightly soluble base. Limewater. Turns milky with CO₂."},
    "NH₃ (Ammonia)":                 {"color":"#f0fdf4","hex":"#bbf7d0","type":"base","formula":"NH3","molar_mass":17.03,"pkb":4.74,"density":0.73,"description":"Weak base. pKb 4.74. Pungent gas. Common ligand."},
    "Na₂CO₃ (Sodium Carbonate)":    {"color":"#f0f9ff","hex":"#e0f2fe","type":"base","formula":"Na2CO3","molar_mass":105.99,"pkb":3.67,"density":2.54,"description":"Mild base. Soda ash. Hydrolysis gives alkaline solution."},
    "NaHCO₃ (Sodium Bicarbonate)":  {"color":"#f9fafb","hex":"#f3f4f6","type":"base","formula":"NaHCO3","molar_mass":84.01,"pkb":7.65,"density":2.20,"description":"Amphoteric, acts mainly as base. Baking soda. Fizzes with acid."},

    # ── Salts / Transition Metal Compounds ─────
    "FeCl₃ (Iron III Chloride)":    {"color":"#b45309","hex":"#f97316","type":"salt","formula":"FeCl3","molar_mass":162.20,"density":2.90,"description":"Yellow-orange solution. Lewis acid. Oxidizing agent. Fe³⁺ characteristic."},
    "CuSO₄ (Copper Sulfate)":       {"color":"#1d4ed8","hex":"#3b82f6","type":"salt","formula":"CuSO4","molar_mass":159.61,"density":3.60,"description":"Bright blue solution. Cu²⁺ turns deep blue with NH₃ (tetraamine complex)."},
    "KMnO₄ (Potassium Permanganate)":{"color":"#6b21a8","hex":"#a855f7","type":"oxidizer","formula":"KMnO4","molar_mass":158.03,"density":2.70,"description":"Deep purple. Strong oxidizer. Decolourises in redox reactions → Mn²⁺ (pale pink)."},
    "K₂Cr₂O₇ (Potassium Dichromate)":{"color":"#c2410c","hex":"#f97316","type":"oxidizer","formula":"K2Cr2O7","molar_mass":294.19,"density":2.68,"description":"Bright orange. Strong oxidizer in acid. Cr₂O₇²⁻ → Cr³⁺ (green) on reduction."},
    "AgNO₃ (Silver Nitrate)":       {"color":"#f8fafc","hex":"#f1f5f9","type":"salt","formula":"AgNO3","molar_mass":169.87,"density":4.35,"description":"Colourless. Reacts with Cl⁻ → white AgCl precipitate. Used to test for halides."},
    "BaCl₂ (Barium Chloride)":      {"color":"#f0f9ff","hex":"#e0f2fe","type":"salt","formula":"BaCl2","molar_mass":208.23,"density":3.86,"description":"Colourless. Reacts with SO₄²⁻ → white BaSO₄ precipitate. Sulfate test."},
    "ZnSO₄ (Zinc Sulfate)":         {"color":"#f0fdf4","hex":"#dcfce7","type":"salt","formula":"ZnSO4","molar_mass":161.47,"density":3.54,"description":"Colourless. Amphoteric Zn²⁺ dissolves in excess NaOH."},
    "FeSO₄ (Iron II Sulfate)":      {"color":"#14532d","hex":"#4ade80","type":"salt","formula":"FeSO4","molar_mass":151.91,"density":3.65,"description":"Pale green solution. Reducing agent. Oxidises in air to Fe³⁺ (yellow-brown)."},
    "NaCl (Sodium Chloride)":        {"color":"#f8fafc","hex":"#f1f5f9","type":"salt","formula":"NaCl","molar_mass":58.44,"density":2.17,"description":"Colourless. Neutral salt. Used as electrolyte."},
    "Na₂S₂O₃ (Sodium Thiosulfate)": {"color":"#f0fdf4","hex":"#d1fae5","type":"salt","formula":"Na2S2O3","molar_mass":158.11,"density":1.67,"description":"Colourless. Reducing agent. Reacts with I₂ → colourless. Used in iodometric titrations."},
    "KI (Potassium Iodide)":        {"color":"#f8fafc","hex":"#fef9c3","type":"salt","formula":"KI","molar_mass":166.00,"density":3.12,"description":"Colourless. Source of I⁻. Oxidised to I₂ (brown) by oxidising agents."},
    "Na₂SO₄ (Sodium Sulfate)":      {"color":"#f9fafb","hex":"#f3f4f6","type":"salt","formula":"Na2SO4","molar_mass":142.04,"density":2.68,"description":"Colourless. Anhydrous form is drying agent. Used in enthalpy experiments."},

    # ── Indicators ─────────────────────────────
    "Phenolphthalein":               {"color":"#fdf4ff","hex":"#f0abfc","type":"indicator","formula":"C₂₀H₁₄O₄","molar_mass":318.32,"density":1.28,"description":"Colourless below pH 8.2, pink/magenta above 10. Used in acid-base titrations."},
    "Methyl Orange":                 {"color":"#fef3c7","hex":"#fbbf24","type":"indicator","formula":"C₁₄H₁₄N₃NaO₃S","molar_mass":327.33,"density":1.28,"description":"Red below pH 3.1, orange at 3.1-4.4, yellow above 4.4."},
    "Litmus":                        {"color":"#ddd6fe","hex":"#a78bfa","type":"indicator","formula":"C₁₂H₁₄O₃N","molar_mass":194.00,"density":1.10,"description":"Red below pH 7, blue above 7. Natural dye. Less sharp endpoint."},
    "Universal Indicator":           {"color":"#86efac","hex":"#4ade80","type":"indicator","formula":"mixture","molar_mass":0,"density":1.00,"description":"Shows full pH spectrum: red (1-3), orange (4-5), yellow (6), green (7), blue (8-9), violet (10-14)."},
    "Starch Solution":               {"color":"#fafaf9","hex":"#e7e5e4","type":"indicator","formula":"(C₆H₁₀O₅)n","molar_mass":0,"density":1.00,"description":"Colourless. Turns deep blue-black with I₂. Used as endpoint indicator in iodometric titrations."},
    "Eriochrome Black T":            {"color":"#292524","hex":"#1c1917","type":"indicator","formula":"C₂₀H₁₂N₃NaO₇S","molar_mass":461.38,"density":1.30,"description":"Wine red with Ca²⁺/Mg²⁺, pure blue at endpoint. EDTA titrations."},
}

CHEMICAL_NAMES = list(CHEMICALS.keys())

# ─────────────────────────────────────────────
# REACTION DATABASE
# ─────────────────────────────────────────────
REACTIONS = {
    frozenset(["HCl (Hydrochloric Acid)","NaOH (Sodium Hydroxide)"]):
        {"name":"Strong Acid–Strong Base Neutralisation","equation":"HCl(aq) + NaOH(aq) → NaCl(aq) + H₂O(l)",
         "net_ionic":"H⁺(aq) + OH⁻(aq) → H₂O(l)","observation":"Temperature rises. Colourless solution. pH→7 at endpoint.",
         "result_color":"#f1f5f9","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-57.3 kJ/mol",
         "mechanism":"Brønsted–Lowry proton transfer. H⁺ from HCl reacts with OH⁻ from NaOH.",
         "theory":"This is a prototypical strong acid–strong base neutralisation. Both reactants fully dissociate. The driving force is formation of water (Kw = 1×10⁻¹⁴). ΔH = −57.3 kJ/mol. The salt NaCl is neutral (pKa of conjugate acid = ∞)."},
    frozenset(["H₂SO₄ (Sulfuric Acid)","NaOH (Sodium Hydroxide)"]):
        {"name":"Sulfuric Acid – Sodium Hydroxide","equation":"H₂SO₄(aq) + 2NaOH(aq) → Na₂SO₄(aq) + 2H₂O(l)",
         "net_ionic":"H⁺(aq) + OH⁻(aq) → H₂O(l)","observation":"Exothermic. Colourless solution. Na₂SO₄ formed.",
         "result_color":"#f1f5f9","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-114.6 kJ/mol",
         "mechanism":"H₂SO₄ is diprotic; both protons sequentially transferred to OH⁻.",
         "theory":"H₂SO₄ donates two protons (stepwise). First dissociation is complete; second has pKa2 = 1.99. Overall ΔH ≈ 2×57.3 kJ/mol."},
    frozenset(["HCl (Hydrochloric Acid)","Na₂CO₃ (Sodium Carbonate)"]):
        {"name":"Acid–Carbonate Reaction","equation":"2HCl(aq) + Na₂CO₃(aq) → 2NaCl(aq) + H₂O(l) + CO₂(g)",
         "net_ionic":"2H⁺(aq) + CO₃²⁻(aq) → H₂O(l) + CO₂(g)","observation":"Vigorous effervescence (CO₂ gas). Solution turns colourless.",
         "result_color":"#f1f5f9","effervescence":True,"precipitate":False,"color_change":False,"delta_H":"-26 kJ/mol",
         "mechanism":"H⁺ protonates CO₃²⁻ → HCO₃⁻, then again → H₂CO₃ → H₂O + CO₂.",
         "theory":"CO₃²⁻ is a diprotic base. The reaction proceeds in two steps. CO₂ gas drives the reaction to completion (Le Chatelier). Fizzing is characteristic of carbonate/bicarbonate + acid reactions."},
    frozenset(["HCl (Hydrochloric Acid)","NaHCO₃ (Sodium Bicarbonate)"]):
        {"name":"Acid–Bicarbonate Reaction","equation":"HCl(aq) + NaHCO₃(aq) → NaCl(aq) + H₂O(l) + CO₂(g)",
         "net_ionic":"H⁺(aq) + HCO₃⁻(aq) → H₂O(l) + CO₂(g)","observation":"Moderate effervescence. CO₂ produced.",
         "result_color":"#f8fafc","effervescence":True,"precipitate":False,"color_change":False,"delta_H":"-11 kJ/mol",
         "mechanism":"Single proton transfer to HCO₃⁻ forming unstable H₂CO₃ which decomposes.",
         "theory":"HCO₃⁻ acts as a base (pKb=7.65). The product H₂CO₃ is unstable (Ka = 4.3×10⁻⁷) and immediately decomposes to CO₂ + H₂O. Used in baking powder reactions."},
    frozenset(["AgNO₃ (Silver Nitrate)","HCl (Hydrochloric Acid)"]):
        {"name":"Halide Precipitation (Chloride Test)","equation":"AgNO₃(aq) + HCl(aq) → AgCl(s)↓ + HNO₃(aq)",
         "net_ionic":"Ag⁺(aq) + Cl⁻(aq) → AgCl(s)","observation":"Immediate white curdy precipitate of AgCl. Insoluble in HNO₃, soluble in NH₃.",
         "result_color":"#f8fafc","effervescence":False,"precipitate":True,"color_change":False,"delta_H":"-65.7 kJ/mol",
         "mechanism":"Ionic precipitation. Ksp(AgCl) = 1.8×10⁻¹⁰, extremely low solubility.",
         "theory":"AgCl precipitates because Qsp instantly exceeds Ksp (1.8×10⁻¹⁰). The precipitate is white, turns grey-purple in light (photoreduction). Dissolves in NH₃ forming [Ag(NH₃)₂]⁺ complex."},
    frozenset(["BaCl₂ (Barium Chloride)","H₂SO₄ (Sulfuric Acid)"]):
        {"name":"Sulfate Precipitation (Sulfate Test)","equation":"BaCl₂(aq) + H₂SO₄(aq) → BaSO₄(s)↓ + 2HCl(aq)",
         "net_ionic":"Ba²⁺(aq) + SO₄²⁻(aq) → BaSO₄(s)","observation":"White dense precipitate of BaSO₄, insoluble in dilute HCl.",
         "result_color":"#f8fafc","effervescence":False,"precipitate":True,"color_change":False,"delta_H":"-26 kJ/mol",
         "mechanism":"Ionic precipitation. Ksp(BaSO₄) = 1.1×10⁻¹⁰.",
         "theory":"BaSO₄ is almost completely insoluble (Ksp=1.1×10⁻¹⁰). Used as gravimetric standard. Does NOT dissolve in hot concentrated HCl or HNO₃—distinguishing feature."},
    frozenset(["KMnO₄ (Potassium Permanganate)","H₂C₂O₄ (Oxalic Acid)"]):
        {"name":"KMnO₄ – Oxalic Acid Redox Titration","equation":"2KMnO₄ + 5H₂C₂O₄ + 3H₂SO₄ → 2MnSO₄ + 10CO₂ + K₂SO₄ + 8H₂O",
         "net_ionic":"MnO₄⁻ + 5e⁻ + 8H⁺ → Mn²⁺ + 4H₂O (×2); H₂C₂O₄ → 2CO₂ + 2H⁺ + 2e⁻ (×5)",
         "observation":"Purple KMnO₄ decolourises as it oxidises oxalic acid. Endpoint: permanent pale pink.",
         "result_color":"#f0abfc","effervescence":True,"precipitate":False,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Redox: MnO₄⁻ (Mn VII→II, gains 5e⁻) oxidises C₂O₄²⁻ (C III→IV, loses 2e⁻). Reaction self-catalysed by Mn²⁺.",
         "theory":"Classic permanganometry. E°(MnO₄⁻/Mn²⁺)=+1.51V, E°(CO₂/C₂O₄²⁻)=−0.49V. ΔE°=2.0V, ΔG°=−nFΔE°<0 → spontaneous. Reaction is slow at room temp, heated to 60–70°C. KMnO₄ is its own indicator."},
    frozenset(["FeCl₃ (Iron III Chloride)","NaOH (Sodium Hydroxide)"]):
        {"name":"Iron(III) Hydroxide Precipitation","equation":"FeCl₃(aq) + 3NaOH(aq) → Fe(OH)₃(s)↓ + 3NaCl(aq)",
         "net_ionic":"Fe³⁺(aq) + 3OH⁻(aq) → Fe(OH)₃(s)","observation":"Reddish-brown gelatinous precipitate of Fe(OH)₃.",
         "result_color":"#b45309","effervescence":False,"precipitate":True,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Ionic precipitation. Ksp[Fe(OH)₃]=2.8×10⁻³⁹.",
         "theory":"Fe³⁺ precipitates as gelatinous Fe(OH)₃ (rust-coloured). Ksp is incredibly small (2.8×10⁻³⁹). Fe(OH)₃ is amphoteric—dissolves in excess strong acid or strong base (to form [Fe(OH)₄]⁻). Used in qualitative analysis Group III cation separation."},
    frozenset(["CuSO₄ (Copper Sulfate)","NaOH (Sodium Hydroxide)"]):
        {"name":"Copper(II) Hydroxide Precipitation","equation":"CuSO₄(aq) + 2NaOH(aq) → Cu(OH)₂(s)↓ + Na₂SO₄(aq)",
         "net_ionic":"Cu²⁺(aq) + 2OH⁻(aq) → Cu(OH)₂(s)","observation":"Pale blue precipitate of Cu(OH)₂. On heating → black CuO.",
         "result_color":"#1e40af","effervescence":False,"precipitate":True,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Ionic precipitation followed by dehydration at higher temperature.",
         "theory":"Cu(OH)₂ Ksp=2.2×10⁻²⁰. Pale blue gelatinous ppt. On heating: Cu(OH)₂ → CuO(black) + H₂O. With excess NH₃: Cu(OH)₂ dissolves → deep blue [Cu(NH₃)₄]²⁺ (Schweizer's reagent)."},
    frozenset(["KMnO₄ (Potassium Permanganate)","FeSO₄ (Iron II Sulfate)"]):
        {"name":"Permanganate – Fe²⁺ Redox","equation":"KMnO₄ + 5FeSO₄ + 4H₂SO₄ → MnSO₄ + 5Fe₂(SO₄)₃ + K₂SO₄ + 4H₂O",
         "net_ionic":"MnO₄⁻ + 5Fe²⁺ + 8H⁺ → Mn²⁺ + 5Fe³⁺ + 4H₂O","observation":"Purple solution decolourises instantly. Solution turns pale yellow (Fe³⁺).",
         "result_color":"#ca8a04","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"MnO₄⁻ (Mn VII→II) oxidises Fe²⁺→Fe³⁺. Each MnO₄⁻ accepts 5e⁻ from 5 Fe²⁺.",
         "theory":"Standard potentials: E°(MnO₄⁻/Mn²⁺)=+1.51V; E°(Fe³⁺/Fe²⁺)=+0.77V. ΔE°=+0.74V, spontaneous. Basis of potassium permanganate back-titration. Solution colour change from purple to nearly colourless (then yellow from Fe³⁺) is dramatic."},
    frozenset(["Na₂S₂O₃ (Sodium Thiosulfate)","KI (Potassium Iodide)","H₂SO₄ (Sulfuric Acid)"]):
        {"name":"Iodometric Titration (Clock Reaction related)","equation":"2Na₂S₂O₃ + I₂ → Na₂S₄O₆ + 2NaI",
         "net_ionic":"2S₂O₃²⁻ + I₂ → S₄O₆²⁻ + 2I⁻","observation":"Brown iodine colour disappears. With starch: deep blue→colourless at endpoint.",
         "result_color":"#fef9c3","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Thiosulfate reduces I₂ to I⁻; S₂O₃²⁻ oxidised to tetrathionate S₄O₆²⁻.",
         "theory":"Iodometric method. S₂O₃²⁻ is the reducing agent. E°(I₂/I⁻)=+0.54V; E°(S₄O₆²⁻/S₂O₃²⁻)=+0.09V. The ratio is exactly 2:1 (S₂O₃²⁻:I₂). Starch gives sharp endpoint: blue → colourless."},
    frozenset(["CH₃COOH (Acetic Acid)","NaOH (Sodium Hydroxide)"]):
        {"name":"Weak Acid–Strong Base Titration","equation":"CH₃COOH(aq) + NaOH(aq) → CH₃COONa(aq) + H₂O(l)",
         "net_ionic":"CH₃COOH + OH⁻ → CH₃COO⁻ + H₂O","observation":"Gradual pH rise. Buffer region evident. Endpoint pH > 7 (≈8.7). Phenolphthalein appropriate.",
         "result_color":"#f1f5f9","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-56.1 kJ/mol",
         "mechanism":"Stepwise proton transfer. Buffer forms during titration (Henderson–Hasselbalch applicable).",
         "theory":"Ka(CH₃COOH)=1.8×10⁻⁵, pKa=4.76. At half-equivalence point: pH=pKa=4.76. Endpoint pH=8.7 (CH₃COO⁻ hydrolysis). Henderson–Hasselbalch: pH = 4.76 + log([A⁻]/[HA]). Buffer capacity maximum at pH=pKa."},
    frozenset(["NH₃ (Ammonia)","HCl (Hydrochloric Acid)"]):
        {"name":"Weak Base–Strong Acid Titration","equation":"NH₃(aq) + HCl(aq) → NH₄Cl(aq)",
         "net_ionic":"NH₃ + H⁺ → NH₄⁺","observation":"Solution becomes acidic at endpoint. pH < 7 at equivalence. Dense white fumes if gaseous.",
         "result_color":"#f8fafc","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-52.2 kJ/mol",
         "mechanism":"Proton transfer from HCl to lone pair on N of NH₃.",
         "theory":"Kb(NH₃)=1.8×10⁻⁵, pKb=4.74, pKa(NH₄⁺)=9.26. Endpoint pH=5.3. Methyl orange indicator is appropriate (endpoint pH 4–4.4). Buffer region: pH = 9.26 + log([NH₃]/[NH₄⁺])."},
    frozenset(["K₂Cr₂O₇ (Potassium Dichromate)","FeSO₄ (Iron II Sulfate)"]):
        {"name":"Dichromate – Fe²⁺ Redox","equation":"K₂Cr₂O₇ + 6FeSO₄ + 7H₂SO₄ → Cr₂(SO₄)₃ + 3Fe₂(SO₄)₃ + K₂SO₄ + 7H₂O",
         "net_ionic":"Cr₂O₇²⁻ + 6Fe²⁺ + 14H⁺ → 2Cr³⁺ + 6Fe³⁺ + 7H₂O","observation":"Orange dichromate turns green (Cr³⁺). Fe²⁺→Fe³⁺ (yellow).",
         "result_color":"#16a34a","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Cr₂O₇²⁻ (Cr VI→III, gains 3e⁻ each Cr) oxidises Fe²⁺→Fe³⁺.",
         "theory":"E°(Cr₂O₇²⁻/Cr³⁺)=+1.33V; E°(Fe³⁺/Fe²⁺)=+0.77V. ΔE°=+0.56V. Colour change orange→green is unambiguous. Diphenylamine indicator used for sharp endpoint in volumetric work. More stable than KMnO₄ as primary standard."},
    frozenset(["CuSO₄ (Copper Sulfate)","NH₃ (Ammonia)"]):
        {"name":"Copper–Ammonia Complex Formation","equation":"CuSO₄(aq) + 4NH₃(aq) → [Cu(NH₃)₄]SO₄(aq)",
         "net_ionic":"Cu²⁺ + 4NH₃ → [Cu(NH₃)₄]²⁺","observation":"Pale blue Cu(OH)₂ ppt first (at low NH₃), then dissolves → deep royal blue tetraamine complex.",
         "result_color":"#1e3a8a","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-kJ variable",
         "mechanism":"Ligand substitution. NH₃ replaces H₂O ligands in coordination sphere of Cu²⁺.",
         "theory":"[Cu(NH₃)₄]²⁺ (tetraamminecopper(II)) is a deep blue square-planar complex. Formation constant Kf ≈ 1×10¹³. Crystal Field Theory: NH₃ is a stronger field ligand than H₂O → larger Δo → blue shift. This is Schweizer's reagent, dissolves cellulose."},
    frozenset(["HCl (Hydrochloric Acid)","H₂SO₄ (Sulfuric Acid)","NaOH (Sodium Hydroxide)"]):
        {"name":"Mixed Acid Neutralisation","equation":"HCl + H₂SO₄ + 3NaOH → NaCl + Na₂SO₄ + 3H₂O",
         "net_ionic":"H⁺ + OH⁻ → H₂O","observation":"Highly exothermic. Colourless solution at endpoint.",
         "result_color":"#f1f5f9","effervescence":False,"precipitate":False,"color_change":True,"delta_H":"-170 kJ/mol (combined)",
         "mechanism":"Sequential proton transfers. All strong acids fully dissociate first.",
         "theory":"The total moles of H⁺ from all strong acids react with total moles of OH⁻. Back-titration possible. Thermochemically additive."},
}

# ─────────────────────────────────────────────
# QUIZ QUESTIONS
# ─────────────────────────────────────────────
QUIZ_QUESTIONS = [
    {"q":"What is the pKa of acetic acid?","opts":["4.76","7.00","2.15","9.26"],"ans":0,"exp":"Ka(CH₃COOH)=1.8×10⁻⁵, pKa=−log(1.8×10⁻⁵)=4.76"},
    {"q":"Which indicator is suitable for a weak acid–strong base titration?","opts":["Methyl Orange","Phenolphthalein","Litmus","Methyl Red"],"ans":1,"exp":"Endpoint pH≈8.7; phenolphthalein range is 8.2–10. Methyl orange (3.1–4.4) would miss it."},
    {"q":"What is the net ionic equation for any strong acid–strong base neutralisation?","opts":["Na⁺+Cl⁻→NaCl","H⁺+OH⁻→H₂O","H₂O→H⁺+OH⁻","H₂+O₂→H₂O"],"ans":1,"exp":"Spectator ions (Na⁺, Cl⁻) cancel. The only reaction is H⁺+OH⁻→H₂O."},
    {"q":"The Ksp of AgCl is 1.8×10⁻¹⁰. What is [Ag⁺] in a saturated solution?","opts":["1.8×10⁻⁵ M","1.34×10⁻⁵ M","3.6×10⁻⁵ M","1.8×10⁻¹⁰ M"],"ans":1,"exp":"Ksp=[Ag⁺][Cl⁻]=s². s=√(1.8×10⁻¹⁰)=1.34×10⁻⁵ M"},
    {"q":"In the KMnO₄–oxalic acid reaction, what is the colour at the endpoint?","opts":["Deep purple","Colourless","Pale pink","Bright orange"],"ans":2,"exp":"One extra drop of KMnO₄ past equivalence gives a permanent pale pink—that is the endpoint."},
    {"q":"What change is observed when excess NH₃ is added to Cu(OH)₂ precipitate?","opts":["No change","White precipitate forms","Deep blue solution forms","Brown gas evolved"],"ans":2,"exp":"[Cu(NH₃)₄]²⁺ (tetraamminecopper(II)) forms—a deep royal blue complex with Kf≈10¹³."},
    {"q":"Which standard reduction potential is HIGHER?","opts":["Fe³⁺/Fe²⁺ (+0.77V)","MnO₄⁻/Mn²⁺ (+1.51V)","They are equal","Cr₂O₇²⁻/Cr³⁺ (+1.33V)"],"ans":1,"exp":"MnO₄⁻/Mn²⁺ E°=+1.51V is the highest among the options, making permanganate the strongest oxidiser."},
    {"q":"At the half-equivalence point of a weak acid titration, which statement is TRUE?","opts":["pH = 7","pH = pKb","pH = pKa","Buffer capacity is zero"],"ans":2,"exp":"Henderson–Hasselbalch: pH=pKa+log([A⁻]/[HA]). At half-equivalence [A⁻]=[HA], so pH=pKa."},
    {"q":"The reaction between Na₂CO₃ and HCl produces which gas?","opts":["HCl gas","O₂","SO₂","CO₂"],"ans":3,"exp":"CO₃²⁻+2H⁺→H₂O+CO₂↑. The carbonic acid H₂CO₃ formed is unstable and decomposes immediately."},
    {"q":"BaSO₄ precipitate is insoluble in dilute HCl. This is because:","opts":["Ba²⁺ has full d-orbitals","Ksp is extremely small (1.1×10⁻¹⁰)","SO₄²⁻ is a strong oxidiser","Ba²⁺ forms a stable complex with Cl⁻"],"ans":1,"exp":"Ksp(BaSO₄)=1.1×10⁻¹⁰ is so small that even excess H⁺ cannot dissolve it; no common ion complexes form."},
    {"q":"Which of these is a self-indicating redox titrant (no external indicator needed)?","opts":["K₂Cr₂O₇","Na₂S₂O₃","KMnO₄","BaCl₂"],"ans":2,"exp":"KMnO₄ is deep purple; its reduction product Mn²⁺ is nearly colourless. One extra drop gives permanent pink—self-indicating."},
    {"q":"What colour does FeCl₃ solution appear?","opts":["Blue","Colourless","Yellow-orange","Green"],"ans":2,"exp":"Fe³⁺ ions give the characteristic yellow-orange colour in aqueous solution due to d-d transitions and charge transfer."},
    {"q":"In iodometric titrations, when should starch indicator be added?","opts":["At the very start","When solution turns blue","Near the endpoint (pale yellow)","After the endpoint"],"ans":2,"exp":"Adding starch near endpoint prevents irreversible starch–I₂ complex formation and gives sharper endpoint."},
    {"q":"The enthalpy of neutralisation for strong acid + strong base is approximately:","opts":["-28 kJ/mol","-57 kJ/mol","-114 kJ/mol","-100 kJ/mol"],"ans":1,"exp":"ΔH neutralisation = −57.3 kJ/mol for H⁺+OH⁻→H₂O. It's constant for all strong acid–strong base combinations."},
    {"q":"Fe(OH)₃ has a Ksp of 2.8×10⁻³⁹. What does this indicate?","opts":["It is soluble at high pH","It precipitates even at trace Fe³⁺ concentrations","It dissolves readily in water","It is amphoteric and dissolves in base only"],"ans":1,"exp":"The incredibly small Ksp (2.8×10⁻³⁹) means [Fe³⁺]×[OH⁻]³ must be negligible—Fe(OH)₃ forms at even µM concentrations."},
    {"q":"Which of the following shows the CORRECT order of acid strength?","opts":["HF > HCl > HBr > HI","HI > HBr > HCl > HF","HCl > HF > HBr > HI","HBr > HCl > HI > HF"],"ans":1,"exp":"Bond enthalpy decreases H–X down the group; weaker bond = stronger acid. HI > HBr > HCl >> HF (HF is a weak acid, pKa=3.17)."},
    {"q":"Crystal Field Theory explains the colour of [Cu(NH₃)₄]²⁺ as due to:","opts":["Charge transfer","d-d electronic transition absorbing visible light","Fluorescence","Phosphorescence"],"ans":1,"exp":"NH₃ splits the d-orbitals (Δo). Electrons transition between d-levels, absorbing orange light → deep blue colour observed."},
    {"q":"What is the role of H₂SO₄ in the KMnO₄–Fe²⁺ titration?","opts":["Reducing agent","Provides acidic medium for MnO₄⁻ reduction to Mn²⁺","Precipitant for Mn²⁺","Indicator"],"ans":1,"exp":"In neutral/alkaline solution MnO₄⁻ reduces only to MnO₂ (brown). H₂SO₄ ensures reduction all the way to Mn²⁺ (colourless/pale pink)."},
    {"q":"Henderson–Hasselbalch equation is: pH = pKa + log([A⁻]/[HA]). At pH = pKa + 1:","opts":["[HA] = 10×[A⁻]","[A⁻] = 10×[HA]","[HA] = [A⁻]","Buffer capacity is maximum"],"ans":1,"exp":"log([A⁻]/[HA])=1 → [A⁻]/[HA]=10. So [A⁻] is 10 times [HA]. The acid is 91% deprotonated."},
    {"q":"Na₂S₂O₃ titrates I₂ in the ratio:","opts":["1:1","1:2","2:1","3:1"],"ans":2,"exp":"2S₂O₃²⁻ + I₂ → S₄O₆²⁻ + 2I⁻. Ratio S₂O₃²⁻:I₂ = 2:1. Each I₂ accepts 2e⁻; each S₂O₃²⁻ donates 1e⁻."},
]

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "page": "login",
        "beaker_contents": [],          # list of {"name":..,"color":..,"volume":..}
        "mixed": False,
        "reaction_result": None,
        "chat_history": [],
        "quiz_idx": 0,
        "quiz_score": 0,
        "quiz_answered": False,
        "quiz_selected": None,
        "show_theory": False,
        "experiments_done": 0,
        "quiz_done": 0,
        "temperature": 25,
        "lab_domain": "Volumetric Analysis",
        "bubbles_active": False,
        "quiz_questions_order": list(range(len(QUIZ_QUESTIONS))),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HELPER: AI CLIENT (Scholar Agent)
# ─────────────────────────────────────────────
@st.cache_resource
def get_client():
    return anthropic.Anthropic()

SCHOLAR_SYSTEM = """You are "Scholar", an expert university-level chemistry AI tutor embedded in a Virtual Chemistry Lab.
You have deep knowledge of:
- Acid-base chemistry, titrations, indicators, buffer theory (Henderson–Hasselbalch)
- Redox reactions, electrochemistry, standard reduction potentials
- Solubility product (Ksp), precipitation reactions, complex ion formation
- Thermochemistry, enthalpy of neutralisation, Hess's Law
- Reaction mechanisms: SN1, SN2, nucleophilic substitution, electrophilic addition, redox half-reactions
- Chemical kinetics: rate laws, activation energy, Arrhenius equation
- Coordination chemistry, crystal field theory, ligand field theory
- Qualitative analysis: cation/anion group tests
Key constants you know:
  Ka(CH₃COOH)=1.8e-5, pKa=4.76 | Kb(NH₃)=1.8e-5 | Ksp(AgCl)=1.8e-10 | Ksp(BaSO₄)=1.1e-10
  Ksp(Fe(OH)₃)=2.8e-39 | Ksp(Cu(OH)₂)=2.2e-20
  E°(MnO₄⁻/Mn²⁺)=+1.51V | E°(Cr₂O₇²⁻/Cr³⁺)=+1.33V | E°(Fe³⁺/Fe²⁺)=+0.77V | E°(I₂/I⁻)=+0.54V
  ΔH_neutralisation(strong-strong)=-57.3 kJ/mol
Always give step-by-step explanations. Use equations where helpful. Keep answers focused and university-level accurate.
If asked about a reaction in the lab, use the context provided."""

def ask_scholar(question: str, context: str = "") -> str:
    client = get_client()
    messages = []
    for msg in st.session_state.chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": f"{context}\n\nStudent question: {question}" if context else question})
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SCHOLAR_SYSTEM,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"Scholar is temporarily unavailable: {str(e)}"

# ─────────────────────────────────────────────
# HELPER: BEAKER SVG RENDERER
# ─────────────────────────────────────────────
def build_beaker_svg(contents, mixed=False, effervescence=False, precipitate=False, result_color=None):
    """Renders a layered/mixed beaker as SVG."""
    W, H = 220, 280
    bx, by = 30, 40      # beaker inner top-left
    bw, bh = 160, 200    # beaker inner dimensions
    max_vol = 500        # mL for full beaker

    total_vol = sum(c.get("volume", 30) for c in contents)
    fill_frac = min(total_vol / max_vol, 0.9)
    fill_px   = int(fill_frac * bh)
    fill_y    = by + bh - fill_px

    svg_layers = []

    if mixed and result_color:
        # Single mixed colour
        svg_layers.append(
            f'<rect x="{bx}" y="{fill_y}" width="{bw}" height="{fill_px}" '
            f'fill="{result_color}" opacity="0.85" rx="2"/>'
        )
    elif contents:
        # Layered display
        cumulative = 0
        for ch in reversed(contents):  # bottom layers first
            vol = ch.get("volume", 30)
            frac = vol / total_vol if total_vol > 0 else 0
            layer_h = max(int(frac * fill_px), 4)
            layer_y = by + bh - cumulative - layer_h
            color = ch.get("color", "#c0d8f0")
            name  = ch.get("name","")[:18]
            svg_layers.append(
                f'<rect x="{bx}" y="{layer_y}" width="{bw}" height="{layer_h}" '
                f'fill="{color}" opacity="0.82" rx="2"/>'
            )
            # layer label
            if layer_h > 14:
                svg_layers.append(
                    f'<text x="{bx+bw//2}" y="{layer_y + layer_h//2 + 5}" '
                    f'text-anchor="middle" font-size="10" fill="#e0f2fe" '
                    f'font-family="Space Grotesk" opacity="0.9">{name}</text>'
                )
            cumulative += layer_h

    # Precipitate layer at bottom
    if precipitate and mixed:
        ppt_h = 22
        svg_layers.append(
            f'<rect x="{bx}" y="{by+bh-ppt_h}" width="{bw}" height="{ppt_h}" '
            f'fill="#f8fafc" opacity="0.95" rx="2"/>'
        )
        svg_layers.append(
            f'<text x="{bx+bw//2}" y="{by+bh-8}" text-anchor="middle" '
            f'font-size="9" fill="#334155" font-family="Space Grotesk">↓ precipitate</text>'
        )

    # Bubble animation
    bubbles = ""
    if effervescence and mixed:
        for i in range(8):
            cx = bx + 20 + (i * 18) % (bw - 20)
            dur = 1.2 + (i % 4) * 0.3
            delay = (i * 0.25) % 1.5
            bubbles += (
                f'<circle cx="{cx}" cy="{by+bh-10}" r="4" fill="none" '
                f'stroke="#7dd3fc" stroke-width="1.5" opacity="0.8">'
                f'<animate attributeName="cy" values="{by+bh-10};{fill_y+10}" '
                f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.8;0" '
                f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="4;7" '
                f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>'
                f'</circle>'
            )

    # Surface sheen
    sheen = ""
    if contents or (mixed and result_color):
        sheen = (
            f'<rect x="{bx}" y="{fill_y}" width="{bw}" height="6" '
            f'fill="white" opacity="0.18" rx="2"/>'
        )

    layers_str = "\n".join(svg_layers)

    svg = f"""
<svg width="{W}" height="{H+20}" viewBox="0 0 {W} {H+20}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <clipPath id="beakerClip">
      <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4"/>
    </clipPath>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Beaker background -->
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#0a1628" rx="4" stroke="#1e3a5f" stroke-width="1.5"/>

  <!-- Liquid layers (clipped) -->
  <g clip-path="url(#beakerClip)">
    {layers_str}
    {sheen}
    {bubbles}
  </g>

  <!-- Beaker glass outline -->
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" rx="4"
        stroke="#3b82f6" stroke-width="2.5" opacity="0.7"/>
  <!-- Glass highlight left -->
  <rect x="{bx+4}" y="{by+8}" width="6" height="{bh-20}" fill="white" opacity="0.07" rx="3"/>

  <!-- Beaker spout (top left notch) -->
  <path d="M {bx-2},{by} Q {bx-8},{by-12} {bx-4},{by-16}" stroke="#3b82f6" stroke-width="2"
        fill="none" opacity="0.5"/>

  <!-- ml markings -->
  {"".join([f'<line x1="{bx+bw-16}" y1="{by+int(bh*i/5)}" x2="{bx+bw-4}" y2="{by+int(bh*i/5)}" stroke="#1e40af" stroke-width="1"/><text x="{bx+bw-28}" y="{by+int(bh*i/5)+4}" font-size="8" fill="#3b82f6" font-family="JetBrains Mono">{500-i*100}</text>' for i in range(6)])}

  <!-- Volume indicator label -->
  <text x="{bx+bw//2}" y="{H+14}" text-anchor="middle" font-size="11" fill="#60a5fa"
        font-family="Space Grotesk">{int(total_vol)} mL total</text>

  <!-- Title glow lines -->
  <line x1="{bx}" y1="{by-6}" x2="{bx+bw}" y2="{by-6}" stroke="#1e40af" stroke-width="0.5" opacity="0.5"/>
</svg>
"""
    return svg


# ─────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────
def page_login():
    col_a, col_b, col_c = st.columns([1, 1.6, 1])
    with col_b:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## ⚗️ Virtual Chemistry Lab")
        st.markdown("<p style='color:#64748b;font-size:14px;'>University-level interactive simulations</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤 Student ID / Name", placeholder="e.g. chem_student_01")
            password = st.text_input("🔒 Password", type="password", placeholder="any password for demo")
            submitted = st.form_submit_button("Enter the Lab →", use_container_width=True)
            if submitted:
                if username.strip():
                    st.session_state.logged_in = True
                    st.session_state.username  = username.strip()
                    st.session_state.page      = "lab"
                    st.rerun()
                else:
                    st.error("Please enter your student ID.")
        st.markdown("<p style='color:#334155;font-size:12px;text-align:center;margin-top:20px;'>Demo version — any credentials accepted</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: LAB
# ─────────────────────────────────────────────
def page_lab():
    # ── SIDEBAR ─────────────────────────────
    with st.sidebar:
        st.markdown(f"### ⚗️ VChem Lab")
        st.markdown(f"<span style='color:#60a5fa;font-size:13px;'>👤 {st.session_state.username}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#4ade80;font-size:12px;'>🧪 Experiments: {st.session_state.experiments_done} | 📝 Quiz: {st.session_state.quiz_done}</span>", unsafe_allow_html=True)
        st.markdown("---")

        nav = st.radio("Navigate", ["🧪 Lab Bench", "📝 Quiz", "📊 Session Log"], label_visibility="collapsed")
        st.session_state.lab_nav = nav
        st.markdown("---")

        if nav == "🧪 Lab Bench":
            st.markdown("#### Lab Domain")
            st.session_state.lab_domain = st.selectbox(
                "Select Domain",
                ["Volumetric Analysis","Inorganic Qualitative Analysis","Chemical Kinetics","Thermochemistry"],
                label_visibility="collapsed"
            )
            st.markdown("---")
            st.markdown("#### 🌡️ Conditions")
            st.session_state.temperature = st.slider("Temperature (°C)", 0, 120, st.session_state.temperature)
            st.markdown("---")
            st.markdown("#### Add Reagents (max 5)")

            if len(st.session_state.beaker_contents) < 5:
                sel_chem = st.selectbox("Select reagent", ["— choose —"] + CHEMICAL_NAMES, label_visibility="collapsed")
                vol = st.number_input("Volume (mL)", min_value=1, max_value=250, value=30)
                conc = st.number_input("Concentration (M)", min_value=0.001, max_value=18.0, value=1.0, step=0.1)

                if st.button("➕ Add to Beaker", use_container_width=True):
                    if sel_chem != "— choose —":
                        chem = CHEMICALS[sel_chem]
                        st.session_state.beaker_contents.append({
                            "name": sel_chem.split("(")[0].strip(),
                            "full_name": sel_chem,
                            "color": chem["hex"],
                            "volume": vol,
                            "conc": conc,
                            "type": chem["type"],
                        })
                        st.session_state.mixed = False
                        st.session_state.reaction_result = None
                        st.session_state.show_theory = False
                        st.rerun()
                    else:
                        st.warning("Choose a reagent first.")
            else:
                st.info("Maximum 5 reagents reached.")

            if st.session_state.beaker_contents:
                st.markdown("**Contents:**")
                for i, c in enumerate(st.session_state.beaker_contents):
                    badge_class = f"badge-{c['type']}" if c['type'] in ['acid','base','salt','oxidizer','indicator'] else 'badge-salt'
                    st.markdown(
                        f"<span class='badge {badge_class}'>{c['name']} {c['volume']}mL</span>",
                        unsafe_allow_html=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔬 Mix Reagents", use_container_width=True, type="primary"):
                    do_mix()
                if st.button("🗑️ Clear Beaker", use_container_width=True):
                    st.session_state.beaker_contents = []
                    st.session_state.mixed = False
                    st.session_state.reaction_result = None
                    st.session_state.show_theory = False
                    st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    # ── MAIN PANEL ───────────────────────────
    nav = st.session_state.get("lab_nav", "🧪 Lab Bench")

    if nav == "🧪 Lab Bench":
        render_lab_bench()
    elif nav == "📝 Quiz":
        render_quiz()
    else:
        render_session_log()


def do_mix():
    if not st.session_state.beaker_contents:
        return
    names_in = frozenset(c["full_name"] for c in st.session_state.beaker_contents)
    # Try exact match
    result = REACTIONS.get(names_in)
    # Try subset match (2-reagent reactions within larger set)
    if not result:
        for key, val in REACTIONS.items():
            if key.issubset(names_in) and len(key) >= 2:
                result = val
                break
    st.session_state.mixed = True
    st.session_state.reaction_result = result
    st.session_state.show_theory = False
    st.session_state.experiments_done += 1


def render_lab_bench():
    result = st.session_state.reaction_result
    mixed  = st.session_state.mixed
    contents = st.session_state.beaker_contents

    # ── 3-column layout ──────────────────────
    col_vessel, col_info, col_chat = st.columns([1.1, 1.4, 1.2])

    with col_vessel:
        st.markdown(f"### 🧪 {st.session_state.lab_domain}")
        domain_icon = {"Volumetric Analysis":"🧫","Inorganic Qualitative Analysis":"🔬",
                       "Chemical Kinetics":"⏱️","Thermochemistry":"🌡️"}
        d = st.session_state.lab_domain
        st.markdown(f"<span style='color:#60a5fa;font-size:12px;'>{domain_icon.get(d,'⚗️')} Temp: {st.session_state.temperature}°C</span>", unsafe_allow_html=True)

        eff  = result["effervescence"] if result else False
        ppt  = result["precipitate"]   if result else False
        rcol = result["result_color"]  if result else None

        svg = build_beaker_svg(
            contents, mixed=mixed,
            effervescence=eff,
            precipitate=ppt,
            result_color=rcol if mixed else None
        )
        st.markdown(f'<div class="beaker-wrap">{svg}</div>', unsafe_allow_html=True)

        if mixed and result:
            obs_col = result.get("result_color","#f1f5f9")
            st.markdown(f"""
<div class="lab-card" style="margin-top:10px;">
  <p style="font-size:12px;color:#94a3b8;">Observation</p>
  <p style="font-size:13px;color:#e2e8f0;">{result['observation']}</p>
  {'<p style="color:#67e8f9;font-size:12px;">🫧 Effervescence detected</p>' if eff else ''}
  {'<p style="color:#a5f3fc;font-size:12px;">⬇ Precipitate formed</p>' if ppt else ''}
  {'<p style="color:#86efac;font-size:12px;">🎨 Colour change: see beaker</p>' if result.get("color_change") else ''}
</div>""", unsafe_allow_html=True)
        elif not contents:
            st.markdown("<p style='color:#334155;font-size:13px;text-align:center;margin-top:20px;'>← Add reagents from the sidebar</p>", unsafe_allow_html=True)
        elif not mixed:
            st.markdown("<p style='color:#60a5fa;font-size:13px;text-align:center;margin-top:12px;'>← Click Mix Reagents to simulate</p>", unsafe_allow_html=True)

    with col_info:
        st.markdown("### 📋 Reaction Analysis")

        if mixed and result:
            st.markdown(f"#### {result['name']}")
            st.markdown(f"<div class='reaction-box'>⚖️ {result['equation']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='reaction-box'>🔹 Net Ionic: {result['net_ionic']}</div>", unsafe_allow_html=True)
            if result.get("delta_H"):
                st.markdown(f"<div class='reaction-box'>🌡️ ΔH = {result['delta_H']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='reaction-box'>⚙️ Mechanism: {result['mechanism']}</div>", unsafe_allow_html=True)

            if st.button("📖 Show Theory", use_container_width=True):
                st.session_state.show_theory = not st.session_state.show_theory

            if st.session_state.show_theory:
                st.markdown(f"<div class='theory-box'>{result['theory']}</div>", unsafe_allow_html=True)
                # Chemical data for each reactant
                st.markdown("**Reagent Data:**")
                for c in contents:
                    chem = CHEMICALS.get(c["full_name"])
                    if chem:
                        st.markdown(f"""<div class='lab-card' style='padding:10px;'>
<b style='color:#7dd3fc;'>{c['full_name'].split('(')[0]}</b>
<span style='color:#64748b;font-size:12px;'> M={chem['molar_mass']} g/mol | ρ={chem.get('density','?')} g/cm³</span>
<p style='font-size:12px;color:#94a3b8;margin-top:4px;'>{chem['description']}</p>
</div>""", unsafe_allow_html=True)

        elif mixed and not result:
            st.markdown("""<div class='lab-card'>
<p style='color:#f59e0b;'>⚠️ No specific reaction found in the database for this combination.</p>
<p style='color:#94a3b8;font-size:13px;'>The reagents may coexist without a notable reaction, or this combination is beyond the current database. Ask Scholar in the chat!</p>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div class='lab-card'><p style='color:#334155;'>Reaction details will appear here after mixing.</p></div>", unsafe_allow_html=True)

            # Show available reaction hints
            st.markdown("**💡 Try these combinations:**")
            hints = [
                "HCl + NaOH (Neutralisation)",
                "KMnO₄ + Oxalic Acid (Redox Titration)",
                "AgNO₃ + HCl (Halide Test)",
                "CuSO₄ + NH₃ (Complex Formation)",
                "FeCl₃ + NaOH (Precipitation)",
            ]
            for h in hints:
                st.markdown(f"<p style='color:#475569;font-size:12px;'>• {h}</p>", unsafe_allow_html=True)

    with col_chat:
        st.markdown("### 🤖 Scholar Agent")
        st.markdown("<p style='color:#475569;font-size:12px;'>Your AI chemistry tutor</p>", unsafe_allow_html=True)

        chat_container = st.container()
        with chat_container:
            # Display history (last 8 messages)
            for msg in st.session_state.chat_history[-8:]:
                role_class = "chat-msg-user" if msg["role"] == "user" else "chat-msg-ai"
                role_label = "You" if msg["role"] == "user" else "Scholar"
                st.markdown(
                    f"<div class='{role_class}'><b>{role_label}:</b> {msg['content']}</div>",
                    unsafe_allow_html=True
                )

        with st.form("chat_form", clear_on_submit=True):
            user_q = st.text_area("Ask Scholar...", placeholder="e.g. Why does KMnO₄ decolourise?", height=80, label_visibility="collapsed")
            send_btn = st.form_submit_button("Send 📨", use_container_width=True)

            if send_btn and user_q.strip():
                # Build context from current reaction
                ctx = ""
                if st.session_state.reaction_result:
                    r = st.session_state.reaction_result
                    ctx = f"Current lab reaction: {r['name']}. Equation: {r['equation']}. Observation: {r['observation']}."
                elif st.session_state.beaker_contents:
                    names = ", ".join(c["full_name"] for c in st.session_state.beaker_contents)
                    ctx = f"Student has these reagents in beaker: {names}."

                st.session_state.chat_history.append({"role": "user", "content": user_q})
                with st.spinner("Scholar thinking..."):
                    answer = ask_scholar(user_q, ctx)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: QUIZ
# ─────────────────────────────────────────────
def render_quiz():
    st.markdown("## 📝 Chemistry Quiz")
    st.markdown(f"<p style='color:#60a5fa;'>Score: {st.session_state.quiz_score} / {st.session_state.quiz_idx} answered</p>", unsafe_allow_html=True)

    order = st.session_state.quiz_questions_order
    idx   = st.session_state.quiz_idx % len(QUIZ_QUESTIONS)
    q_data = QUIZ_QUESTIONS[order[idx]]

    st.markdown(f"<div class='lab-card'><b style='color:#7dd3fc;'>Q{st.session_state.quiz_idx+1}.</b> <span style='color:#e2e8f0;font-size:15px;'> {q_data['q']}</span></div>", unsafe_allow_html=True)

    for i, opt in enumerate(q_data["opts"]):
        if not st.session_state.quiz_answered:
            if st.button(f"  {opt}", key=f"opt_{i}", use_container_width=True):
                st.session_state.quiz_answered = True
                st.session_state.quiz_selected = i
                if i == q_data["ans"]:
                    st.session_state.quiz_score += 1
                st.rerun()
        else:
            if i == q_data["ans"]:
                st.markdown(f"<div class='quiz-opt correct'>✅ {opt}</div>", unsafe_allow_html=True)
            elif i == st.session_state.quiz_selected and i != q_data["ans"]:
                st.markdown(f"<div class='quiz-opt wrong'>❌ {opt}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='quiz-opt'>{opt}</div>", unsafe_allow_html=True)

    if st.session_state.quiz_answered:
        st.markdown(f"<div class='theory-box'>💡 <b>Explanation:</b> {q_data['exp']}</div>", unsafe_allow_html=True)
        if st.button("Next Question →", use_container_width=True, type="primary"):
            st.session_state.quiz_idx      += 1
            st.session_state.quiz_done     += 1
            st.session_state.quiz_answered  = False
            st.session_state.quiz_selected  = None
            if st.session_state.quiz_idx % len(QUIZ_QUESTIONS) == 0:
                random.shuffle(st.session_state.quiz_questions_order)
            st.rerun()


# ─────────────────────────────────────────────
# PAGE: SESSION LOG
# ─────────────────────────────────────────────
def render_session_log():
    st.markdown("## 📊 Session Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Experiments Done", st.session_state.experiments_done)
    c2.metric("Quiz Questions", st.session_state.quiz_done)
    c3.metric("Quiz Score", f"{st.session_state.quiz_score}/{st.session_state.quiz_done}" if st.session_state.quiz_done else "—")

    st.markdown("---")
    st.markdown("### 🧪 Available Reactions in Database")
    for key, val in REACTIONS.items():
        reactants_str = " + ".join(list(key))
        st.markdown(f"""<div class='lab-card'>
<b style='color:#7dd3fc;'>{val['name']}</b><br>
<span style='color:#64748b;font-size:12px;'>{reactants_str}</span><br>
<span style='color:#94a3b8;font-size:12px;'>{val['equation']}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧬 Full Reagent Catalogue")
    for name, data in CHEMICALS.items():
        badge_class = f"badge-{data['type']}" if data['type'] in ['acid','base','salt','oxidizer','indicator'] else 'badge-salt'
        st.markdown(f"""<div class='lab-card' style='padding:10px;'>
<span class='badge {badge_class}'>{data['type'].upper()}</span>
<b style='color:#bfdbfe;'> {name}</b>
<p style='color:#64748b;font-size:12px;margin:4px 0 0 0;'>{data['description']}</p>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    page_login()
else:
    page_lab()
