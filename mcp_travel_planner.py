from textwrap import dedent
#from agno.agent import Agent
from agno.tools.mcp import MultiMCPTools
#from agno.tools.googlesearch import GoogleSearchTools
import google.generativeai as genai
import os

async def run_mcp_travel_planner(destination: str, num_days: int, preferences: str, budget: int, gemini_key: str, google_maps_key: str):
    """Run the MCP-based travel planner agent with real-time data access."""

    try:
        genai.configure(api_key=gemini_key)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        # Set Google Maps API key environment variable
        os.environ["GOOGLE_MAPS_API_KEY"] = google_maps_key

        # Initialize MCPTools with Airbnb MCP
        mcp_tools = MultiMCPTools(
            [
                "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt",
                "npx @gongrzhe/server-travelplanner-mcp",
            ],
            env={
                "GOOGLE_MAPS_API_KEY": google_maps_key,
            },
            timeout_seconds=180,
        )

        # Connect to Airbnb MCP server
        await mcp_tools.connect()

        # Create the planning prompt
        prompt = f"""
        IMMEDIATELY create an extremely detailed and comprehensive travel itinerary for:

        **Destination:** {destination}
        **Duration:** {num_days} days
        **Budget:** ${budget} USD total
        **Preferences:** {preferences}

        DO NOT ask any questions. Generate a complete, highly detailed itinerary now using all available tools.

        **CRITICAL REQUIREMENTS:**
        - Use Google Maps MCP to calculate distances and travel times between ALL locations
        - Include specific addresses for every location, restaurant, and attraction
        - Provide detailed timing for each activity with buffer time between locations
        - Calculate precise costs for transportation between each location
        - Include opening hours, ticket prices, and best visiting times for all attractions
        - Provide detailed weather information and specific packing recommendations

        **REQUIRED OUTPUT FORMAT:**
        1. **Trip Overview** - Summary, total estimated cost breakdown, detailed weather forecast
        2. **Accommodation** - 3 specific Airbnb options with real prices, addresses, amenities, and distance from city center
        3. **Transportation Overview** - Detailed transportation options, costs, and recommendations
        4. **Day-by-Day Itinerary** - Extremely detailed schedule with:
           - Specific start/end times for each activity
           - Exact distances and travel times between locations (use Google Maps MCP)
           - Detailed descriptions of each location with addresses
           - Opening hours, ticket prices, and best visiting times
           - Estimated costs for each activity and transportation
           - Buffer time between activities for unexpected delays
        5. **Dining Plan** - Specific restaurants with addresses, price ranges, cuisine types, and distance from accommodation
        6. **Detailed Practical Information**:
           - Weather forecast with clothing recommendations
           - Currency exchange rates and costs
           - Local transportation options and costs
           - Safety information and emergency contacts
           - Cultural norms and etiquette tips
           - Communication options (SIM cards, WiFi, etc.)
           - Health and medical considerations
           - Shopping and souvenir recommendations

        Use Airbnb MCP for real accommodation data, Google Maps MCP for ALL distance calculations and location services, and web search for current information.
        Make reasonable assumptions and fill in any gaps with your knowledge.
        Generate the complete, highly detailed itinerary in one response without asking for clarification.
        """

        # Use Gemini model to generate the itinerary
        response = gemini_model.generate_content(prompt)
        return response.text

    finally:
        await mcp_tools.close()