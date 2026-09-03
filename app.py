import os
import streamlit as st
from google import genai
from google.genai import types

# Page setup
st.set_page_config(
    page_title="Pakistani Fashion Shopping Assistant",
    page_icon="👗",
    layout="wide"
)

st.title("👗 Pakistani Outfit Suggestion Platform")
st.write("Find tailored outfit suggestions with direct purchase links from top Pakistani brands.")

# Sidebar API Key configuration
st.sidebar.header("Settings")
user_api_key = st.sidebar.text_input(
    "Enter Gemini API Key", 
    type="password", 
    help="Get a key from Google AI Studio (aistudio.google.com)"
)

api_key = user_api_key or os.environ.get("GEMINI_API_KEY")

# Input Form
with st.form("fashion_filter_form"):
    st.subheader("Specify Your Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Category / Style",
            ["Simple Casual", "Embroidered", "Formal / Partywear", "Bridal", "Printed Unstitched", "Ready to Wear (Pret)"]
        )
        fabric = st.selectbox(
            "Fabric",
            ["Lawn", "Cotton", "Silk", "Chiffon", "Organza", "Velvet", "Khaddar", "Linen", "Any"]
        )
        pieces = st.selectbox(
            "Number of Pieces",
            ["1-Piece (Kurti)", "2-Piece (Shirt + Dupatta/Trouser)", "3-Piece (Full Suit)", "Any"]
        )

    with col2:
        color = st.text_input("Preferred Color(s)", placeholder="e.g., Emerald Green, Pastel Pink, Black & Gold")
        max_price = st.number_input("Maximum Budget (PKR)", min_value=1000, max_value=150000, value=10000, step=1000)
        specific_brands = st.multiselect(
            "Preferred Brands (Optional)",
            ["Sapphire", "Khaadi", "Nishat Linen", "Gul Ahmed", "Sana Safinaz", "JUNAID JAMSHED (J.)", "Maria.B", "Limelight", "Beechtree", "Bareeze"],
            default=[]
        )

    submit_button = st.form_submit_button("Find Outfits 🛍️")

# Process Request
if submit_button:
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar or set GEMINI_API_KEY environment variable.")
    else:
        try:
            # Initialize Gemini Client
            client = genai.Client(api_key=api_key)

            brands_str = ", ".join(specific_brands) if specific_brands else "popular Pakistani brands (e.g., Sapphire, Khaadi, Nishat Linen, Gul Ahmed, Limelight, Maria.B)"
            
            prompt = f"""
You are a top Pakistani personal fashion stylist and shopping assistant.
Find available outfits matching these exact specifications:

- Category/Style: {category}
- Fabric: {fabric}
- Suit Type: {pieces}
- Preferred Color: {color if color else "Any"}
- Maximum Budget: PKR {max_price}
- Preferred Brands: {brands_str}

REQUIREMENTS:
1. Recommend 4 to 6 specific outfit options currently available from top official Pakistani clothing brand websites.
2. For each recommendation, provide:
   - **Outfit Name / Title**
   - **Brand Name**
   - **Price in PKR**
   - **Fabric & Collection Details**
   - **Direct Purchase Link:** You MUST search for and provide the exact clickable direct web link (`[Buy Here](URL)`) to the outfit on the official brand website.
3. Keep the layout structured using Markdown callouts or clean headers.
4. Ensure prices stay strict within the PKR {max_price} budget.
"""

            with st.spinner("Searching official Pakistani brand stores for matching outfits..."):
                # Call Gemini Flash with Google Search Grounding enabled
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.3
                    )
                )

            st.success("Here are your matching outfit recommendations:")
            st.markdown("---")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
