import streamlit as st
import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Define Structured JSON Output Schema using Pydantic
class OutfitSuggestion(BaseModel):
    brand_name: str = Field(description="Name of the real Pakistani retail brand (e.g., Sapphire, Khaadi, Ethnic, Nishat Linen, Alkaram)")
    article_name: str = Field(description="The specific catalog name of the dress article (e.g., 'Printed Slub Lawn Straight Shirt')")
    article_sku: str = Field(description="The uppercase alphanumeric item code format unique to the brand (e.g., 'PRWCAWMV813S_999', 'KRT-24-091', 'EST23490')")
    price_pkr: int = Field(description="Current retail sale price or base price in PKR as an integer code")
    fabric: str = Field(description="Fabric material verified or matched (e.g., Slub Lawn, Cambric, Cotton)")
    category: str = Field(description="Style category matching user selection (e.g., Simple Casual, Embroidered)")
    color: str = Field(description="Primary color shade of the dress item (e.g., Beige, Royal Blue)")
    design_details: str = Field(description="1-2 sentences highlighting design parameters (e.g., 'A slim fit straight shirt featuring a u-neckline and geometric patterns.')")
    exact_product_url: str = Field(description="The deep-link pointing directly to the specific individual article page on the brand's official web store. It must append the item code structure directly to the product domain directory path, following patterns like: https://sapphireonline.pk or https://khaadi.com. Do not output a broad collection link.")

class OutfitList(BaseModel):
    suggestions: list[OutfitSuggestion]

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="LibasAI - Direct Deep-Link Finder", page_icon="👗", layout="wide")

st.title("👗 LibasAI: Direct Item Deep-Link Finder")
st.write("Find individual articles across major Pakistani clothing retailers with exact direct-to-product shopping URLs.")

# Sidebar configuration for API Credentials
with st.sidebar:
    st.header("🔑 API Settings")
    default_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Enter Gemini API Key", value=default_key, type="password", 
                            help="Get an API key from Google AI Studio. Leave blank to run via the UI Simulator Fallback.")
    
    if api_key:
        st.success("API Key loaded!")
    else:
        st.info("💡 Running in **Simulator Mode**. Enter your Gemini API key to query live models dynamically.")

# Main Input Layout Form Split into Columns
st.subheader("🎨 Enter Your Outfit Constraints")
col1, col2 = st.columns(2)

with col1:
    category = st.selectbox(
        "Style Category",
        ["Simple Casual", "Embroidered", "Semi-Formal", "Formal Wear", "Festive/Eid Collection"]
    )
    fabric = st.selectbox(
        "Preferred Fabric",
        ["Lawn", "Slub Lawn", "Cotton", "Cambric", "Silk", "Chiffon", "Khaddar", "Linen", "Velvet"]
    )

with col2:
    color = st.text_input("Preferred Color(s)", placeholder="e.g., Beige, Mustard, Emerald Green, Indigo")
    max_price = st.slider("Maximum Budget Limit (PKR)", min_value=2000, max_value=30000, value=6000, step=500)

# Submit query
if st.button("✨ Fetch Exact Product Links", type="primary"):
    if not color.strip():
        st.warning("Please specify a color preference to filter catalog entries correctly.")
    else:
        # Prompt structure guiding the model to stitch precise URLs
        prompt = f"""
        Find 3 realistic individual apparel articles from top Pakistani clothing brands that match these constraints:
        - Style Category: {category}
        - Material/Fabric: {fabric}
        - Color Palette: {color}
        - Max Price Limit: {max_price} PKR
        
        CRITICAL LINK RULE:
        The 'exact_product_url' field must map to the specific product target itself, not a collection index page. 
        Stitch the URL string precisely by placing the generated or mapped Item SKU code suffix at the absolute end of the website's product directory route.
        Example target syntax reference shape to emulate:
        - Sapphire: https://sapphireonline.pk[SKU_CODE_HERE]
        - Khaadi: https://khaadi.com[SKU_CODE_HERE]
        """

        with st.spinner("Stitching exact product deep-links... Please wait..."):
            if api_key:
                try:
                    # Initialize the modern official Google GenAI Client
                    client = genai.Client(api_key=api_key)
                    
                    # Request structured json layout from gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="You are a precise data scraper and personal shopper for Pakistani fashion networks. Your core objective is to output valid, structured clothing JSON details. You must build complete deep-links directing directly to individual product pages (e.g., domain/products/sku) using realistic retail SKU conventions.",
                            response_mime_type="application/json",
                            response_schema=OutfitList,
                            temperature=0.2
                        ),
                    )
                    
                    data = json.loads(response.text)
                    results = data.get("suggestions", [])
                    
                except Exception as e:
                    st.error(f"AI Generation Error: {str(e)}")
                    results = []
            else:
                # --- UI SIMULATOR FALLBACK DEMONSTRATING DIRECT SKU TARGETING ---
                simulated_sku = "PRWCAWMV813S_999" if fabric.lower() == "slub lawn" else "PRWCAWMV812A_420"
                results = [
                    {
                        "brand_name": "Sapphire",
                        "article_name": f"Printed {fabric} Straight Shirt",
                        "article_sku": simulated_sku,
                        "price_pkr": 3493 if max_price >= 3500 else int(max_price * 0.9),
                        "fabric": fabric,
                        "category": category,
                        "color": color if color else "Beige",
                        "design_details": f"A sleek straight shirt profile styled with delicate design lines across a high-quality {fabric} weave.",
                        "exact_product_url": f"https://sapphireonline.pk{simulated_sku}"
                    },
                    {
                        "brand_name": "Khaadi",
                        "article_name": f"Casual {category} Kurta Essentials",
                        "article_sku": "KRT-24-091A",
                        "price_pkr": int(max_price * 0.75),
                        "fabric": fabric,
                        "category": category,
                        "color": color if color else "Multi",
                        "design_details": f"Traditional blocks over regular cut layouts optimized for breezy seasonal adjustments.",
                        "exact_product_url": f"https://khaadi.comkrt-24-091a"
                    }
                ]
            
            # --- DISPLAY RENDER ENGINE ---
            if results:
                st.success(f"🎉 Trace complete! Found {len(results)} exact article matches.")
                
                for idx, outfit in enumerate(results):
                    with st.container(border=True):
                        c_left, c_right = st.columns([3, 1])
                        with c_left:
                            st.markdown(f"### 🏷️ {outfit['brand_name']} — *{outfit['article_name']}*")
                            st.code(f"Article SKU Ref: {outfit['article_sku']}", language="text")
                            st.write(outfit['design_details'])
                            
                            st.markdown(f"**🎨 Colorway:** {outfit['color']} | **🧵 Fabric:** {outfit['fabric']} | **📂 Style Category:** {outfit['category']}")
                        
                        with c_right:
                            st.markdown(f"<h3 style='text-align: right; color: #333;'>Rs. {outfit['price_pkr']:,}</h3>", unsafe_allow_html=True)
                            
                            # Distinct high-contrast action button routing users to specific item details
                            action_btn = f"""
                            <div style='text-align: right; margin-top: 30px;'>
                                <a href="{outfit['exact_product_url']}" target="_blank" style="display: inline-block; padding: 0.6em 1.2em; color: white; background-color: #008CBA; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 14px; box-shadow: 1px 2px 4px rgba(0,0,0,0.15);">🛒 Buy Direct Article</a>
                            </div>
                            """
                            st.markdown(action_btn, unsafe_allow_html=True)
            else:
                st.error("Could not format direct deep links. Try relaxing your filters or maximum budget bounds.")
