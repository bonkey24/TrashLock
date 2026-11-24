"""
ui.py – Stitch theme styling and UI helper components for TrashLock.

Extracts and applies design tokens from the Stitch design templates:
- Background: #46344E
- Surface (cards, sidebar): #5A5560
- Surface Container (inputs, boxes): #46344E
- Primary (accent yellow): #FAED26 (on-primary: #46344E)
- Secondary: #9B786F (on-secondary: #1C1520)
- Text (on-background, on-surface): #F5F1E8
- Muted / Outline: #9D8D8F
- Success (green badge): #22C55E (on-success: #052E16)
- Error (red badge): #EF4444 (on-error: #1F0505)
- Typography: Space Grotesk (display/body) & JetBrains Mono (numbers/code)
"""

import html
import streamlit as st


def inject_css():
    """Inject Google Fonts and custom CSS matching the Stitch design system."""
    css = """
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=block" rel="stylesheet">

    <style>
    /* ==========================================================================
       Stitch Design System Tokens
       ========================================================================== */
    :root {
        --tl-bg: #46344E;
        --tl-surface: #5A5560;
        --tl-surface-container: #46344E;
        --tl-primary: #FAED26;
        --tl-primary-dark: #46344E;
        --tl-secondary: #9B786F;
        --tl-text: #F5F1E8;
        --tl-muted: #9D8D8F;
        --tl-outline: #9D8D8F;
        --tl-success: #22C55E;
        --tl-success-dark: #052E16;
        --tl-error: #EF4444;
        --tl-error-dark: #1F0505;
        --tl-radius-md: 12px;
        --tl-radius-sm: 8px;
    }

    /* Base Typography & Background */
    html, body, [class*="st-"], .stApp {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--tl-text) !important;
    }
    .stApp {
        background-color: var(--tl-bg) !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: var(--tl-text) !important;
        letter-spacing: -0.5px !important;
    }

    /* Monospace / Numerics */
    code, pre, .font-mono, [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Shared Left Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--tl-surface) !important;
        border-right: 1px solid var(--tl-outline) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--tl-primary) !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: var(--tl-text) !important;
    }

    /* Sidebar Navigation (Radio Pills) */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 6px;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background-color: transparent !important;
        padding: 8px 14px !important;
        border-radius: var(--tl-radius-sm) !important;
        transition: background-color 150ms ease-out, color 150ms ease-out !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: var(--tl-secondary) !important;
        color: #1C1520 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover * {
        color: #1C1520 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] {
        background-color: var(--tl-primary) !important;
        border: 1px solid rgba(250, 237, 38, 0.4) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"] * {
        color: var(--tl-primary-dark) !important;
        font-weight: 700 !important;
    }

    /* Card Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--tl-surface) !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-md) !important;
        padding: 22px 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25), 0 2px 4px -2px rgba(0, 0, 0, 0.2) !important;
    }

    /* Primary and Secondary Buttons */
    div.stButton > button,
    div.stButton > button[kind="primary"],
    div[data-testid="stDownloadButton"] > button {
        background-color: var(--tl-primary) !important;
        color: var(--tl-primary-dark) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: var(--tl-radius-sm) !important;
        padding: 10px 22px !important;
        transition: all 150ms ease-out !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }
    div.stButton > button:hover,
    div.stButton > button[kind="primary"]:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: var(--tl-secondary) !important;
        color: #1C1520 !important;
        border: none !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: var(--tl-secondary) !important;
        color: #1C1520 !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-sm) !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: var(--tl-primary) !important;
        color: var(--tl-primary-dark) !important;
    }

    /* Form Input Fields (Name, PIN, Dropdowns) */
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        background-color: var(--tl-surface-container) !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-sm) !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] span {
        color: var(--tl-text) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        border-color: var(--tl-primary) !important;
        box-shadow: 0 0 0 1px var(--tl-primary) !important;
    }

    /* Slider Styling */
    div[data-testid="stSlider"] [role="slider"] {
        background-color: var(--tl-primary) !important;
        border: 2px solid var(--tl-surface-container) !important;
    }
    /* Hide duplicate floating thumb value tooltip so threshold shows only once */
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        display: none !important;
    }

    /* Toggle / Checkbox Styling */
    div[data-testid="stCheckbox"] label span[data-checked="true"] {
        background-color: var(--tl-primary) !important;
    }

    /* Progress Bar */
    div[data-testid="stProgress"] > div > div > div {
        background-color: var(--tl-primary) !important;
    }
    div[data-testid="stProgress"] > div > div {
        background-color: var(--tl-surface-container) !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: 9999px !important;
    }

    /* Camera Input Widget */
    [data-testid="stCameraInput"] {
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-md) !important;
        background-color: var(--tl-surface-container) !important;
        padding: 12px !important;
    }

    /* Table Styling */
    div[data-testid="stTable"] table {
        background-color: var(--tl-surface) !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-md) !important;
        overflow: hidden !important;
        width: 100% !important;
    }
    div[data-testid="stTable"] th {
        background-color: var(--tl-surface-container) !important;
        color: var(--tl-primary) !important;
        border-bottom: 1px solid var(--tl-outline) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stTable"] td {
        border-bottom: 1px solid rgba(157, 141, 143, 0.25) !important;
        color: var(--tl-text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        padding: 10px 14px !important;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: var(--tl-surface-container) !important;
        border: 1px solid var(--tl-outline) !important;
        border-radius: var(--tl-radius-sm) !important;
        color: var(--tl-text) !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def page_header(title: str, description: str = ""):
    """Render the standard Stitch page header with title, tagline, and description."""
    desc_html = (
        f'<p style="font-size: 14px; color: #9D8D8F; line-height: 1.5; margin-bottom: 20px; font-family: \'Space Grotesk\', sans-serif;">{description}</p>'
        if description
        else '<div style="margin-bottom: 16px;"></div>'
    )
    st.markdown(
        f"""
        <header style="margin-bottom: 16px;">
            <h1 style="font-size: 32px; font-weight: 700; color: #F5F1E8; margin: 0; font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.5px;">{title}</h1>
            <p style="font-size: 14px; color: #F5F1E8; opacity: 0.85; margin: 2px 0 6px 0; font-family: 'Space Grotesk', sans-serif;">Your body as a password</p>
            {desc_html}
        </header>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, subtitle: str = ""):
    """Render a card header matching Stitch card typography."""
    sub_html = (
        f'<p style="font-size: 13px; color: #9D8D8F; margin: 4px 0 16px 0; font-family: \'Space Grotesk\', sans-serif;">{subtitle}</p>'
        if subtitle
        else '<div style="margin-bottom: 16px;"></div>'
    )
    st.markdown(
        f"""
        <div style="margin-bottom: 8px;">
            <h2 style="font-size: 20px; font-weight: 700; color: #F5F1E8; margin: 0; font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.25px;">{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def success_badge(text: str = "Access granted", subtext: str = "Distance within match threshold"):
    """Render a large green access granted badge matching login.html."""
    st.markdown(
        f"""
        <div style="background-color: #22C55E; color: #052E16; border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 12px; padding: 18px 20px; display: flex; align-items: center; gap: 16px; margin: 16px 0;">
            <div style="width: 44px; height: 44px; border-radius: 50%; background-color: #052E16; color: #22C55E; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; line-height: 1.2; color: #052E16;">{text}</span>
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 13px; color: #052E16; opacity: 0.85; margin-top: 2px;">{subtext}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def error_badge(text: str = "Access denied", subtext: str = "Distance exceeds match threshold"):
    """Render a large red access denied badge matching login.html."""
    st.markdown(
        f"""
        <div style="background-color: #EF4444; color: #1F0505; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 18px 20px; display: flex; align-items: center; gap: 16px; margin: 16px 0;">
            <div style="width: 44px; height: 44px; border-radius: 50%; background-color: #1F0505; color: #EF4444; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; line-height: 1.2; color: #1F0505;">{text}</span>
                <span style="font-family: 'Space Grotesk', sans-serif; font-size: 13px; color: #1F0505; opacity: 0.85; margin-top: 2px;">{subtext}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str | int, subtitle: str = ""):
    """Render a dataset summary metric card matching analysis.html."""
    sub_html = (
        f'<span style="font-size: 12px; color: #9D8D8F; font-family: \'Space Grotesk\', sans-serif;">{subtitle}</span>'
        if subtitle
        else ""
    )
    st.markdown(
        f"""
        <div style="background-color: #5A5560; border: 1px solid #9D8D8F; border-radius: 12px; padding: 18px 22px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.25); display: flex; flex-direction: column; justify-content: space-between; min-height: 115px; margin-bottom: 12px;">
            <span style="font-size: 13px; font-weight: 600; color: #F5F1E8; font-family: 'Space Grotesk', sans-serif;">{label}</span>
            <p style="font-family: 'JetBrains Mono', monospace; font-size: 36px; font-weight: 700; color: #FAED26; margin: 4px 0; line-height: 1.1;">{value}</p>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_metrics_panel(closest_match: str, distance: float, similarity: float, decision_str: str = ""):
    """Render the result metrics list and decision rule box matching login.html."""
    st.markdown(
        f"""
        <div style="border-top: 1px solid rgba(157, 141, 143, 0.4); border-bottom: 1px solid rgba(157, 141, 143, 0.4); margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(157, 141, 143, 0.2);">
                <span style="color: #9D8D8F; font-size: 14px; font-family: 'Space Grotesk', sans-serif;">Closest match</span>
                <span style="color: #F5F1E8; font-size: 16px; font-weight: 600; font-family: 'Space Grotesk', sans-serif;">{closest_match}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(157, 141, 143, 0.2);">
                <span style="color: #9D8D8F; font-size: 14px; font-family: 'Space Grotesk', sans-serif;">Cosine distance</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #FAED26; font-size: 20px; font-weight: 600;">{distance:.4f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0;">
                <span style="color: #9D8D8F; font-size: 14px; font-family: 'Space Grotesk', sans-serif;">Similarity</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #FAED26; font-size: 20px; font-weight: 600;">{similarity:.1%}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if decision_str:
        st.markdown(
            f"""
            <div style="background-color: #46344E; border: 1px solid rgba(157, 141, 143, 0.5); border-radius: 8px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <span style="color: #9D8D8F; font-size: 13px; font-family: 'Space Grotesk', sans-serif;">Decision rule</span>
                <span style="font-family: 'JetBrains Mono', monospace; color: #FAED26; font-size: 13px; font-weight: 600;">{decision_str}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def privacy_note():
    """Render the standard Stitch privacy container."""
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; background-color: #46344E; border: 1px solid rgba(157, 141, 143, 0.5); border-radius: 8px; padding: 10px 14px; margin-top: 12px;">
            <span style="color: #FAED26; font-size: 16px;">🔒</span>
            <span style="color: #F5F1E8; opacity: 0.9; font-size: 13px; font-family: 'Space Grotesk', sans-serif;">
                Only numeric templates are stored, never photos.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_test_log_table(logs: list[dict]):
    """Render the verification test log table with Pass and Fail badges matching test_log.html."""
    if not logs:
        st.info("ℹ️ No test log entries recorded yet. Use the **Add row** form above to record experimental scenarios.")
        return

    rows = []
    for log in logs:
        is_pass = str(log.get("status", "")).strip().lower() == "pass"
        badge_html = (
            '<span style="background-color: #22C55E; color: #052E16; border: 1px solid rgba(34, 197, 94, 0.4); font-family: \'Space Grotesk\', sans-serif; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;">✓ Pass</span>'
            if is_pass
            else '<span style="background-color: #EF4444; color: #1F0505; border: 1px solid rgba(239, 68, 68, 0.4); font-family: \'Space Grotesk\', sans-serif; font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;">✕ Fail</span>'
        )
        tc_esc = html.escape(str(log.get("test_case", "")))
        exp_esc = html.escape(str(log.get("expected", "")))
        act_esc = html.escape(str(log.get("actual", "")))

        row_html = (
            '<tr style="border-bottom: 1px solid rgba(157, 141, 143, 0.25);">'
            f'<td style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; color: #F5F1E8; font-size: 14px;">{tc_esc}</td>'
            f'<td style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; color: #9D8D8F; font-size: 14px;">{exp_esc}</td>'
            f'<td style="padding: 12px 16px; font-family: \'JetBrains Mono\', monospace; color: #F5F1E8; font-size: 13px;">{act_esc}</td>'
            f'<td style="padding: 12px 16px; text-align: right;">{badge_html}</td>'
            '</tr>'
        )
        rows.append(row_html)

    tbody_content = "".join(rows)

    table_html = (
        '<div style="background-color: #5A5560; border: 1px solid #9D8D8F; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.25); margin: 12px 0;">'
        '<table style="width: 100%; border-collapse: collapse; text-align: left;">'
        '<thead>'
        '<tr style="background-color: #46344E; border-bottom: 1px solid #9D8D8F;">'
        '<th style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; font-size: 13px; font-weight: 600; color: #FAED26;">Test case</th>'
        '<th style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; font-size: 13px; font-weight: 600; color: #FAED26;">Expected</th>'
        '<th style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; font-size: 13px; font-weight: 600; color: #FAED26;">Actual</th>'
        '<th style="padding: 12px 16px; font-family: \'Space Grotesk\', sans-serif; font-size: 13px; font-weight: 600; color: #FAED26; text-align: right;">Pass/Fail</th>'
        '</tr>'
        '</thead>'
        f'<tbody>{tbody_content}</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def style_figure(fig, ax):
    """
    Style Matplotlib figures to seamlessly integrate with Stitch card styling:
    - Card background #5A5560
    - Text and title in off-white #F5F1E8
    - Ticks and gridlines in #9D8D8F (alpha 0.35)
    - Border lines in #9D8D8F
    """
    CARD_BG = "#5A5560"
    TEXT_COLOR = "#F5F1E8"
    MUTED_COLOR = "#9D8D8F"

    fig.patch.set_facecolor(CARD_BG)
    ax.set_facecolor(CARD_BG)

    # Clean borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUTED_COLOR)
    ax.spines["bottom"].set_color(MUTED_COLOR)
    ax.spines["left"].set_linewidth(1.0)
    ax.spines["bottom"].set_linewidth(1.0)

    # Ticks & labels
    ax.tick_params(colors=TEXT_COLOR, which="both", labelsize=10)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.xaxis.label.set_size(12)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_size(12)
    ax.title.set_color(TEXT_COLOR)
    ax.title.set_size(13)

    # Gridlines
    ax.grid(True, linestyle="-", color=MUTED_COLOR, alpha=0.35, linewidth=1.0)
