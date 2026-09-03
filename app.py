import streamlit as st
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Define Structured JSON Output Schema using Pydantic
class OutfitSuggestion(BaseModel):
    brand_name: str = Field(description="Name of the Pakistani brand (e.g., Khaadi, Sapphire, Ethnic, Sana Safinaz, J.)")
    outfit_title: str = Field(description="Name or title of the dress/outfit")
    price_pkr: int = Field(description="Approximate retail price in PKR as an integer")
    fabric: str = Field(description="Fabric material verified or matched")
    category: str = Field(description="Style category matching user choice (e.g., Embroidered, Simple Casual, Formal)")
    color: str = Field(description="Primary color of the dress")
    description: str = Field(description="Short 1-2 sentence description explaining why this fits the user's requirements.")
    website_url: str = Field(description="The realistic direct URL to this category or collection on the official brand website (e.g., https://sapphireonline.pk or https://khaadi.com)")

class OutfitList(BaseModel):
    suggestions: list[OutfitSuggestion]

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="LibasAI - Pakistani Outfit Finder", page_icon="👗", layout="wide")

st.title("👗 LibasAI: Pakistani Brand Outfit Finder")
st.write("Specify your style preferences to search across major Pakistani fashion houses using AI.")

# Sidebar configuration for API Credentials
with st.sidebar:
    st.header("🔑 API Settings")
    # Tries to pull from Streamlit Secrets or Environment variable first
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Enter Gemini API Key", value=default_key, type="password", 
                            help="Get an API key from Google AI Studio. Leave empty to use UI Simulator Mode.")
    
    if api_key:
        st.success("API Key loaded successfully!")
    else:
        st.info("💡 Running in **Simulator Mode**. Enter a real Gemini API Key to fetch live dynamic AI suggestions.")

# Main Input Layout Form Split into Columns
st.subheader("🎨 Tell Us What You're Looking For")
col1, col2 = st.columns(2)

with col1:
    category = st.selectbox(
        "Style Category",
        ["Simple Casual", "Embroidered", "Semi-Formal", "Formal Wear", "Festive/Eid Collection"]
    )
    fabric = st.selectbox(
        "Preferred Fabric",
        ["Lawn", "Cotton", "Cambric", "Silk", "Chiffon", "Khaddar", "Linen", "Velvet"]
    )

with col2:
    color = st.text_input("Preferred Color(s)", placeholder="e.g., Royal Blue, Mustard, Emerald Green, Black")
    max_price = st.slider("Maximum Budget (PKR)", min_value=2000, max_value=30000, value=7500, step=500)

# Submit query
if st.button("✨ Find My Perfect Outfit", type="primary"):
    if not color.strip():
        st.warning("Please specify a preferred color to narrow down the look!")
    else:
        # Build prompt payload
        prompt = f"""
        Find 3 realistic dress options from popular retail fashion brands in Pakistan that fit these criteria exactly:
        - Category/Style: {category}
        - Fabric Type: {fabric}
        - Color: {color}
        - Maximum Price Limit: {max_price} PKR
        
        Ensure each recommendation links to a valid real-world URL structure from the official web stores of popular brands like Sapphire, Khaadi, Ethnic, Alkaram, J., Zellbury, or Nishat Linen.
        """

        with st.spinner("Analyzing Pakistani fashion brands... Please wait..."):
            if api_key:
                try:
                    # Initialize the modern official Google GenAI Client
                    client = genai.Client(api_key=api_key)
                    
                    # Request structured json layout from gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="You are a premium Pakistani fashion personal shopper. Recommend real outfits from top Pakistani retail brands matching the criteria exactly. Provide valid, realistic direct collection or product URLs to their official web stores.",
                            response_mime_type="application/json",
                            response_schema=OutfitList,
                            temperature=0.3
                        ),
                    )
                    
                    # Safely load the JSON dictionary payload
                    data = json.loads(response.text)
                    results = data.get("suggestions", [])
                    
                except Exception as e:
                    st.error(f"AI Generation Error: {str(e)}")
                    results = []
            else:
                # --- UI SIMULATOR FALLBACK DATA ---
                results = [
                    {
                        "brand_name": "Sapphire",
                        "outfit_title": f"Classic {fabric} Solid Item",
                        "price_pkr": int(max_price * 0.75),
                        "fabric": fabric,
                        "category": category,
                        "color": color,
                        "description": f"A beautiful daily staple from their latest runway look featuring premium {fabric} stitching accents.",
                        "website_url": "https://sapphireonline.pk"
                    },
                    {
                        "brand_name": "Khaadi",
                        "outfit_title": f"Contemporary {category} Print",
                        "price_pkr": int(max_price * 0.90),
                        "fabric": fabric,
                        "category": category,
                        "color": color,
                        "description": f"Traditional geometric prints overlaying crisp {color} color blocks designed for modern comfort.",
                        "website_url": "https://khaadi.com"
                    }
                ]
            
            # --- DISPLAY THE RESULTS ---
            if results:
                st.success(f"🎉 Found {len(results)} matching options for you!")
                
                for idx, outfit in enumerate(results):
                    with st.container(border=True):
                        c_left, c_right = st.columns([3, 1])
                        with c_left:
                            st.markdown(f"### 🏷️ {outfit['brand_name']} - *{outfit['outfit_title']}*")
                            st.write(outfit['description'])
                            
                            # Clean structured metadata tags
                            st.markdown(f"**🎨 Color:** {outfit['color']} | **🧵 Fabric:** {outfit['fabric']} | **📂 Category:** {outfit['category']}")
                        
                        with c_right:
                            st.markdown(f"### **Rs. {outfit['price_pkr']:,}**")
                            # Explicitly name the platform source anchor link for transparency
                            st.markdown(
                                f'<a href="{outfit["website_url"]}" target="_blank" style="display: inline-block; padding: 0.5em 1em; color: white; background-color: #FF4B4B; border-radius: 5px; text-decoration: none; font-weight: bold;">🛒 Buy from Brand Site</a>', 
                                unsafe_allow_html=True
                            )
            else:
                st.error("No items matching your specific parameters could be successfully processed. Try easing budget parameters.")
