import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(
    page_title="AI Indian Meal Prep Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Injection (Using CSS snippets inspired by UI libraries like Tailwind/Flowbite)
st.markdown("""
<style>
    /* Global font & background tweaks */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Custom Header Banner */
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        padding: 1.75rem 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        font-weight: 800 !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Styled metric cards */
    .metric-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        border-radius: 0.75rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 3. Retrieve API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Please configure your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("Indian_Food_Nutrition_Processed.csv")

try:
    df = load_data()
except Exception as e:
    st.error("Could not load dataset file `Indian_Food_Nutrition_Processed.csv`. Please ensure it is in the repository.")
    df = pd.DataFrame()

# 4. Header Section
st.markdown("""
<div class="main-header">
    <h1>🥗 AI Indian Meal Prep Planner</h1>
    <p style="margin:0; opacity: 0.9; font-size: 0.95rem;">
        Generate data-backed, nutrition-balanced Indian meal prep plans in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# 5. Sidebar for Quick Stats / Quick Settings
with st.sidebar:
    st.header("⚙️ Preferences Summary")
    st.info("💡 **Tip**: Higher calorie targets work best with 5–7 day plans for better ingredient distribution.")
    
    if not df.empty:
        st.metric(label="Total Recipes in Database", value=f"{len(df):,}")
    
    st.divider()
    st.caption("Powered by Google Gemini 1.5 & Pandas")

# 6. User Inputs (Grid Layout)
st.subheader("🎯 Step 1: Define Your Goals")

input_container = st.container(border=True)
with input_container:
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        diet_type = st.selectbox(
            "Dietary Preference",
            ["Vegetarian", "Non-Vegetarian", "Vegan", "Eggetarian", "Jain"]
        )
        target_calories = st.slider(
            "Target Daily Calories (kcal)",
            min_value=1200,
            max_value=3500,
            value=2000,
            step=50
        )

    with col2:
        days = st.select_slider(
            "Plan Duration (Days)",
            options=[1, 2, 3, 5, 7],
            value=3
        )
        allergies = st.text_input(
            "Allergies / Restrictions",
            placeholder="e.g., Low Sodium, Dairy-free, No Peanuts"
        )

    user_notes = st.text_area(
        "Specific Meal Preferences",
        placeholder="e.g., Quick breakfast (<15 mins), high-protein lunches, include oats or paneer...",
        height=80
    )

# 7. Meal Plan Generation
st.write("")
if st.button("✨ Generate AI Meal Prep Plan"):
    if df.empty:
        st.error("Dataset is empty. Cannot supply context to AI.")
    else:
        with st.spinner("Analyzing dataset & crafting your personalized meal plan..."):
            # Provide sample context from dataset
            data_summary = df.head(80).to_csv(index=False)

            prompt = f"""
            You are an expert Indian nutritionist and meal planning assistant.
            Use the following dataset context to select recipes and ingredients where relevant:

            DATASET CONTEXT SAMPLE:
            {data_summary}

            USER REQUIREMENTS:
            - Diet Type: {diet_type}
            - Daily Calorie Target: {target_calories} kcal
            - Duration: {days} days
            - Dietary Restrictions/Allergies: {allergies if allergies else 'None'}
            - Specific Requests: {user_notes if user_notes else 'None'}

            INSTRUCTIONS:
            Format your output cleanly using Markdown with clear headings.
            Ask the user what items they have in their inventory. Ask the user whether they are meal prepping for a sinngle meal, a single day, a week and so on.
            Ask the user how much time they have on hand to make a meal and crosscheck with the database and suggest relevant meals.
            Provide:
            1. Meal Breakdown (Breakfast, Lunch, Evening Snack, Dinner)
            2. Calories and Macros (Protein, Carbs, Fats) per meal
            3. Estimated Prep Time & Brief Prep Tips for batch cooking.
            Also scour the internet and provide links to yt channels/recipe websites for the specific recipe suggested.
            """

            try:
                response = model.generate_content(prompt)
                
                # Output Results in a stylized card container
                st.success("✅ Plan generated successfully!")
                
                output_box = st.container(border=True)
                with output_box:
                    st.markdown("### 📋 Your Customized Meal Prep Plan")
                    st.markdown(response.text)
                    
            except Exception as err:
                st.error(f"Failed to communicate with AI: {err}")