# Shared styles and CSS with Dark Mode support (Priority 9)
# Theming is driven by CSS custom properties so every component can adapt to
# the active theme without hard-coded colour edits. Dark mode also remaps the
# legacy hard-coded hex colours still present in inline HTML strings across the
# pages, which previously caused invisible (light-on-light) text.
import streamlit as st


def load_app_css():
    """Load all application-wide CSS styles dynamically depending on theme."""
    theme = st.session_state.get("theme", "Ethereal Silk (Light)")
    if theme not in ["Ethereal Silk (Light)", "Midnight Cosmic (Dark)"]:
        theme = "Ethereal Silk (Light)"
        st.session_state["theme"] = "Ethereal Silk (Light)"

    # ---- Theme design tokens (CSS variables) ----
    # Ethereal Silk (Light) is the default; Midnight Cosmic (Dark) overrides it.
    tokens = """
        :root {
            --bg: #F8FAFC;
            --bg-gradient: radial-gradient(circle at 5% 5%, rgba(20, 184, 166, 0.08) 0%, rgba(255, 255, 255, 0) 50%),
                           radial-gradient(circle at 95% 95%, rgba(99, 102, 241, 0.06) 0%, rgba(255, 255, 255, 0) 50%),
                           linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            --card: rgba(255, 255, 255, 0.85);
            --border: rgba(226, 232, 240, 0.8);
            --text: #0F172A;
            --text-soft: #64748B;
            --text-body: #334155;
            --primary: #0D9488;
            --primary-light: #14B8A6;
            --primary-dark: #115E59;
            --info: #3B82F6;
            --info-bg: rgba(59, 130, 246, 0.08);
            --success: #10B981;
            --success-bg: rgba(16, 185, 129, 0.08);
            --warning: #F59E0B;
            --warning-bg: rgba(245, 158, 11, 0.08);
            --danger: #EF4444;
            --danger-bg: rgba(239, 68, 68, 0.08);
            --purple: #8B5CF6;
            --purple-bg: rgba(139, 92, 246, 0.08);
            --accent: #F59E0B;
            --accent-bg: rgba(245, 158, 11, 0.08);
            --nav-hover: rgba(13, 148, 136, 0.08);
            --shadow: rgba(15, 23, 42, 0.04);
            --shadow-strong: rgba(15, 23, 42, 0.08);
            --sidebar-bg: linear-gradient(180deg, #F1F5F9 0%, #E2E8F0 100%);
            --sidebar-text: #334155;
            --sidebar-text-soft: #64748B;
        }
    """

    if theme == "Midnight Cosmic (Dark)":
        tokens = """
            :root {
                --bg: #0B0F19;
                --bg-gradient: radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, rgba(15, 23, 42, 0) 45%),
                               radial-gradient(circle at 90% 80%, rgba(20, 184, 166, 0.1) 0%, rgba(15, 23, 42, 0) 50%),
                               linear-gradient(135deg, #0b0f19 0%, #111827 100%);
                --card: rgba(17, 24, 39, 0.75);
                --border: rgba(139, 92, 246, 0.2);
                --text: #F8FAFC;
                --text-soft: #94A3B8;
                --text-body: #CBD5E1;
                --primary: #8B5CF6;
                --primary-light: #A78BFA;
                --primary-dark: #4C1D95;
                --info: #60A5FA;
                --info-bg: rgba(96, 165, 250, 0.12);
                --success: #34D399;
                --success-bg: rgba(52, 211, 153, 0.12);
                --warning: #F59E0B;
                --warning-bg: rgba(245, 158, 11, 0.12);
                --danger: #F87171;
                --danger-bg: rgba(248, 113, 113, 0.12);
                --purple: #C084FC;
                --purple-bg: rgba(192, 132, 252, 0.12);
                --accent: #F59E0B;
                --accent-bg: rgba(245, 158, 11, 0.12);
                --nav-hover: rgba(139, 92, 246, 0.15);
                --shadow: rgba(0, 0, 0, 0.3);
                --shadow-strong: rgba(0, 0, 0, 0.5);
                --sidebar-bg: linear-gradient(180deg, #111827 0%, #0B0F19 100%);
                --sidebar-text: #CBD5E1;
                --sidebar-text-soft: #94A3B8;
            }
        """

    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        {tokens}

        /* ---- Google Fonts ---- */
        html, body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* ---- Premium Components ---- */
        .premium-info-banner {{
            background: linear-gradient(135deg, var(--info-bg), var(--bg)) !important;
            border: 1px solid var(--border) !important;
            border-left: 5px solid var(--info) !important;
            border-radius: 18px !important;
            padding: 22px 24px !important;
            margin-bottom: 20px !important;
            color: var(--text) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
        }}
        .premium-info-banner h4 {{
            margin: 0 0 6px !important;
            color: var(--text) !important;
            font-family: 'Lora', serif !important;
            font-size: 18px !important;
            font-weight: 700 !important;
        }}
        .premium-info-banner p {{
            margin: 0 !important;
            color: var(--text-body) !important;
            font-size: 14px !important;
        }}
        
        .premium-alert-banner {{
            background: var(--danger-bg) !important;
            border: 1px solid var(--border) !important;
            border-left: 5px solid var(--danger) !important;
            border-radius: 18px !important;
            padding: 18px 22px !important;
            margin-bottom: 12px !important;
            color: var(--text) !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
        }}
        .premium-alert-banner h3 {{
            margin: 0 !important;
            color: var(--danger) !important;
            font-family: 'Lora', serif !important;
            font-size: 18px !important;
            font-weight: 700 !important;
        }}
        .premium-alert-banner p {{
            margin: 6px 0 0 !important;
            color: var(--text-body) !important;
            font-size: 14px !important;
        }}

        /* Welcome Banner Premium Theme Match Overrides */
        .welcome-banner {{
            background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
            box-shadow: 0 16px 40px var(--shadow-strong) !important;
        }}
        .welcome-banner h2, .welcome-banner h2 * {{
            color: #FFFFFF !important;
        }}
        .welcome-banner p, .welcome-banner p * {{
            color: rgba(255, 255, 255, 0.9) !important;
        }}
        .welcome-role-badge {{
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
        }}

        .clinical-feature-card {{
            background: var(--card) !important;
            padding: 28px 24px !important;
            border-radius: 20px !important;
            border: 1px solid var(--border) !important;
            height: 240px !important;
            box-shadow: 0 4px 16px var(--shadow) !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            transition: all .3s cubic-bezier(.4,0,.2,1) !important;
        }}
        .clinical-feature-card:hover {{
            transform: translateY(-5px) !important;
            box-shadow: 0 12px 28px var(--shadow-strong) !important;
            border-color: var(--primary) !important;
        }}
        .clinical-feature-card .feature-icon {{
            font-size: 38px !important;
            margin-bottom: 12px !important;
        }}
        .clinical-feature-card h4 {{
            margin: 0 0 8px !important;
            color: var(--text) !important;
            font-family: 'Lora', serif !important;
            font-size: 19px !important;
            font-weight: 700 !important;
        }}
        .clinical-feature-card p {{
            color: var(--text-body) !important;
            font-size: 13.5px !important;
            margin: 0 !important;
            line-height: 1.5 !important;
        }}

        .testimonial-card {{
            background: var(--card) !important;
            padding: 24px !important;
            border-radius: 18px !important;
            border: 1px solid var(--border) !important;
            box-shadow: 0 4px 12px var(--shadow) !important;
            transition: all 0.3s ease !important;
            height: 100%;
        }}
        .testimonial-card:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px var(--shadow-strong) !important;
        }}
        .testimonial-card p.quote {{
            font-style: italic !important;
            color: var(--text) !important;
            margin-bottom: 12px !important;
            font-size: 15px !important;
            line-height: 1.6 !important;
        }}
        .testimonial-card p.author {{
            font-weight: 700 !important;
            color: var(--primary) !important;
            font-size: 14px !important;
            margin: 0 !important;
        }}

        /* ---- Dynamic Theme Overrides & animations ---- */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-12px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes scaleUp {{
            from {{ opacity: 0; transform: scale(0.96); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        .stApp {{
            background: var(--bg-gradient) !important;
            background-attachment: fixed !important;
            color: var(--text) !important;
            animation: fadeIn 0.4s ease-out;
        }}

        .stat-card, .prediction-card, .metric-card, .chat-bubble, [data-testid="stMetricValue"] {{
            animation: slideIn 0.35s ease-out;
            transition: all 0.2s ease-in-out;
        }}

        .stat-card:hover, .prediction-card:hover, .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(15,110,132,.15) !important;
        }}

        div[data-testid="stVerticalBlock"] > div {{
            color: var(--text);
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--text) !important;
            font-family: 'Lora', 'Playfair Display', serif !important;
        }}

        /* Make standard markdown text match theme but exclude widgets */
        .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown label {{
            color: var(--text);
        }}

        /* Streamlit widget labels visibility fix */
        label, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
        .stWidgetLabel, .stWidgetLabel p, div[data-testid="stCaptionContainer"] {{
            color: var(--text) !important;
        }}

        /* Tables theme matching */
        table, th, td, [data-testid="stTable"] {{
            color: var(--text) !important;
            background-color: var(--card) !important;
        }}
        th {{
            font-weight: 700 !important;
            border-bottom: 2px solid var(--border) !important;
        }}
        td {{
            border-bottom: 1px solid var(--border) !important;
        }}

        /* Metric and Stat Cards */
        .stat-card, .prediction-card, .metric-card,
        div[style*="background:white"], div[style*="background: white"],
        div[style*="background:#FFFFFF"], div[style*="background:#fff"] {{
            background-color: var(--card) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
        }}

        .stat-card p, .prediction-text, .metric-card p,
        p[style*="color:gray"], p[style*="color:#7B8E96"] {{
            color: var(--text-soft) !important;
        }}

        .stat-card h1, .prediction-title, .metric-card h3,
        h2[style*="color:#0F3D4F"], h1[style*="color:#0F3D4F"], h3[style*="color:#0F3D4F"], h4[style*="color:#0F3D4F"] {{
            color: var(--text) !important;
        }}

        /* ---- Polished Buttons & Form Submit Buttons ---- */
        .stButton>button, div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.6rem 1.4rem !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            letter-spacing: 0.2px !important;
            transition: all .25s cubic-bezier(.4,0,.2,1) !important;
            box-shadow: 0 2px 8px var(--shadow) !important;
        }}
        .stButton>button:hover, div[data-testid="stFormSubmitButton"] button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px var(--shadow-strong) !important;
            filter: brightness(1.06) !important;
        }}
        .stButton>button:active, div[data-testid="stFormSubmitButton"] button:active {{
            transform: translateY(0) scale(.97) !important;
        }}

        /* ---- Top navbar ---- */
        .top-navbar {{
            background: var(--card);
            border-bottom: 1px solid var(--border);
            padding: 14px 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 16px;
            margin-bottom: 8px;
            box-shadow: 0 2px 10px var(--shadow);
        }}
        .top-navbar .nav-brand {{
            font-size: 22px;
            font-weight: 800;
            color: var(--text);
        }}
        .top-navbar .nav-links {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        .top-navbar .nav-link {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-soft);
            cursor: pointer;
            padding: 8px 14px;
            border-radius: 10px;
            transition: all .2s;
            text-decoration: none;
        }}
        .top-navbar .nav-link:hover {{
            background: var(--nav-hover);
            color: var(--primary);
        }}

        /* ---- Horizontal Nav Pill Bar (Adjacent Sibling Override) ---- */
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div.stHorizontalBlock,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            gap: 8px !important;
            padding: 8px 4px 12px !important;
            scrollbar-width: thin !important;
            scrollbar-color: var(--border) transparent !important;
            margin-bottom: 8px !important;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div.stHorizontalBlock::-webkit-scrollbar,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {{
            height: 4px;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div.stHorizontalBlock::-webkit-scrollbar-thumb,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div[data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {{
            background: var(--border);
            border-radius: 4px;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div.stHorizontalBlock > div,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div.stHorizontalBlock > div > div,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div[data-testid="stHorizontalBlock"] div[data-testid="column"],
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] div[data-testid="stHorizontalBlock"] div[data-testid="column"] > div {{
            width: max-content !important;
            flex: 0 0 auto !important;
            min-width: max-content !important;
            padding: 0 !important;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button {{
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            padding: 10px 20px !important;
            border-radius: 30px !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            white-space: nowrap !important;
            transition: all .25s cubic-bezier(.4,0,.2,1) !important;
            border: 1.5px solid var(--border) !important;
            background: var(--card) !important;
            color: var(--text-soft) !important;
            height: auto !important;
            box-shadow: none !important;
            transform: none !important;
            width: max-content !important;
            min-width: max-content !important;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button:hover {{
            background: var(--nav-hover) !important;
            color: var(--primary) !important;
            border-color: var(--primary) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px var(--shadow) !important;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button[data-testid="baseButton-primary"],
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button[kind="primary"] {{
            background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
            color: white !important;
            border-color: transparent !important;
            box-shadow: 0 4px 14px var(--shadow-strong) !important;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button[data-testid="baseButton-primary"]::after,
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button[kind="primary"]::after {{
            content: "";
            position: absolute;
            left: 50%;
            bottom: 4px;
            height: 3px;
            border-radius: 3px;
            background: white;
            transform: translateX(-50%);
            animation: navGlow 1.6s ease-in-out infinite;
        }}
        div[data-testid="element-container"]:has(#nav-container-marker) + div[data-testid="element-container"] button p {{
            color: inherit !important;
            font-weight: inherit !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }}

        /* ---- Section headers ---- */
        .section-header {{
            font-size: 20px;
            font-weight: 700;
            color: var(--text);
            margin: 24px 0 14px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border);
        }}

        /* ---- Patient info card ---- */
        .patient-info-card {{
            background: var(--nav-hover);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 20px;
        }}
        .patient-info-card h4 {{
            margin: 0 0 8px;
            color: var(--text);
            font-size: 18px;
        }}
        .patient-info-card p {{
            margin: 4px 0;
            color: var(--text-soft);
            font-size: 15px;
        }}

        /* ---- Styled Sidebar ---- */
        section[data-testid="stSidebar"] {{
            background: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border) !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: var(--sidebar-text) !important;
        }}
        section[data-testid="stSidebar"] .stButton>button {{
            background: linear-gradient(135deg, #dc2626, #ef4444) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(220,38,38,.3) !important;
        }}
        section[data-testid="stSidebar"] .stButton>button:hover {{
            background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
            box-shadow: 0 6px 18px rgba(220,38,38,.4) !important;
        }}

        /* Floating Sidebar Toggle and Collapse Buttons */
        button[data-testid="collapsedSidebarTab"],
        button[aria-label="Expand sidebar"],
        button[aria-label="Collapse sidebar"],
        [data-testid="collapsedSidebarTab"] button {{
            background-color: var(--primary-dark) !important;
            color: white !important;
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            box-shadow: 0 4px 12px var(--shadow-strong) !important;
            border: 1px solid var(--border) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease-in-out !important;
        }}
        button[data-testid="collapsedSidebarTab"]:hover,
        button[aria-label="Expand sidebar"]:hover,
        button[aria-label="Collapse sidebar"]:hover,
        [data-testid="collapsedSidebarTab"] button:hover {{
            background-color: var(--primary) !important;
            transform: scale(1.05) !important;
        }}
        button[data-testid="collapsedSidebarTab"] svg,
        button[aria-label="Expand sidebar"] svg,
        button[aria-label="Collapse sidebar"] svg {{
            color: white !important;
            fill: white !important;
        }}

        /* Sidebar profile card */
        .sidebar-profile {{
            text-align: center;
            padding: 24px 16px;
            margin-bottom: 16px;
        }}
        .sidebar-avatar {{
            width: 72px;
            height: 72px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
            color: white !important;
            font-size: 28px;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 14px;
            box-shadow: 0 4px 16px var(--shadow-strong) !important;
            border: 3px solid rgba(255,255,255,.2) !important;
        }}
        .sidebar-name {{
            font-size: 18px;
            font-weight: 700;
            color: var(--sidebar-text) !important;
            margin: 0 0 4px;
        }}
        .sidebar-email {{
            font-size: 12px;
            color: var(--sidebar-text-soft) !important;
            margin: 0 0 12px;
        }}
        .sidebar-role-badge {{
            display: inline-block;
            padding: 4px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: var(--nav-hover) !important;
            color: var(--primary) !important;
            border: 1px solid var(--border) !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* ---- Form Input Styling ---- */
        .stSelectbox > div > div,
        .stDateInput > div > div,
        .stTimeInput > div > div,
        .stNumberInput > div > div,
        .stTextInput > div > div,
        .stTextArea > div > div,
        div[data-baseweb="select"] > div,
        input, select, textarea {{
            background-color: var(--card) !important;
            color: var(--text) !important;
            border-radius: 12px !important;
            border-color: var(--border) !important;
            transition: all .2s ease;
        }}
        .stSelectbox *, .stDateInput *, .stTimeInput *, .stNumberInput *, .stTextInput *, .stTextArea *,
        div[data-baseweb="select"] *, [role="option"] *, [data-baseweb="popover"] * {{
            color: var(--text) !important;
        }}

        /* Force correct readable text colors inside Streamlit native alerts */
        div[data-testid="stAlert"] p, div[data-testid="stAlert"] li, div[data-testid="stAlert"] span, div[data-testid="stAlert"] div {{
            color: var(--text) !important;
        }}
        .stSelectbox > div > div:focus-within,
        .stDateInput > div > div:focus-within,
        .stNumberInput > div > div:focus-within,
        .stTextInput > div > div:focus-within,
        .stTextArea > div > div:focus-within {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px color-mix(in srgb, var(--primary) 15%, transparent) !important;
        }}
        div[data-baseweb="popover"] *, [role="listbox"] *, [role="option"] {{
            background-color: var(--card) !important;
            color: var(--text) !important;
        }}

        /* ---- Chatbot Bubble Styles ---- */
        .chat-bubble {{
            padding: 12px 16px;
            border-radius: 16px;
            margin-bottom: 12px;
            max-width: 80%;
            font-size: 15px;
            line-height: 1.5;
        }}
        .chat-user {{
            background-color: var(--primary);
            color: white !important;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }}
        .chat-user p, .chat-user span {{
            color: white !important;
        }}
        .chat-ai {{
            background-color: var(--card);
            border: 1px solid var(--border);
            color: var(--text);
            margin-right: auto;
            border-bottom-left-radius: 4px;
        }}
        .chat-ai p, .chat-ai span {{
            color: var(--text) !important;
        }}

        /* ---- Smooth, modern scrollbars ---- */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: color-mix(in srgb, var(--primary) 35%, transparent);
            border-radius: 8px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--primary); }}

        /* ---- Animated, modern tabs ---- */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: var(--card) !important;
            border-radius: 14px 14px 0 0 !important;
            border-bottom: 2px solid var(--border) !important;
            gap: 4px;
            padding: 4px 4px 0 !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            transition: all .2s ease;
            border-radius: 10px 10px 0 0;
            background-color: transparent !important;
        }}
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div {{
            color: var(--text-soft) !important;
            transition: all .2s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover p,
        .stTabs [data-baseweb="tab"]:hover span,
        .stTabs [data-baseweb="tab"]:hover div {{
            color: var(--text) !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] p,
        .stTabs [data-baseweb="tab"][aria-selected="true"] span,
        .stTabs [data-baseweb="tab"][aria-selected="true"] div {{
            color: var(--primary) !important;
            font-weight: 700 !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: var(--primary) !important;
        }}
        .stTabs [data-baseweb="tab-border"] {{
            background-color: var(--border) !important;
        }}
        .stTabs [data-baseweb="tab-panel"] {{
            background-color: transparent !important;
            color: var(--text) !important;
        }}

        /* Hide default Streamlit sidebar header */
        [data-testid="stSidebarNav"] {{ display: none; }}

        /* Hide Streamlit branding elements */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header[data-testid="stHeader"] {{ background: transparent; }}

        /* =========================================================
           ANIMATION KEYFRAMES + PAGE TRANSITIONS
           ========================================================= */
        @keyframes pageFadeIn {{
            from {{ opacity: 0; transform: translateY(14px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes expandGauge {{
            from {{ opacity: 0; transform: scale(.85); }}
            to   {{ opacity: 1; transform: scale(1); }}
        }}
        @keyframes navGlow {{
            0%, 100% {{ opacity: .4; width: 16px; }}
            50%      {{ opacity: 1; width: 28px; }}
        }}
        @keyframes popIn {{
            from {{ opacity: 0; transform: scale(.96); }}
            to   {{ opacity: 1; transform: scale(1); }}
        }}

        /* app.py adds .page-enter only when the active page changes */
        .page-enter {{ animation: pageFadeIn .45s cubic-bezier(.22,1,.36,1); }}
        .page-enter * {{ animation: slideUp .5s cubic-bezier(.22,1,.36,1) both; }}
        .page-enter .stPlotlyChart,
        .page-enter iframe {{ animation: none !important; }}

        /* Staggered entrance for cards sitting in columns */
        .stColumns .stat-card,
        .stColumns .prediction-card {{ animation: popIn .45s cubic-bezier(.22,1,.36,1) both; }}
    </style>
    """, unsafe_allow_html=True)

    # ---- Dark mode: remap legacy hard-coded colours still present in inline
    #      HTML strings (fixes light-on-light invisible text) ----
    if theme == "Midnight Cosmic (Dark)":
        dark_remap = """
        <style>
            [style*="color:#0F3D4F"], [style*="color: #0F3D4F"] { color: var(--text) !important; }
            [style*="color:#4D6A75"], [style*="color: #4D6A75"] { color: var(--text-body) !important; }
            [style*="color:#7B8E96"], [style*="color: #7B8E96"] { color: var(--text-soft) !important; }
            [style*="color:#374151"], [style*="color:#6B7280"] { color: var(--text-soft) !important; }
            [style*="color:#1E40AF"], [style*="color:#1E3A8A"], [style*="color:#0F766E"], [style*="color:#0369A1"],
            [style*="color:#1D4ED8"], [style*="color:#3B82F6"], [style*="color:#0284C7"], [style*="color:#38BDF8"] { color: var(--info) !important; }
            [style*="color:#166534"], [style*="color:#047857"], [style*="color:#065F46"], [style*="color:#10B981"],
            [style*="color:#059669"], [style*="color:#6EE7B7"] { color: var(--success) !important; }
            [style*="color:#92400E"], [style*="color:#78350F"], [style*="color:#F59E0B"], [style*="color:#D97706"] { color: var(--warning) !important; }
            [style*="color:#991B1B"], [style*="color:#DC2626"], [style*="color:#dc2626"], [style*="color:#D32F2F"],
            [style*="color:#b91c1c"], [style*="color:#F43F5E"], [style*="color:#ef4444"], [style*="color:#BE123C"] { color: var(--danger) !important; }
            [style*="color:#6D28D9"], [style*="color:#8B5CF6"] { color: var(--purple) !important; }

            [style*="background:#F4FBFD"], [style*="background: #F4FBFD"],
            [style*="background:#EAF6FB"], [style*="background:#EAF2F5"], [style*="background:#D5EAF1"],
            [style*="background:#F9FBFB"], [style*="background:#f9f9f9"], [style*="background:#F3F4F6"],
            [style*="background:#eee"], [style*="background: #eee"] { background-color: var(--card) !important; }

            [style*="background:#EFF6FF"], [style*="background:#F0F9FF"], [style*="background:#E0F2FE"],
            [style*="background:#DBEAFE"], [style*="background:#7DD3FC"] { background-color: var(--info-bg) !important; }

            [style*="background:#F0FDF4"], [style*="background:#ECFDF5"], [style*="background:#BBF7D0"] { background-color: var(--success-bg) !important; }
            [style*="background:#FEF2F2"], [style*="background:#FFF1F2"] { background-color: var(--danger-bg) !important; }
            [style*="background:#FFFBEB"], [style*="background:#FEF3C7"], [style*="background:#FFF7ED"] { background-color: var(--warning-bg) !important; }
            [style*="background:#F5F3FF"] { background-color: var(--purple-bg) !important; }

            [style*="linear-gradient(135deg,#F0F9FF"], [style*="linear-gradient(135deg, #F0F9FF"] {
                background: linear-gradient(135deg, var(--info-bg), var(--primary-dark)) !important;
            }
            [style*="linear-gradient(135deg,#EFF6FF"], [style*="linear-gradient(135deg,#EFF6FF,#DBEAFE)"], [style*="linear-gradient(135deg, #EFF6FF"] {
                background: linear-gradient(135deg, var(--info-bg), var(--primary-dark)) !important;
            }
            [style*="linear-gradient(135deg,#FFFBEB"], [style*="linear-gradient(135deg, #FFFBEB"],
            [style*="linear-gradient(135deg,#FEF3C7"] {
                background: linear-gradient(135deg, var(--warning-bg), #3a2e12) !important;
            }
            [style*="rgba(255,255,255,0.7)"] { background-color: rgba(22,27,34,.7) !important; }

            [style*="border:#E8F0F3"], [style*="border:1px solid #E8F0F3"], [style*="border-color:#E8F0F3"] { border-color: var(--border) !important; }
            [style*="border:#EAF2F5"], [style*="border:#D5EAF1"], [style*="border:#BFDBFE"], [style*="border:#BBF7D0"],
            [style*="border:#c8d8e0"] { border-color: var(--border) !important; }
        </style>
        """
        st.markdown(dark_remap, unsafe_allow_html=True)
