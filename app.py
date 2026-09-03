import streamlit as st
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Define Structured JSON Output Schema using Pydantic
class OutfitSuggestion(BaseModel):
    brand_name: str = Field(description="Name of the real Pakistani retail brand (e.g., Sapphire, Khaadi, Ethnic, Alkaram, Nishat Linen, J.)")
    article_name: str = Field(description="The specific catalog name or title of the exact dress article (e.g., 'Embroidered Lawn Shaila', 'Shadow Muse A', 'Floral Breeze Co-Ord')")
    article_sku: str = Field(description="The alphanumeric item code or SKU identifier string characteristic of the brand (e.g., '3PESGS26V769', '0T3PSLS25V51', 'EST23490')")
    price_pkr: int = Field(description="Approximate current retail price in PKR as an integer code matching realistic tier bounds")
    fabric: str = Field(description="Fabric material verified or matched")
    category: str = Field(description="Style category matching user choice (e.g., Embroidered, Simple Casual)")
    color: str = Field(description="Primary color shade of the dress item")
    design_details: str = Field(description="A highly specific description detailing the print motif, neckline style, embroidery patches, and composition of the individual article pieces.")
    specific_product_url: str = Field(description="A deep link pointing directly to the individual product page for that specific item SKU on the official web store (e.g., https://sapphireonline.pk or similar direct brand layout). Do not provide a general landing page or collection catalog index.")

class OutfitList(BaseModel):
    suggestions: list[OutfitSuggestion]

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="LibasAI - Specific Article Finder", page_icon="👗", layout="wide")

st.title("👗 LibasAI: Specific Article Finder")
st.write("Find individual Pakistani retail brand dresses matching your constraints with direct item deep links.")

# Sidebar configuration for API Credentials
with st.sidebar:
    st.header("🔑 API Settings")
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Enter Gemini API Key", value=default_key, type="password", 
                            help="Get an API key from Google AI Studio. Leave empty to run in Simulator mode.")
    
    if api_key:
        st.success("API Key active!")
    else:
        st.info("💡 Running in **Simulator Mode**. Provide an active Gemini API Key to fetch live dynamic AI suggestions.")

# Main Input Layout Form Split into Columns
st.subheader("🎨 Customize Your Search Requirements")
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
    color = st.text_input("Preferred Color(s)", placeholder="e.g., Mustard Yellow, Indigo Blue, Crimson Red, Jet Black")
    max_price = st.slider("Maximum Budget Limit (PKR)", min_value=2000, max_value=30000, value=8500, step=500)

# Submit query
if st.button("✨ Search Specific Articles", type="primary"):
    if not color.strip():
        st.warning("Please enter a preferred color to help narrow down the item catalog.")
    else:
        # Strict explicit formatting prompt instruction
        prompt = f"""
        Find 3 realistic individual dress articles from real retail fashion brands in Pakistan that match these criteria:
        - Style Category: {category}
        - Fabric Base: {fabric}
        - Color Vibe: {color}
        - Max Price Limit: {max_price} PKR
        
        CRITICAL RULE: Do not suggest broad collection roots or main directory links. You must generate or target a deep individual product url routing path unique to that specific item code/SKU structure.
        """

        with st.spinner("Filtering specific brand collections... Please wait..."):
            if api_key:
                try:
                    # Initialize the modern official Google GenAI Client
                    client = genai.Client(api_key=api_key)
                    
                    # Request structured json layout from gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="You are a meticulous fashion scanner for Pakistani apparel brands. Recommend actual, highly granular individual dress items. Ensure each item contains a highly specific item code (SKU) and a corresponding product-specific deep purchase link pattern pointing directly to that article's final detail page.",
                            response_mime_type="application/json",
                            response_schema=OutfitList,
                            temperature=0.25
                        ),
                    )
                    
                    data = json.loads(response.text)
                    results = data.get("suggestions", [])
                    
                except Exception as e:
                    st.error(f"AI Generation Error: {str(e)}")
                    results = []
            else:
                # --- UI SIMULATOR FALLBACK DATA FOR SPECIFIC ARTICLES ---
                results = [
                    {
                        "brand_name": "Sapphire",
                        "article_name": f"Shadow Muse {fabric} Ensemble",
                        "article_sku": "3PESGS26V769",
                        "price_pkr": int(max_price * 0.80),
                        "fabric": fabric,
                        "category": category,
                        "color": color,
                        "design_details": f"A distinct 3-piece composition featuring detailed embroidery layouts across a {color} palette base canvas.",
                        "specific_product_url": f"https://sapphireonline.pk"
                    },
                    {
                        "brand_name": "Khaadi",
                        "article_name": f"Geometric Block Printed {category} Top",
                        "article_sku": "EST23490",
                        "price_pkr": int(max_price * 0.65),
                        "fabric": fabric,
                        "category": category,
                        "color": color,
                        "design_details": f"A contemporary styled shirt silhouette accentuating rich {color} design layers with fine stitching panels along the borders.",
                        "specific_product_url": f"https://khaadi.com"
                    }
                ]
            
            # --- DISPLAY THE SPECIFIC ARTICLE SCHEMATIC RESULTS ---
            if results:
                st.success(f"🎉 Found {len(results)} distinct articles matching your criteria!")
                
                for idx, item in enumerate(results):
                    with st.container(border=True):
                        c_left, c_right = st.columns([3, 1])
                        with c_left:
                            st.markdown(f"### 🏷️ {item['brand_name']} — **{item['article_name']}**")
                            st.caption(f"**SKU / Article Code Reference:** {item['article_sku']}")
                            st.write(item['design_details'])
                            
                            st.markdown(f"**🎨 Colorway:** {item['color']} | **🧵 Fabric Base:** {item['fabric']} | **📂 Type:** {item['category']}")
                        
                        with c_right:
                            st.markdown(f"<h3 style='text-align: right; margin-top: 10px;'>Rs. {item['price_pkr']:,}</h3>", unsafe_allow_html=True)
                            
                            # Distinct styled purchase anchor button pointing directly to specific item page
                            button_html = f"""
                            <div style='text-align: right; margin-top: 25px;'>
                                <a href="{item['specific_product_url']}" target="_blank" style="display: inline-block; padding: 0.6em 1.2em; color: white; background-color: #000000; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 14px;">🛒 Shop Article</a>
                            </div>
                            """
                            st.markdown(button_html, unsafe_allow_html=True)
            else:
                st.error("Could not trace clean specific article schemas. Please broaden budget constraints or change fabric parameters.")
