#import re
import asyncio
import streamlit as st
from datetime import date, datetime
from mcp_travel_planner import run_mcp_travel_planner
from ics_generator import generate_ics_content
import os

# Load API keys from Streamlit secrets
# For local development, create a .streamlit/secrets.toml file.
# See https://docs.streamlit.io/library/advanced-features/secrets-management
groq_key = st.secrets.get("GEMINI_API_KEY")
google_maps_key = st.secrets.get("GOOGLE_MAPS_API_KEY")



def run_travel_planner(destination: str, num_days: int, preferences: str, budget: int, gemini_key: str, google_maps_key: str):
    """Synchronous wrapper for the async MCP travel planner."""
    return asyncio.run(run_mcp_travel_planner(destination, num_days, preferences, budget, gemini_key, google_maps_key))
    
# -------------------- Streamlit App --------------------

# Configure the page
st.set_page_config(   
    page_title="MCP AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None

# Title and description
st.title("✈️ MCP AI Travel Planner")
st.caption("Plan your next adventure with AI Travel Planner using MCP servers for real-time data access")

# Check if API keys are loaded
if not groq_key or not google_maps_key:
    st.error("API keys are not configured. Please add them to your Streamlit Cloud secrets.")
else:
    # Main input section
    st.header("🌍 Trip Details")

    col1, col2 = st.columns(2)

    with col1:
        destination = st.text_input("Destination", placeholder="e.g., Paris, Tokyo, New York")
        num_days = st.number_input("Number of Days", min_value=1, max_value=30, value=7)

    with col2:
        budget = st.number_input("Budget (USD)", min_value=100, max_value=10000, step=100, value=2000)
        start_date = st.date_input("Start Date", min_value=date.today(), value=date.today())

    # Preferences section
    st.subheader("🎯 Travel Preferences")
    preferences_input = st.text_area(
        "Describe your travel preferences",
        placeholder="e.g., adventure activities, cultural sites, food, relaxation, nightlife...",
        height=100
    )

    # Quick preference buttons
    quick_prefs = st.multiselect(
        "Quick Preferences (optional)",
        ["Adventure", "Relaxation", "Sightseeing", "Cultural Experiences",
         "Beach", "Mountain", "Luxury", "Budget-Friendly", "Food & Dining",
         "Shopping", "Nightlife", "Family-Friendly"],
        help="Select multiple preferences or describe in detail above"
    )

    # Combine preferences
    all_preferences = []
    if preferences_input:
        all_preferences.append(preferences_input)
    if quick_prefs:
        all_preferences.extend(quick_prefs)

    preferences = ", ".join(all_preferences) if all_preferences else "General sightseeing"

    # Generate button
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🎯 Generate Itinerary", type="primary"):
            if not destination:
                st.error("Please enter a destination.")
            elif not preferences:
                st.warning("Please describe your preferences or select quick preferences.")
            else:
                tools_message = "🏨 Connecting to Airbnb MCP"
                if google_maps_key:
                    tools_message += " and Google Maps MCP"
                tools_message += ", creating itinerary..."

                with st.spinner(tools_message):
                    try:
                        # Calculate number of days from start date
                        response = run_travel_planner(
                            destination=destination,
                            num_days=num_days,
                            preferences=preferences,
                            budget=budget,
                            gemini_key=groq_key,
                            google_maps_key=google_maps_key
                        )

                        # Store the response in session state
                        st.session_state.itinerary = response

                        # Show MCP connection status
                        if "Airbnb" in response and ("listing" in response.lower() or "accommodation" in response.lower()):
                            st.success("✅ Your travel itinerary is ready with Airbnb data!")
                            st.info("🏨 Used real Airbnb listings for accommodation recommendations")
                        else:
                            st.success("✅ Your travel itinerary is ready!")
                            st.info("📝 Used general knowledge for accommodation suggestions (Airbnb MCP may have failed to connect)")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.info("Please try again or check your internet connection.")

    with col2:
        if st.session_state.itinerary:
            # Generate the ICS file
            ics_content = generate_ics_content(st.session_state.itinerary, datetime.combine(start_date, datetime.min.time()))

            # Provide the file for download
            st.download_button(
                label="📅 Download as Calendar",
                data=ics_content,
                file_name="travel_itinerary.ics",
                mime="text/calendar"
            )

    # Display itinerary
    if st.session_state.itinerary:
        st.header("📋 Your Travel Itinerary")
        st.markdown(st.session_state.itinerary)
