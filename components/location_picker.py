# Phase 4 — Location Picker Component (M3)
# Manual city input is the DEFAULT (browser geolocation is secondary).
# Streamlit geolocation is inconsistent — city input is more reliable.

import streamlit as st
from utils.osm_service import geocode_city
import utils.database as db


def render_location_picker(disease: str = "", show_recent: bool = True) -> tuple:
    """
    Render the location picker UI.
    Returns (city_name, lat, lng) — all may be None if not yet set.

    Args:
        disease:      Used for logging recent searches (e.g. "Diabetes")
        show_recent:  Whether to show recent searches dropdown
    """
    st.markdown("""
    <div class="premium-info-banner">
        <h4>📍 Find Nearby Specialists</h4>
        <p>Enter your city to find the best hospitals and clinics near you.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Manual City Input (DEFAULT) ───────────────────
    col_city, col_btn = st.columns([3, 1])
    with col_city:
        default_val = st.session_state.get("user_city", "")
        city_input = st.text_input(
            "🏙️ Enter Your City",
            value=default_val,
            placeholder="e.g. Mumbai, Delhi, Bangalore, Chennai",
            key="loc_city_input"
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", key="loc_search_btn", use_container_width=True)

    # ── GPS Option (Secondary) ─────────────────────────
    with st.expander("📡 Or use my current GPS location (may not work in all browsers)"):
        st.info("💡 Click the button below. Your browser will ask for location permission.")

        # JS geolocation component
        geo_html = """
        <div id="geo_status" style="font-size:13px;color:#6B7280;margin-bottom:8px;">
            Status: Waiting for location...
        </div>
        <script>
        function getLocation() {
            var status = document.getElementById('geo_status');
            if (navigator.geolocation) {
                status.innerHTML = '⏳ Requesting GPS...';
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        status.innerHTML = '✅ Location detected: ' +
                            pos.coords.latitude.toFixed(4) + ', ' +
                            pos.coords.longitude.toFixed(4);
                        var lat = pos.coords.latitude;
                        var lng = pos.coords.longitude;
                        var input_lat = window.parent.document.querySelector(
                            'input[aria-label="GPS_LAT"]');
                        var input_lng = window.parent.document.querySelector(
                            'input[aria-label="GPS_LNG"]');
                        if (input_lat) { input_lat.value = lat; input_lat.dispatchEvent(new Event('input', {bubbles:true})); }
                        if (input_lng) { input_lng.value = lng; input_lng.dispatchEvent(new Event('input', {bubbles:true})); }
                    },
                    function(err) {
                        status.innerHTML = '❌ Location denied or unavailable. Please use city input instead.';
                    }
                );
            } else {
                status.innerHTML = '❌ Geolocation not supported in this browser.';
            }
        }
        </script>
        <button onclick="getLocation()" style="
            background:#3B82F6;color:white;border:none;
            padding:8px 18px;border-radius:8px;cursor:pointer;font-size:14px;">
            📍 Detect My Location
        </button>
        """
        st.components.v1.html(geo_html, height=90)
        st.caption("If GPS fails, close this and use the city input above — it works better on Streamlit.")

        # Hidden input fields for GPS coordinates (M3)
        st.markdown('<div style="display:none;">', unsafe_allow_html=True)
        gps_lat = st.text_input("GPS_LAT", key="gps_lat_input")
        gps_lng = st.text_input("GPS_LNG", key="gps_lng_input")
        st.markdown('</div>', unsafe_allow_html=True)

        if gps_lat and gps_lng:
            try:
                lat_val = float(gps_lat)
                lng_val = float(gps_lng)
                if st.session_state.get("user_lat") != lat_val or st.session_state.get("user_lng") != lng_val:
                    from utils.osm_service import reverse_geocode_coords
                    city_name = reverse_geocode_coords(lat_val, lng_val) or "GPS Location"
                    st.session_state["user_city"] = city_name
                    st.session_state["user_lat"] = lat_val
                    st.session_state["user_lng"] = lng_val
                    st.rerun()
            except Exception:
                pass

    # ── Process Search ─────────────────────────────────
    if search_clicked and city_input and city_input.strip():
        city = city_input.strip()
        with st.spinner(f"📡 Locating {city}..."):
            lat, lng = geocode_city(city)

        if lat and lng:
            st.session_state["user_city"] = city
            st.session_state["user_lat"]  = lat
            st.session_state["user_lng"]  = lng

            # Log to recent searches (Removed per DB cleanup)
            pass

            st.success(f"✅ Location found: {city} ({lat:.4f}, {lng:.4f})")
        else:
            st.error(f"❌ Could not locate '{city}'. Try a different spelling or add the state (e.g. 'Mumbai, Maharashtra').")

    # ── Return current location state ──────────────────
    city = st.session_state.get("user_city", "")
    lat  = st.session_state.get("user_lat")
    lng  = st.session_state.get("user_lng")

    # Show active location chip
    if city and lat:
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:var(--success-bg);border:1px solid var(--border);
                    padding:6px 14px;border-radius:999px;margin-top:6px;">
            <span style="color:var(--success);font-size:18px;">📍</span>
            <span style="color:var(--text);font-size:14px;font-weight:600;">
                {city} &nbsp;·&nbsp; {lat:.4f}°N, {lng:.4f}°E
            </span>
        </div>
        """, unsafe_allow_html=True)

    return city, lat, lng


def clear_location():
    """Reset saved location from session state."""
    for key in ["user_city", "user_lat", "user_lng"]:
        st.session_state.pop(key, None)
