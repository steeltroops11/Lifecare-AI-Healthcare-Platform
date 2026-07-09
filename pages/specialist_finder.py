# Phase 4 — Specialist Finder Page (M6)
# Full pipeline: Location → OSM Search → AI Filter → Ranking → M9 Best Pick → Appointment Request

import streamlit as st
from components.location_picker import render_location_picker
from components.cards import (
    hospital_card, ai_best_hospital_card, appointment_request_form
)
from utils.osm_service import search_specialists, get_directions_url, get_osm_view_url, DISEASE_TO_SPECIALTY
from utils.hospital_ranker import rank_hospitals, get_ai_best_pick
import utils.database as db


def show():
    st.header("🏥 Smart Specialist Finder")
    st.caption("AI-powered nearby specialist search using OpenStreetMap — 100% free, no billing.")

    # ── Pull last prediction from session ────────────────
    disease   = st.session_state.get("specialist_disease", "")
    risk      = st.session_state.get("specialist_risk", 0.0)
    risk_level = st.session_state.get("specialist_risk_level", "MODERATE")
    specialist = st.session_state.get("specialist_type", "General Physician")
    emergency  = st.session_state.get("specialist_emergency", False)
    rec_obj   = st.session_state.get("specialist_rec_obj", {})

    # ── Section 1: Disease Risk Summary Banner ─────────────
    if disease:
        color_map = {
            "LOW": ("var(--success)", "var(--success-bg)"),
            "MODERATE": ("var(--warning)", "var(--warning-bg)"),
            "HIGH": ("var(--accent)", "var(--accent-bg)"),
            "CRITICAL": ("var(--danger)", "var(--danger-bg)"),
        }
        emoji_map = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}
        color, bg = color_map.get(risk_level, ("var(--text-soft)", "var(--card)"))
        emoji = emoji_map.get(risk_level, "⚪")

        st.markdown(f"""
        <div style="background:{bg};border:1.5px solid {color};border-radius:18px;
                    padding:20px 24px;margin-bottom:20px;">
            <div style="display:flex;align-items:center;gap:16px;">
                <span style="font-size:36px;">{emoji}</span>
                <div>
                    <h4 style="margin:0;color:var(--text);font-size:18px;font-weight:800;">
                        {disease} — Risk: {risk*100:.1f}%
                    </h4>
                    <p style="margin:4px 0 0;color:{color};font-size:14px;font-weight:600;">
                        {risk_level} · Recommended Specialist: {specialist}
                    </p>
                    <p style="margin:4px 0 0;color:var(--text-body);font-size:13px;">
                        {rec_obj.get('urgency', '')}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # No disease selected — let user pick manually
        st.info("💡 Run a disease prediction first and click 'Find Specialist', or search manually below.")
        disease_opts = ["Diabetes", "Heart Disease", "Kidney Disease", "Readmission"]
        disease = st.selectbox("Select Disease Specialty to Search", disease_opts, key="finder_disease_select")
        risk_level = st.selectbox("Risk Level", ["LOW", "MODERATE", "HIGH", "CRITICAL"], index=2, key="finder_risk_level")
        specialist = {
            "Diabetes": "Endocrinologist",
            "Heart Disease": "Cardiologist",
            "Kidney Disease": "Nephrologist",
            "Readmission": "General Physician"
        }.get(disease, "General Physician")
        emergency = (risk_level == "CRITICAL")

    # Adaptive Radius Logic (Risk-based)
    radius_map = {
        "LOW": 5.0,
        "MODERATE": 10.0,
        "HIGH": 15.0,
        "CRITICAL": 30.0
    }
    radius = radius_map.get(risk_level, 10.0)

    # ── Section 2: CRITICAL Emergency Banner ──────────────
    if emergency or risk_level == "CRITICAL":
        st.markdown("""
        <div style="background:var(--danger-bg);border:2px solid var(--danger);border-radius:16px;
                    padding:18px 22px;margin-bottom:12px;
                    animation: pulse 1.5s infinite;">
            <style>@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.7} }</style>
            <h3 style="margin:0;color:var(--danger);font-size:18px;font-weight:800;">
                🚨 CRITICAL RISK DETECTED — Emergency Care Required
            </h3>
            <p style="margin:6px 0 0;color:var(--text);font-size:14px;">
                Only fully equipped hospitals are recommended. Please seek care immediately.<br>
                ☎️ <strong>Emergency: Call 108</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Emergency call button
        st.link_button("☎️ CALL 108 — Emergency Ambulance", "tel:108",
                        use_container_width=True)

        # ── Auto-display Nearest Emergency Hospital (M4) ──
        user_city_state = st.session_state.get("user_city", "")
        u_lat = st.session_state.get("user_lat")
        u_lng = st.session_state.get("user_lng")

        if u_lat and u_lng and user_city_state:
            st.markdown("##### 🚑 Nearest Emergency Hospital (Auto-Detected):")
            # Cache-friendly search
            with st.spinner("Finding nearest emergency hospital..."):
                facilities, _, _, _ = search_specialists(
                    city=user_city_state, disease=disease,
                    radius_km=30.0, lat=u_lat, lng=u_lng
                )
            if facilities:
                ranked_emergencies = rank_hospitals(facilities, u_lat, u_lng, disease=disease, risk_level="CRITICAL")
                if ranked_emergencies:
                    nearest = ranked_emergencies[0]
                    n_name = nearest.get("name")
                    n_dist = nearest.get("distance_km")
                    n_addr = nearest.get("address", "Address not available")
                    n_etas = nearest.get("travel_etas", {})
                    n_drv = n_etas.get("driving", 0)

                    st.markdown(f"""
                    <div style="background:var(--card);border-radius:14px;padding:16px 20px;
                                border-left:5px solid var(--danger);box-shadow:0 4px 14px var(--shadow);margin-bottom:12px;">
                        <h4 style="margin:0;color:var(--danger);font-size:16px;font-weight:800;">🏥 {n_name}</h4>
                        <p style="margin:4px 0 0;color:var(--text-soft);font-size:13px;">📍 {n_addr}</p>
                        <p style="margin:4px 0 0;color:var(--primary);font-size:12px;font-weight:700;">⏱️ Drive: {n_drv} mins &nbsp;·&nbsp; 📏 {n_dist} km away</p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_emg_dir, col_emg_call = st.columns(2)
                    with col_emg_dir:
                        st.link_button("🧭 Navigate to Emergency Now", get_directions_url(n_name, nearest.get("lat"), nearest.get("lng")), use_container_width=True)
                    with col_emg_call:
                        if nearest.get("phone"):
                            st.link_button(f"📞 Call Hospital: {nearest.get('phone')}", f"tel:{nearest.get('phone')}", use_container_width=True)
                        else:
                            st.link_button("☎️ Call Emergency Services (108)", "tel:108", use_container_width=True)
            st.markdown("---")

    # ── Section 3: Location Picker ─────────────────────────
    st.markdown("---")
    city, lat, lng = render_location_picker(disease=disease)

    # ── Section 4: Search & Display Results ───────────────
    st.markdown("---")
    if lat and lng and city:
        st.markdown(f"ℹ️ *Search Radius automatically set to **{radius:.0f} km** based on risk level.*")

        search_key = f"finder_results_{city}_{radius}_{disease}"
        if st.button(f"🔍 Find {specialist}s near {city}", key="finder_search_btn",
                     use_container_width=True) or search_key in st.session_state:

            # Run search (with cache)
            if search_key not in st.session_state:
                with st.spinner(f"🔎 Searching for {specialist}s near {city}..."):
                    facilities, _, _, from_cache = search_specialists(
                        city=city, disease=disease,
                        radius_km=radius, lat=lat, lng=lng
                    )
                st.session_state[search_key] = facilities
                if from_cache:
                    st.caption("⚡ Results loaded from cache.")
            else:
                facilities = st.session_state[search_key]

            if not facilities:
                st.warning(f"No hospitals or clinics found near **{city}** within {radius:.0f} km. "
                           f"Try expanding the search radius or check the city name.")
            else:
                # Rank facilities
                ranked = rank_hospitals(facilities, lat, lng, disease=disease, risk_level=risk_level)

                # M9 AI Best Pick
                best_pick = get_ai_best_pick(ranked, disease)

                st.markdown(f"### 🏥 Found {len(ranked)} Facilities near {city}")

                # ── AI Best Pick Card (top of page) ─────────
                if best_pick:
                    ai_best_hospital_card(best_pick, disease)

                st.markdown("---")
                st.markdown("### 📋 All Ranked Facilities")

                # ── Show all ranked facilities ───────────────
                for facility in ranked[:15]:  # show top 15
                    hospital_card(facility, disease)

        else:
            st.info(f"Click **🔍 Find {specialist}s near {city}** to search for nearby facilities.")

    elif city and not lat:
        st.warning("📍 City not geocoded yet. Click the **🔍 Search** button in the location box above first.")
    else:
        st.info("👆 Enter your city above to start searching for nearby specialists.")

    # ── Section 5: Saved Favorites ──────────────────────────
    st.markdown("---")
    patient_email = st.session_state.get("user_email", "")
    if patient_email:
        favorites = db.get_favorites(patient_email)
        if favorites:
            with st.expander(f"⭐ My Saved Clinics ({len(favorites)})"):
                for fav in favorites:
                    col_info, col_dir, col_rem = st.columns([3, 1, 1])
                    with col_info:
                        st.markdown(f"""
                        <div style="background:var(--warning-bg);border-left:3px solid var(--warning);
                                    padding:10px 14px;border-radius:8px;">
                            <strong style="color:var(--text);">⭐ {fav['clinic_name']}</strong><br>
                            <span style="font-size:12px;color:var(--text-soft);">{fav['clinic_address'] or 'Address not available'}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_dir:
                        maps_url = get_directions_url(
                            fav['clinic_name'],
                            fav.get('clinic_lat'),
                            fav.get('clinic_lng')
                        )
                        st.link_button("🗺️ Directions", maps_url, use_container_width=True)
                    with col_rem:
                        if st.button("🗑️ Remove", key=f"rem_fav_{fav['id']}", use_container_width=True):
                            db.remove_favorite(patient_email, fav['clinic_name'])
                            st.rerun()
