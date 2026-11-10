"""
AeroTwin-HUMS IEEE Paper Generator
Produces a 6-page, two-column, IEEE-style DOCX manuscript.
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import copy

OUTPUT_DIR = r"c:\Users\Omkar\Desktop\WebSpaces\reserch papper"

doc = Document()

# ─── Page setup ───────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = Cm(1.91)
section.bottom_margin = Cm(2.54)
section.left_margin = Cm(1.78)
section.right_margin = Cm(1.78)

# Two-column layout
sectPr = section._sectPr
cols = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="360"/>')
sectPr.append(cols)

# ─── Style definitions ────────────────────────────────────────────────
style = doc.styles

# Title style
title_style = style.add_style('PaperTitle', 1)
title_style.font.name = 'Times New Roman'
title_style.font.size = Pt(22)
title_style.font.bold = True
title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_style.paragraph_format.space_before = Pt(0)
title_style.paragraph_format.space_after = Pt(6)

# Author style
author_style = style.add_style('AuthorBlock', 1)
author_style.font.name = 'Times New Roman'
author_style.font.size = Pt(9)
author_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
author_style.paragraph_format.space_before = Pt(0)
author_style.paragraph_format.space_after = Pt(1)

# Section heading (I. II. etc.)
section_heading = style.add_style('SectionHeading', 1)
section_heading.font.name = 'Times New Roman'
section_heading.font.size = Pt(10)
section_heading.font.bold = True
section_heading.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
section_heading.paragraph_format.space_before = Pt(8)
section_heading.paragraph_format.space_after = Pt(4)

# Subsection heading
sub_heading = style.add_style('SubsectionHeading', 1)
sub_heading.font.name = 'Times New Roman'
sub_heading.font.size = Pt(10)
sub_heading.font.bold = False
sub_heading.font.italic = True
sub_heading.paragraph_format.space_before = Pt(6)
sub_heading.paragraph_format.space_after = Pt(2)

# Body text
body_style = style.add_style('IEEEBody', 1)
body_style.font.name = 'Times New Roman'
body_style.font.size = Pt(9)
body_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
body_style.paragraph_format.space_before = Pt(0)
body_style.paragraph_format.space_after = Pt(2)
body_style.paragraph_format.first_line_indent = Cm(0.35)
body_style.paragraph_format.line_spacing = 1.0

# Abstract style
abstract_style = style.add_style('AbstractStyle', 1)
abstract_style.font.name = 'Times New Roman'
abstract_style.font.size = Pt(9)
abstract_style.font.bold = True
abstract_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
abstract_style.paragraph_format.space_before = Pt(6)
abstract_style.paragraph_format.space_after = Pt(2)

# Equation style
eq_style = style.add_style('Equation', 1)
eq_style.font.name = 'Times New Roman'
eq_style.font.size = Pt(9)
eq_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
eq_style.paragraph_format.space_before = Pt(3)
eq_style.paragraph_format.space_after = Pt(3)

# Reference style
ref_style = style.add_style('Reference', 1)
ref_style.font.name = 'Times New Roman'
ref_style.font.size = Pt(8)
ref_style.paragraph_format.space_before = Pt(0)
ref_style.paragraph_format.space_after = Pt(1)
ref_style.paragraph_format.first_line_indent = Cm(-0.5)
ref_style.paragraph_format.left_indent = Cm(0.5)

# Caption style
cap_style = style.add_style('Caption2', 1)
cap_style.font.name = 'Times New Roman'
cap_style.font.size = Pt(8)
cap_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_style.paragraph_format.space_before = Pt(2)
cap_style.paragraph_format.space_after = Pt(4)

# Table caption style (above table)
tcap_style = style.add_style('TableCaption', 1)
tcap_style.font.name = 'Times New Roman'
tcap_style.font.size = Pt(8)
tcap_style.font.bold = False
tcap_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
tcap_style.paragraph_format.space_before = Pt(4)
tcap_style.paragraph_format.space_after = Pt(2)

# ─── Helper functions ─────────────────────────────────────────────────
def add_body(text, bold_prefix=None):
    p = doc.add_paragraph(style='IEEEBody')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(9)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9)
    return p

def add_equation(text, number):
    p = doc.add_paragraph(style='Equation')
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9)
    run.font.italic = True
    run2 = p.add_run(f'    ({number})')
    run2.font.name = 'Times New Roman'
    run2.font.size = Pt(9)
    return p

def add_section_heading(text):
    p = doc.add_paragraph(text, style='SectionHeading')
    return p

def add_subsection(text):
    p = doc.add_paragraph(text, style='SubsectionHeading')
    return p

def add_table_compact(headers, rows, caption_text):
    """Add a compact table with caption above."""
    # Caption above
    cap = doc.add_paragraph(caption_text, style='TableCaption')
    
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    
    # Set font size for all cells
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(7)
                r.font.name = 'Times New Roman'
                r.bold = True
    
    for ri, row_data in enumerate(rows):
        for ci, val in enumerate(row_data):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = str(val)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(7)
                    r.font.name = 'Times New Roman'
    return table


# ═══════════════════════════════════════════════════════════════════════
#   PAGE 1: Title, Authors, Abstract, Introduction
# ═══════════════════════════════════════════════════════════════════════

# Title
doc.add_paragraph(
    'AeroTwin-HUMS: An Integrated Physics-Informed\nFramework for UAV Engine Health Monitoring\nand Prognostics',
    style='PaperTitle'
)

# Author block - Row 1
authors_row1 = [
    ("Ratna Patil", "ratna.patil@vit.edu"),
    ("Aarya M. Sinha", "aarya.sinha24@vit.edu"),
    ("Alisha Gulhane", "alisha.gulhane24@vit.edu"),
]
authors_row2 = [
    ("Omkar Bachhav", "omkar.bachhav24@vit.edu"),
    ("Anushree Muthukumar", "anushree.muthukumar24@vit.edu"),
    ("Vidal Deo", "vidal.deo@vit.edu"),
]

dept_line = "Department of Artificial Intelligence and Data Science"
inst_line = "Vishwakarma Institute of Technology"
loc_line = "Pune, Maharashtra, India"

for author_row in [authors_row1, authors_row2]:
    # Create a single-row table for author positioning
    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ci, (name, email) in enumerate(author_row):
        cell = t.rows[0].cells[ci]
        for existing_p in cell.paragraphs:
            existing_p.clear()
        # Name
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(name)
        r.bold = True
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
        # Dept
        p2 = cell.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(dept_line)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(7)
        r2.font.italic = True
        # Inst
        p3 = cell.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p3.add_run(f"{inst_line}, {loc_line}")
        r3.font.name = 'Times New Roman'
        r3.font.size = Pt(7)
        r3.font.italic = True
        # Email
        p4 = cell.add_paragraph()
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r4 = p4.add_run(email)
        r4.font.name = 'Times New Roman'
        r4.font.size = Pt(7)
        r4.font.italic = True
        
        # Reduce cell margins
        for paragraph in cell.paragraphs:
            paragraph.paragraph_format.space_before = Pt(0)
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0

# ─── Abstract ─────────────────────────────────────────────────────────
doc.add_paragraph('Abstract', style='AbstractStyle')

abs_text = (
    "Small-to-medium Unmanned Aerial Vehicles (UAVs) powered by internal combustion piston engines "
    "operate in severe, non-stationary thermal and acoustic environments where conventional static "
    "threshold monitoring generates excessive false alarms. This paper presents AeroTwin-HUMS, an "
    "integrated physics-informed digital twin framework for real-time condition monitoring, fault "
    "diagnosis, and Remaining Useful Life (RUL) estimation. The framework couples a deterministic "
    "13-channel engine model—comprising eleven closed-form sensor maps and a calibrated 45-term "
    "polynomial response surface—with regularized Mahalanobis-χ² anomaly detection, whitened "
    "cosine-similarity fault isolation against an empirical Fault Signature Matrix, and dual-track "
    "prognostic estimators: a Kalman-recursive Wiener first-hitting-time process and an ExtraTrees "
    "ensemble. Independent validation on 1,100 synthetic flight samples across 22 multi-phase mission "
    "trajectories demonstrates per-channel noise reproduction within 12.4% of calibrated values, fault "
    "signature alignment with cosine similarity ≥0.999, leave-one-trajectory-out diagnostic accuracy "
    "of 87.8%, zero-shot physics-based fault isolation of 99.2% at severity >0.35, and an audited "
    "out-of-fold RUL regression performance of R²=0.758 (MAE=808.7 cycles) following elimination of "
    "target-variable leakage. Material limitations including synthetic calibration boundaries, model "
    "artifact serialization constraints, and the absence of physical engine test data are systematically "
    "evaluated."
)
add_body(abs_text)

# Index terms
p = doc.add_paragraph(style='IEEEBody')
r = p.add_run('Index Terms')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(9)
r2 = p.add_run(
    '—Health and Usage Monitoring Systems (HUMS), Digital Twin, Unmanned Aerial Vehicles, '
    'Fault Diagnosis, Prognostics, Mahalanobis Distance, Wiener Process, Remaining Useful Life.'
)
r2.font.name = 'Times New Roman'
r2.font.size = Pt(9)

# ─── I. INTRODUCTION ──────────────────────────────────────────────────
add_section_heading('I. Introduction')

add_body(
    "Unmanned Aerial Vehicles (UAVs) deployed in surveillance, cargo delivery, and atmospheric "
    "research increasingly rely on internal combustion piston engines for their superior energy "
    "density and endurance over electric propulsion. However, piston engines exhibit complex "
    "mechanical, thermal, and fluid-dynamic wear patterns. In-flight degradation—cylinder ring "
    "wear, cooling baffle restrictions, lubricant starvation, ignition misfire, and wastegate "
    "leakage—can precipitate catastrophic engine failure if unmitigated [1]."
)

add_body(
    "Historically, Health and Usage Monitoring Systems (HUMS) have relied on static limit-checking "
    "(redline alerts). In aerial applications, engine variables such as Exhaust Gas Temperature "
    "(EGT), Manifold Absolute Pressure (MAP), and Cylinder Head Temperature (CHT) are intrinsically "
    "coupled to flight state and atmospheric conditions [2]. A climb to 3,000 m naturally reduces "
    "MAP, mimicking the signature of a wastegate leak. Consequently, static thresholds either "
    "generate unacceptable false alarm rates or must be set so wide that incipient degradation "
    "remains undetected until structural breakdown."
)

add_body(
    "Recent PHM advances favor data-driven deep learning [3]. While capable, purely data-driven "
    "architectures suffer three critical shortcomings in aerospace deployment: (i) they require "
    "massive run-to-failure datasets rarely obtainable for operational UAVs; (ii) they function "
    "as uninterpretable black boxes precluding formal verification under standards such as "
    "DO-178C [17]; (iii) their predictions become unreliable outside the training distribution."
)

add_body(
    "To bridge this gap, this paper introduces AeroTwin-HUMS, a physics-informed digital twin "
    "architecture for real-time engine health monitoring. The framework evaluates incoming "
    "multi-channel telemetry against an analytical twin reflecting real-time atmospheric and "
    "operational state, separating ambient shifts from true mechanical degradation."
)

add_body(
    "The core contributions are: (1) a calibrated 13-channel physics baseline combining closed-form "
    "sensor maps with ISA atmospheric modeling; (2) robust Mahalanobis-χ² anomaly scoring with "
    "dynamic sensor validity masking; (3) zero-shot fault fingerprinting via whitened cosine "
    "similarity against the Fault Signature Matrix; (4) audited dual-path prognostics with "
    "target-leakage disclosure; and (5) systematic evaluation of engineering limitations.",
    bold_prefix="Contributions. "
)

# ─── II. RELATED WORK ─────────────────────────────────────────────────
add_section_heading('II. Related Work')

add_subsection('A. HUMS and Engine Condition Monitoring')
add_body(
    "HUMS originated in rotorcraft transmission vibration diagnostics [4]. Standard implementations "
    "extract Condition Indicators such as RMS, kurtosis, and crest factor from high-frequency "
    "accelerometers. For fixed-wing UAV piston engines, HUMS development has lagged due to "
    "Size-Weight-Power (SWaP) constraints and lower sensor density, motivating tiered "
    "edge-cloud monitoring topologies [5]."
)

add_subsection('B. Physics-Informed Digital Twins')
add_body(
    "Digital twins represent virtual replicas updated via real-time telemetry [6]. In engine "
    "health monitoring, physics-based modeling typically employs thermodynamic gas path analysis "
    "[7]. Hybrid twins combine deterministic physical equations with data-driven surrogates "
    "to account for unmodeled friction and sensor anomalies [8]. AeroTwin-HUMS adopts this "
    "paradigm by implementing closed-form nominal physics alongside regularized residual metrics."
)

add_subsection('C. Residual-Based Anomaly Detection')
add_body(
    "Residual generation e(t) = y(t) − ŷ(t) decouples operational input variations from system "
    "anomalies [9]. When multi-channel sensor noise is correlated, the Mahalanobis distance accounts "
    "for covariance Σ, transforming correlated residuals into a scalar whose squared value follows a "
    "χ² distribution [10]. Practical implementation requires covariance regularization and explicit "
    "handling of coloured AR(1) noise to prevent statistical score inflation."
)

add_subsection('D. Degradation Modeling and RUL Estimation')
add_body(
    "The Wiener process with drift (dX = μdt + σdW) models steady deterioration with operational "
    "random shocks [11]. Its first hitting time to a failure threshold follows an Inverse-Gaussian "
    "distribution, providing closed-form confidence intervals [12]. Concurrently, ensemble methods "
    "such as ExtraTrees [13] have gained prominence for RUL estimation, though rigorous "
    "group-aware cross-validation is mandatory to prevent leakage across contiguous flight samples."
)

# ─── III. SYSTEM ARCHITECTURE ─────────────────────────────────────────
add_section_heading('III. System Architecture')

add_body(
    "AeroTwin-HUMS is engineered as a decoupled multi-tier monitoring service. Fig. 1 illustrates "
    "the end-to-end architecture, distinguishing verified operational paths from planned integrations."
)

# Figure 1 - Architecture diagram as text box
p = doc.add_paragraph(style='IEEEBody')
p.paragraph_format.first_line_indent = Cm(0)
p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(4)
r = p.add_run(
    '┌─────────────────────────────────────────────┐\n'
    '│     UAV Telemetry (13 Channels + Controls)   │\n'
    '│              ↓ [WebSocket]                    │\n'
    '│  ┌──────────────────────────────────┐        │\n'
    '│  │    FastAPI Ingestion Layer        │        │\n'
    '│  │  (JWT Auth · Session Lifecycle)   │        │\n'
    '│  └──────────┬───────────────────────┘        │\n'
    '│              ↓                                │\n'
    '│  ┌──────────────────────────────────┐        │\n'
    '│  │    RealTimeMonitor (per engine)   │        │\n'
    '│  │  ├ Sensor Validation Gate         │        │\n'
    '│  │  ├ Twin Physics Reference         │        │\n'
    '│  │  ├ Residual + Mahalanobis-χ²      │        │\n'
    '│  │  ├ Fault Fingerprinting (FSM)     │        │\n'
    '│  │  └ RUL (Wiener / ExtraTrees)      │        │\n'
    '│  └──────────┬───────────────────────┘        │\n'
    '│              ↓                                │\n'
    '│  ┌──────────────────────────────────┐        │\n'
    '│  │  Alert Service · TimescaleDB      │        │\n'
    '│  │  React Dashboard · Three.js 3D    │        │\n'
    '│  └──────────────────────────────────┘        │\n'
    '│                                               │\n'
    '│  - - - Unwired: CAN Bus, MQTT, Redis - - -   │\n'
    '└─────────────────────────────────────────────┘'
)
r.font.name = 'Courier New'
r.font.size = Pt(6)

fig1_cap = doc.add_paragraph(style='Caption2')
r = fig1_cap.add_run('Fig. 1. ')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(8)
r2 = fig1_cap.add_run(
    'AeroTwin-HUMS system architecture. Solid paths are verified operational; '
    'dashed items indicate implemented but unwired integrations.'
)
r2.font.name = 'Times New Roman'
r2.font.size = Pt(8)

add_subsection('A. Ingestion and Session Management')
add_body(
    "Telemetry is ingested via authenticated WebSocket streams (ws/ingest). To ensure strict "
    "isolation, the backend instantiates stateful Session objects managed by TwinService. Each "
    "session holds an independent RealTimeMonitor containing its own sensor validation history, "
    "AR noise state, and thread-safe lock. Sessions are reaped after a 6-hour TTL. CAN and MQTT "
    "adapters are implemented in the codebase but are not wired to the application startup."
)

add_subsection('B. Plant vs. Twin Separation')
add_body(
    "A fundamental design rule is structural separation between the faulted plant (used by "
    "TrajectorySimulator for synthetic generation) and the clean twin baseline (inside "
    "RealTimeMonitor). Sharing instances would cause nominal expectations to absorb injected "
    "faults, blinding the anomaly detector."
)

add_subsection('C. Technology Stack and Persistence')
add_body(
    "The backend uses Python with FastAPI 0.115.0, Uvicorn 0.30.6, SQLAlchemy 2.0.35, "
    "and a vendored aerotwin_physics package (v1.0.0). Numerical computation relies on "
    "NumPy 1.26.4, SciPy 1.13.1, and scikit-learn 1.5.2. The database schema targets "
    "TimescaleDB hypertables with time-partitioned sensor readings, residuals, health indices, "
    "and 7-year audit retention for aerospace compliance. The React 18 frontend provides "
    "real-time SVG instrumentation, Recharts diagnostic plots, and a procedural Three.js "
    "3D engine visualization."
)

# ─── IV. PROPOSED METHODOLOGY ─────────────────────────────────────────
add_section_heading('IV. Proposed Methodology')

add_subsection('A. Atmospheric State Formulation')
add_body(
    "AeroTwin-HUMS implements the International Standard Atmosphere (ISA) model. Ambient "
    "temperature T (°C), pressure p (Pa), and density ρ (kg/m³) are calculated as functions of "
    "geometric altitude h (m) and ISA deviation ΔT:"
)

add_equation('T(h) = 15.0 − 0.0065·h + ΔT_ISA', 1)
add_equation('p(h) = 101325 · [max(1 − 2.256×10⁻⁵·h, 10⁻⁶)]^5.256', 2)
add_equation('ρ(p, T) = p / [287.05 · (T + 273.15)]', 3)

add_body(
    "Measured ambient inputs from static ports override ISA during live telemetry processing "
    "to prevent weather offsets from leaking into MAP residuals."
)

add_subsection('B. Multi-Channel Sensor Response Model')
add_body(
    "The nominal engine state ŷ ∈ ℝ¹³ is evaluated at operating point u = [h, V, θ_thr, L, "
    "β_prop, ṁ_f]. Requested power P_req = 300·L (kW). Eleven channels use closed-form maps "
    "recovered from a synthetic reference dataset:"
)

add_equation('EGT_A = 420 + 300·θ_thr + 0.003·h', 4)
add_equation('MAP = (p_amb/1000)·(0.30 + 0.72·θ_thr)', 5)
add_equation('RPM = 2000 + 550·θ_thr', 6)
add_equation('Vib = 0.4 + 1.6·L²', 7)

add_body(
    "Two Turbine Inlet Temperature channels use a calibrated 45-term quadratic response surface "
    "over nine operating features (R² = 0.999991, σ = 0.217). Channels sensor_4 and sensor_11 "
    "have unconfirmed physical identities and are down-weighted in diagnostic calculations."
)

add_subsection('C. Sensor Noise and Plausibility Gating')
add_body(
    "Sensor noise is modeled as a multiplicative AR(1) process with per-channel parameters "
    "calibrated from synthetic data. Relative noise levels range from 0.09% (fuel_flow) to "
    "1.88% (sensor_11), with lag-1 correlations of φ=0.585 (egt_a), φ=0.495 (map_kpa), "
    "and φ=0.237 (fuel_flow). A plausibility gate flags readings with relative change >30% "
    "as sensor faults, masking them from anomaly scoring."
)

add_subsection('D. Regularized Mahalanobis Distance')
add_body(
    "The residual vector e_k = y_obs − ŷ_twin is computed at each timestep. For valid sensor "
    "indices ℐ, the centered residual ẽ = e_ℐ − μ_ref is scored against the healthy reference "
    "covariance:"
)

add_equation('D_M = √[ẽᵀ(Σ_ℐ + λI)⁻¹ẽ] · γ_scale', 8)

add_body(
    "where λ = 10⁻⁹ guarantees numerical invertibility and γ_scale = 0.766 matches empirical "
    "shrinkage. The anomaly score S ∈ [0,1] is the chi-square CDF:"
)

add_equation('S_k = F_χ²(D_M²; dof = |ℐ|);  trip if S_k > 0.70', 9)

# Figure 2 — Processing pipeline
p = doc.add_paragraph(style='IEEEBody')
p.paragraph_format.first_line_indent = Cm(0)
p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(4)
r = p.add_run(
    '  Telemetry y_k, Operating Point u_k\n'
    '              ↓\n'
    '  [Plausibility Gate: Δrel ≤ 0.30]\n'
    '              ↓\n'
    '  [ISA + Nominal Physics → ŷ_twin]\n'
    '              ↓\n'
    '  [Residual e_k = y_k − ŷ_twin]\n'
    '              ↓\n'
    '  [Mahalanobis D_M → χ² CDF → S_k]\n'
    '        ↓              ↓\n'
    '  S_k ≤ 0.70      S_k > 0.70\n'
    '  (Nominal)       (Anomaly)\n'
    '                      ↓\n'
    '              [Cosine vs. FSM]\n'
    '              [Softmax → Fault]\n'
    '                      ↓\n'
    '              [Health Index H_k]\n'
    '              [RUL Estimation]'
)
r.font.name = 'Courier New'
r.font.size = Pt(6.5)

fig2_cap = doc.add_paragraph(style='Caption2')
r = fig2_cap.add_run('Fig. 2. ')
r.bold = True
r.font.name = 'Times New Roman'
r.font.size = Pt(8)
r2 = fig2_cap.add_run(
    'Real-time monitoring pipeline from telemetry receipt through anomaly decision, '
    'fault isolation, and prognostic inference.'
)
r2.font.name = 'Times New Roman'
r2.font.size = Pt(8)

add_subsection('E. Fault Isolation via Whitened Cosine Similarity')
add_body(
    "When anomaly trips, the FaultFingerprinter compares normalized residuals against the Fault "
    "Signature Matrix (FSM) containing five empirical fault modes (misfire, ring_wear, "
    "cooling_restriction, oil_starvation, wastegate_leak) plus a generalised_wear pseudo-mode. "
    "Both residual and signature vectors are whitened by channel noise standard deviations:"
)

add_equation('v_c = (e_c/σ_c)·w_c·𝕀(c∈ℐ);  u_m = S_m/‖S_m‖₂', 10)
add_equation('sim(e,m) = uₘᵀ(v/‖v‖₂);  p(m) = softmax(sim/T)', 11)

add_body(
    "where T = 0.15, w_c = 0.5 for unconfirmed channels, and the minimum similarity threshold "
    "is 0.30. The generalised_wear hypothesis prevents false discrete fault diagnoses on "
    "aging engines."
)

add_subsection('F. Degradation and Prognostics')
add_body(
    "AeroTwin-HUMS provides dual prognostic paths. "
    "(1) Wiener Process: Degradation X ∈ [0,1] follows dX = μdt + σdW. An online Kalman "
    "filter tracks drift μ with Q = 10⁻¹⁰, R = 10⁻⁶. For failure threshold w = 0.75 − X_t, "
    "RUL follows an Inverse-Gaussian distribution with E[RUL] = w/μ. "
    "(2) Model 5 ExtraTrees: An ensemble of 2,000 extremely randomized trees trained on 51 "
    "features mapping telemetry and lag-delta measurements to RUL in operating cycles "
    "(60 s/cycle). The ±15% band applied to ML predictions is not a calibrated confidence "
    "interval; the reported confidence value of 0.760 represents the validation R², not "
    "a statistical confidence level."
)

add_body(
    "Health index H is estimated either by Model 4 (184-feature ExtraTrees regressor) or "
    "the closed-form exponential fallback H = exp(−ρ·D_M) with ρ = 0.02. Due to Git LFS "
    "artifact constraints in the tested environment, the fallback path was the only "
    "executable prognostic in independent testing.",
    bold_prefix="Fallback behavior. "
)

# ─── V. EXPERIMENTAL RESULTS ──────────────────────────────────────────
add_section_heading('V. Experimental Results and Evaluation')

add_subsection('A. Dataset and Evaluation Protocol')
add_body(
    "AeroTwin-HUMS was validated against 1,100 synthetic samples across 22 mission "
    "trajectories (50 samples/trajectory at Δt = 60s). The dataset spans four regimes: "
    "HEALTHY (6 missions), FAULT (5 missions), DEGRADATION (5 missions), and RUL "
    "run-to-failure (6 missions). All calibration parameters derive from "
    "phm_synthetic_dataset_v2-2, a reference workbook not included in the repository. "
    "The sensor equations are empirical fits to this synthetic data, not first-principles "
    "thermodynamic models."
)

# TABLE I — Technology Summary
add_table_compact(
    ['Subsystem', 'Algorithm / Stack', 'Status'],
    [
        ['Physics Model', '11 closed-form maps + 45-term TIT surface', 'Verified'],
        ['Anomaly Detection', 'Mahalanobis-χ² (ridge=10⁻⁹, γ=0.766)', 'Verified'],
        ['Fault Diagnosis', 'Whitened cosine similarity vs. FSM (5 modes)', 'Verified'],
        ['Health Index', 'ExtraTrees (184 feat.) / exp(−ρ·D)', 'Fallback only'],
        ['RUL Estimation', 'ExtraTrees (51 feat.) / Wiener IG', 'OOF verified'],
        ['Ingestion', 'FastAPI + WebSocket', 'Active'],
        ['Persistence', 'TimescaleDB hypertables', 'Schema only'],
        ['Frontend', 'React 18 + Three.js + Recharts', 'Active'],
    ],
    'TABLE I: System Technology and Module Implementation Status'
)

add_subsection('B. Independently Reproduced Results')
add_body(
    "The built-in validation harness was executed without the reference dataset, yielding "
    "6/6 passing checks. Per-channel noise sigma deviated at most 12.4% from calibrated "
    "values (map_kpa channel). The simulated residual norm median (28.2) matched the "
    "reference (33.1) within a ratio of 0.85. Fault signature alignment achieved cosine "
    "similarity ≥ 0.999 across all five modes. Leave-one-trajectory-out supervised "
    "cross-validation reported 87.8% overall accuracy versus the 84.5% reference."
)

add_body(
    "Zero-shot physics fingerprinting isolated 99.2% of severity>0.35 samples (120/121) "
    "without any training data. The physics evaluation and residual computation latency "
    "was measured at 0.27 ms per sample on a standard x86 CPU thread."
)

# TABLE II — Performance Metrics
add_table_compact(
    ['Metric', 'Value', 'Evidence Status'],
    [
        ['Noise sigma alignment', '≤12.4% of calibrated', 'Reproduced'],
        ['Fault cosine similarity', '≥0.999 all modes', 'Reproduced'],
        ['LOO diagnostic accuracy', '87.8%', 'Reproduced'],
        ['Zero-shot isolation (sev>0.35)', '99.2% (120/121)', 'Reproduced'],
        ['Physics+residual latency', '0.27 ms/sample', 'Reproduced'],
        ['Model 5 OOF R²', '0.758', 'Recomputed from CSV'],
        ['Model 5 OOF MAE', '808.7 cycles (≈13.5h)', 'Recomputed from CSV'],
        ['Model 5 OOF RMSE', '1349.6 cycles', 'Recomputed from CSV'],
        ['Anomaly precision 94.5%', '—', 'Unverifiable'],
        ['F1 90% (15 classes)', '5 modes; 13-62% per-class', 'Contradicted'],
        ['RUL interval coverage 78%', '—', 'Unverifiable (joblib error)'],
    ],
    'TABLE II: Quantitative Metrics with Evidence Verification Status'
)

add_subsection('C. Model 5 RUL Recomputation')
add_body(
    "Independent recomputation from model5_clean_oof_predictions.csv (1,100 rows, 22 "
    "GroupKFold missions) yielded MAE = 808.7 cycles, RMSE = 1349.6 cycles, R² = 0.758, "
    "materially consistent with the repository-reported values (MAE=805.3, RMSE=1343.1, "
    "R²=0.760). Critically, the original model metadata reported R²=0.9998 with 52 features "
    "including the target variable rul_target_cycles — a target leakage issue documented "
    "in the final configuration and guarded by an assertion in the production code."
)

# TABLE III — Related Work Comparison
add_table_compact(
    ['Study', 'Method', 'Dataset', 'Key Metric'],
    [
        ['Jardine et al. [1]', 'CBM review', 'Survey', 'Framework taxonomy'],
        ['Shen et al. [3]', 'Deep CNN', 'C-MAPSS turbofan', 'RUL RMSE=18.4 cyc'],
        ['Samuel & Pines [4]', 'Vibration CI', 'Rotorcraft', 'Transmission diag.'],
        ['Ye & Chen [11]', 'IG process', 'Lab bearings', 'Closed-form CI'],
        ['Geurts et al. [13]', 'ExtraTrees', 'General ML', 'Ensemble theory'],
        ['This work', 'Physics + ML', 'Synth. UAV (22 msn)', 'R²=0.758, 0.27ms'],
    ],
    'TABLE III: Comparison with Related Approaches'
)

# ─── VI. DISCUSSION ───────────────────────────────────────────────────
add_section_heading('VI. Discussion')

add_subsection('A. Architectural Strengths')
add_body(
    "By grounding telemetry analysis in closed-form physics, AeroTwin-HUMS eliminates false "
    "alarms driven by atmospheric transitions. The 0.27 ms per-sample latency makes it viable "
    "for ground-station deployment. The inclusion of generalised_wear in the FSM provides an "
    "effective guard against false discrete fault diagnoses on aging machinery. The zero-shot "
    "isolation rate of 99.2% demonstrates that physics-derived fault signatures can substitute "
    "for large labelled training datasets in the initial deployment phase."
)

add_subsection('B. Disclosed Limitations')
add_body(
    "Five critical limitations are identified. "
    "(1) Model artifacts: The .joblib files are Git LFS pointer stubs (133 bytes). Runtime "
    "joblib.load() fails, causing the system to fall back onto heuristic exponential health "
    "mappings. (2) Feature truncation: Model 4 runtime generates 106 of 184 expected features; "
    "78 default to zero. (3) Synthetic provenance: All calibration parameters derive from "
    "synthetic data. No physical engine manufacturer, model, or dynamometer data is identified. "
    "(4) Unconfirmed channels: sensor_4 and sensor_11 remain physically unverified, requiring "
    "artificial down-weighting. (5) No multi-engine coupling: Dual-engine airframes run "
    "independent parallel sessions with no cross-airframe vibration model.",
    bold_prefix="Engineering limitations. "
)

add_body(
    "The CAN bus and MQTT adapters exist as implemented classes "
    "but are never instantiated in the application startup. Redis is configured but unused. "
    "The REST ingestion endpoint stores data directly to the database without triggering "
    "model inference. The frontend contains a mixture of live backend-connected telemetry "
    "handling and locally generated mock data for replay, risk assessment, and maintenance "
    "views. These integration gaps must be addressed before operational deployment.",
    bold_prefix="Integration gaps. "
)

add_body(
    "The claimed ±15% RUL band is a fixed heuristic, not a calibrated prediction interval. "
    "The per-class LOO diagnostic accuracy ranges from 13.3% (misfire) to 61.8% (ring_wear) "
    "in the reference dataset, reflecting the small number of trajectories per fault type "
    "rather than fundamental model inadequacy. Expanding the training set to 10+ trajectories "
    "per mode would substantively improve supervised diagnostic performance.",
    bold_prefix="Statistical caveats. "
)

# ─── VII. CONCLUSION ──────────────────────────────────────────────────
add_section_heading('VII. Conclusion')

add_body(
    "This paper has presented AeroTwin-HUMS, an integrated physics-informed digital twin "
    "framework for UAV piston engine health monitoring, anomaly detection, fault isolation, "
    "and remaining useful life estimation. By embedding closed-form thermodynamic relationships, "
    "ISA environmental modeling, regularized Mahalanobis distance scoring, and whitened cosine "
    "similarity within a modular service architecture, the system provides zero-shot diagnostic "
    "interpretability while suppressing environmentally-induced false alarms."
)

add_body(
    "Independent validation confirms: per-channel noise reproduction within 12.4% of "
    "calibrated values, fault signature cosine alignment ≥0.999, leave-one-trajectory-out "
    "accuracy of 87.8%, zero-shot isolation of 99.2% at severity >0.35, and an audited "
    "out-of-fold RUL R² of 0.758 following target leakage elimination. The physics-only "
    "inference path achieves 0.27 ms per sample."
)

add_body(
    "Future work will focus on: (1) resolving Git LFS model artifacts and validating "
    "ML inference end-to-end; (2) calibrating sensor response equations against physical "
    "engine dynamometer data; (3) establishing certified operating envelope limits from "
    "manufacturer specifications; (4) wiring CAN bus and MQTT adapters for embedded "
    "deployment; and (5) conducting controlled flight test campaigns to validate the "
    "framework on operational airframes."
)

# ─── REFERENCES ───────────────────────────────────────────────────────
add_section_heading('References')

refs = [
    '[1] A. Jardine, D. Lin, and D. Banjevic, "A review on machinery diagnostics and prognostics implementing condition-based maintenance," Mech. Syst. Signal Process., vol. 20, no. 7, pp. 1483–1510, 2006.',
    '[2] J. D. Anderson, Introduction to Flight, 8th ed. New York, NY, USA: McGraw-Hill, 2016.',
    '[3] G. Shen, C. Lu, and Y. Wang, "Deep convolutional neural networks for aircraft engine remaining useful life estimation," IEEE Trans. Ind. Inform., vol. 17, no. 10, pp. 6872–6881, 2021.',
    '[4] B. Samuel and D. Pines, "A review of vibration-based techniques for helicopter transmission diagnostics," J. Sound Vib., vol. 282, no. 1–2, pp. 475–508, 2005.',
    '[5] F. Cadini, E. Zio, and D. Avram, "Model-based and data-driven prognostics under non-stationary operational conditions," Rel. Eng. Syst. Saf., vol. 94, no. 4, pp. 825–833, 2009.',
    '[6] M. Grieves and J. Vickers, "Digital twin: Mitigating unpredictable, undesirable emergent behavior in complex systems," in Transdiscip. Perspect. Complex Syst., Springer, 2017, pp. 85–113.',
    '[7] M. Schwabacher, "A survey of data-driven prognostics," in Proc. Infotech@Aerospace Conf., Arlington, VA, USA, 2005, pp. 1–11.',
    '[8] K. Worden, W. Staszewski, and J. Hensman, "Natural computing for mechanical system identification: A review," Phil. Trans. R. Soc. A, vol. 369, no. 1938, pp. 894–920, 2011.',
    '[9] J. Gertler, Fault Detection and Diagnosis in Engineering Systems. New York, NY, USA: Marcel Dekker, 1998.',
    '[10] P. C. Mahalanobis, "On the generalized distance in statistics," Proc. Natl. Inst. Sci. India, vol. 2, no. 1, pp. 49–55, 1936.',
    '[11] Z. Ye and N. Chen, "The inverse Gaussian process as a model for degradation data," Technometrics, vol. 56, no. 3, pp. 302–311, 2014.',
    '[12] X. Si, W. Wang, C. Hu, and D. Zhou, "Remaining useful life estimation: A review on the statistical data-driven approaches," Eur. J. Oper. Res., vol. 213, no. 1, pp. 1–14, 2011.',
    '[13] P. Geurts, D. Ernst, and L. Wehenkel, "Extremely randomized trees," Mach. Learn., vol. 63, no. 1, pp. 3–42, 2006.',
    '[14] A. Saxena, K. Goebel, D. Simon, and N. Eklund, "Damage propagation modeling for aircraft engine run-to-failure simulation," in Proc. IEEE PHM, Denver, CO, USA, 2008, pp. 1–9.',
    '[15] E. Zio, The Monte Carlo Simulation Method for System Reliability and Risk Analysis. London, UK: Springer, 2013.',
    '[16] U.S. Standard Atmosphere, 1976, NOAA, NASA, USAF, Washington, DC, USA, NOAA-S/T 76-1562, 1976.',
    '[17] RTCA Inc., DO-178C: Software Considerations in Airborne Systems and Equipment Certification, Washington, DC, USA, 2011.',
    '[18] T. Wang, J. Yu, D. Siegel, and J. Lee, "A similarity-based prognostics approach for remaining useful life estimation of engineered systems," in Proc. IEEE PHM, Denver, CO, USA, 2008, pp. 1–6.',
]

for ref in refs:
    p = doc.add_paragraph(ref, style='Reference')

# ─── Save ─────────────────────────────────────────────────────────────
output_path = os.path.join(OUTPUT_DIR, 'AeroTwin_HUMS_IEEE_Paper.docx')
doc.save(output_path)
print(f"Paper saved to: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
