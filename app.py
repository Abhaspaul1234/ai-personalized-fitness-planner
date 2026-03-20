from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from PIL import Image
import google.generativeai as genai


st.set_page_config(page_title="AI Workout & Diet Planner", layout="wide")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    st.warning("GOOGLE_API_KEY not found in environment. Add it to your .env file.")

def get_gemini_response(prompt: str) -> str:
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY not configured."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return getattr(response, "text", str(response))
    except Exception as e:
        return f"Error generating response: {str(e)}"

if "profile" not in st.session_state:
    st.session_state["profile"] = {
        "age": 25,
        "gender": "Male",
        "goals": "Lose 10 pounds in 3 months\nImprove cardiovascular health",
        "conditions": "None",
        "routines": "30-minute walk 3x/week",
        "preferences": "Vegetarian\nLow carb",
        "restrictions": "No dairy\nNo nuts",
    }

with st.sidebar:
    st.subheader("Your Health Profile")

    age = st.number_input(
        "Age",
        min_value=5,
        max_value=100,
        value=st.session_state["profile"].get("age", 25),
    )

    genders = ["Male", "Female", "Other"]
    current_gender = st.session_state["profile"].get("gender", "Male")
    gender_index = genders.index(current_gender) if current_gender in genders else 0

    gender = st.selectbox("Gender", genders, index=gender_index)

    goals = st.text_area("Health Goals", value=st.session_state["profile"]["goals"])
    conditions = st.text_area("Medical Conditions", value=st.session_state["profile"]["conditions"])
    routines = st.text_area("Current Routines", value=st.session_state["profile"]["routines"])
    preferences = st.text_area("Food Preferences", value=st.session_state["profile"]["preferences"])
    restrictions = st.text_area("Dietary Restrictions", value=st.session_state["profile"]["restrictions"])

    if st.button("Update Profile"):
        st.session_state["profile"] = {
            "age": age,
            "gender": gender,
            "goals": goals,
            "conditions": conditions,
            "routines": routines,
            "preferences": preferences,
            "restrictions": restrictions,
        }
        st.success("Profile Updated ✅")

st.title("AI Personalized Workout & Diet Planner")

tab1, tab2, tab3 = st.tabs(["Meal Planning", "Food Analysis", "Health Insights"])

# TAB 1 — MEAL PLANNING

with tab1:
    st.subheader("Personalized Meal Planning")

    col1, col2 = st.columns(2)

    with col1:
        user_input = st.text_area(
            "Describe specific requirements",
            placeholder="e.g., 1800 kcal/day, high protein, quick meals",
        )
        generate_plan = st.button("Create Personalized Meal Plan")

    with col2:
        st.write("### Your Health Profile")
        st.json(st.session_state["profile"])

    if generate_plan:
        profile = st.session_state["profile"]

        with st.spinner("Creating your personalized meal plan..."):
            prompt = f"""
Create a personalized 7-day meal plan.

User Details:
Age: {profile.get('age')}
Gender: {profile.get('gender')}

Health Goals: {profile.get('goals')}
Medical Conditions: {profile.get('conditions')}
Current Routines: {profile.get('routines')}
Food Preferences: {profile.get('preferences')}
Dietary Restrictions: {profile.get('restrictions')}

Additional Requirements: {user_input if user_input else 'None'}

IMPORTANT:
- Adjust calories and protein based on age and gender
- Ensure micronutrient sufficiency
- Make the plan practical and affordable

Provide:
1) 7-day meal plan
2) Daily calories & macros
3) Why these meals were chosen
4) Shopping list
5) Meal prep tips
"""
            response = get_gemini_response(prompt)

            st.subheader("Your Personalized Meal Plan")
            st.markdown(response)

            st.download_button(
                "Download Meal Plan",
                data=response,
                file_name="meal_plan.txt",
                mime="text/plain",
            )

# TAB 2 — FOOD ANALYSIS

with tab2:
    st.subheader("Food Analysis")
    st.info("📸 Upload an image and enter the food name for the best demo result.")

    uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
    food_name = st.text_input(
        "Enter food name",
        placeholder="e.g., pizza, burger, salad, rice bowl",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Analyze Food"):
        if uploaded_file is None:
            st.warning("⚠️ Please upload a food image first.")
        elif not food_name.strip():
            st.warning("⚠️ Please enter the food name for better accuracy.")
        else:
            with st.spinner("Analyzing food..."):
                prompt = f"""
You are a nutrition expert.

Analyze this food: {food_name}

Provide:
- Calories
- Macronutrients
- Health benefits
- Portion advice
- One short caution if needed

Keep the answer clear and practical.
"""
                result = get_gemini_response(prompt)

                st.subheader("Food Analysis Result")
                st.success("Analysis Complete ✅")
                st.write(f"🍽️ Food Entered: **{food_name}**")
                st.markdown(result)

# TAB 3 — HEALTH INSIGHTS

with tab3:
    st.subheader("Health & Nutrition Insights")

    health_query = st.text_input("Ask your health question")

    if st.button("Get Expert Insights"):
        if not health_query.strip():
            st.warning("Please type a health question first.")
        else:
            profile = st.session_state["profile"]

            prompt = f"""
Answer the following health question:

{health_query}

User Profile:
Age: {profile.get('age')}
Gender: {profile.get('gender')}
Goals: {profile.get('goals')}
Medical Conditions: {profile.get('conditions')}
Current Routines: {profile.get('routines')}
Food Preferences: {profile.get('preferences')}
Dietary Restrictions: {profile.get('restrictions')}

Provide:
- Simple science explanation
- Practical advice
- Precautions
"""
            response = get_gemini_response(prompt)

            st.subheader("Expert Answer")
            st.markdown(response)