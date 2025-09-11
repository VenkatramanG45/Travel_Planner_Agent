import streamlit as st
import asyncio
import os
from mcp_travel_planner import run_mcp_travel_planner

st.set_page_config(layout="wide")

st.title("MCP Travel Planner")

st.markdown("""
This application uses the MCP Travel Planner to generate detailed travel itineraries.
Fill in the details below and click 'Generate Itinerary'.
""")

# Input fields for travel planning
destination = st.text_input("Destination", "Paris, France")
num_days = st.number_input("Number of Days", min_value=1, max_value=30, value=5)
preferences = st.text_area("Preferences (e.g., historical sites, food tours, nightlife)", "Historical sites, art museums, good food")
budget = st.number_input("Budget (USD total)", min_value=100, value=2000)

# API Key inputs
# Retrieve API keys from environment variables
gemini_api_key = os.environ.get("GEMINI_API_KEY")
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

if st.button("Generate Itinerary"):
    if not gemini_api_key or not google_maps_api_key:
        st.error("API keys are not configured in environment variables. Please set GEMINI_API_KEY and GOOGLE_MAPS_API_KEY.")
    else:
        with st.spinner("Generating your itinerary... This may take a few minutes.Airbnb MCP is Calling"):
            try:
                itinerary = asyncio.run(run_mcp_travel_planner(
                    destination=destination,
                    num_days=num_days,
                    preferences=preferences,
                    budget=budget,
                    gemini_key=gemini_api_key,
                    google_maps_key=google_maps_api_key
                ))
                st.success("Itinerary Generated!")
                st.markdown(itinerary)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.warning("Please ensure your API keys are correct and the MCP servers are running if you are running locally.")

