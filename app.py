import streamlit as st
import os
import json
try:
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback placeholder for environments without the new SDK installed during initial setup
    pass

# Set page configuration
st.set_page_config(
    page_title="Pakistani Outfit Finder",
    page_icon="👗",
    layout="wide"
)

st.title("🇵🇰 AI-Powered Pakistani Outfit Finder")
st.subheader("Find your perfect look across all Pakistani brands")

# Sidebar for API Configuration
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))

if not api_key:
    st.info("💡 Please enter your Gemini API Key in the sidebar to power the smart recommendations, or use the app with demo search capability.")

# User Input Form
with st.form("search_form"):
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Category / Style", ["Casual Simple", "Semi-Formal", "Formal Embroidered", "Bridal Wear", "Kurtas"])
        fabric = st.selectbox("Fabric Type", ["Lawn", "Cotton", "Khaddar", "Silk", "Chiffon", "Velvet", "Organza"])
    with col2:
        color = st.text_input("Color Choice (e.g., Crimson Red, Emerald Green, Pastel Pink)", placeholder="e.g., Royal Blue")
        price_range = st.slider("Max Budget (PKR)", min_value=1000, max_value=50000, value=7500, step=500)
    
    additional_notes = st.text_input("Any specific preferences? (e.g., '3-piece suit', 'minimalist print', 'Sapphire style')")
    submit_btn = st.form_submit_button("Search Outfits")

# System instruction and schema definition for Gemini Flash
SYSTEM_INSTRUCTION = (
    "You are an expert Pakistani fashion personal shopper assistant. "
    "Based on the user's requirements (fabric, color, price, category), you must recommend 3 realistic "
    "outfits from real well-known Pakistani brands (e.g., Sapphire, Khaadi, Sana Safinaz, Maria.B, Alkaram, J., Zara Shahjahan). "
    "Provide realistic product titles, specific prices within their budget, detailed description highlights, "
    "and matching style tips."
)

# Standardized output structure matching user needs
JSON_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "recommendations": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "brand": {"type": "STRING"},
                    "product_name": {"type": "STRING"},
                    "estimated_price_pkr": {"type": "INTEGER"},
                    "fabric": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "styling_tip": {"type": "STRING"}
                },
                "required": ["brand", "product_name", "estimated_price_pkr", "fabric", "description", "styling_tip"]
            }
        }
    },
    "required": ["recommendations"]
}

if submit_btn:
    with st.spinner("✨ Gemini Flash is scanning top Pakistani brands..."):
        if api_key:
            try:
                # Initialize the modern Google GenAI Client
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Find outfits with these strict criteria:
                - Category: {category}
                - Fabric: {fabric}
                - Preferred Color: {color if color else 'Any complementary color'}
                - Maximum Budget: {price_range} PKR
                - Extra preferences: {additional_notes}
                """
                
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=JSON_SCHEMA,
                        temperature=0.3
                    ),
                )
                
                # Parse the structured JSON response
                data = json.loads(response.text)
                recommendations = data.get("recommendations", [])
                
            except Exception as e:
                st.error(f"Error connecting to Gemini API: {str(e)}")
                st.warning("🔄 Showing simulation mode results due to API error.")
                recommendations = []
        else:
            # Simulated fallback recommendations when API key is missing
            recommendations = [
                {
                    "brand": "Sapphire",
                    "product_name": f"Classic {category} Collection Split",
                    "estimated_price_pkr": int(price_range * 0.75),
                    "fabric": fabric,
                    "description": f"A beautiful selection featuring highlighted {color if color else 'traditional'} tones, tailored perfectly for contemporary everyday looks.",
                    "styling_tip": "Pair with statement silver jhumkas and traditional khussas for a complete look."
                },
                {
                    "brand": "Khaadi",
                    "product_name": f"Daily Casuals {fabric} Edition",
                    "estimated_price_pkr": int(price_range * 0.85),
                    "fabric": fabric,
                    "description": f"Intricate patterns focusing on {color if color else 'neutral'} highlights. Breathable and comfortable material.",
                    "styling_tip": "Style with a neat slicked-back ponytail and a metallic minimalist watch."
                }
            ]
        
        # Display Results
        if recommendations:
            st.success(f"Found {len(recommendations)} matching options for you!")
            
            for idx, item in enumerate(recommendations):
                with st.container():
                    st.markdown(f"### {idx+1}. {item['brand']} — {item['product_name']}")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Estimated Price", f"PKR {item['estimated_price_pkr']:,}")
                    c2.metric("Fabric", item['fabric'])
                    c3.metric("Style Match", "High Match")
                    
                    st.markdown(f"**Description:** {item['description']}")
                    st.info(f"💡 **Styling Tip:** {item['styling_tip']}")
                    st.markdown("---")
        else:
            st.warning("No outfits found matching those exact specs. Try broadening your budget or fabric preferences.")
