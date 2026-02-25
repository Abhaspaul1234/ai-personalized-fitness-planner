from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.warning("GOOGLE_API_KEY not found in environment. Set it in a .env file.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

if 'health_profile' not in st.session_state:
    st.session_state['health_profile'] = {
        'age': 25,
        'gender': 'Male',
        'goals': 'Lose 10 pounds in 3 months\nImprove cardiovascular health',
        'conditions': 'None',
        'routines': '30-minute walk 3x/week',
        'preferences': 'Vegetarian\nLow carb',
        'restrictions': 'No dairy\nNo nuts'
    }

def get_gemini_response(prompt: str):
    if not GOOGLE_API_KEY:
        return "Error: API key not configured."

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return getattr(response, "text", str(response))
    except Exception as e:
        return f"Error generating response: {str(e)}"


def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return {
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }
    return None

st.set_page_config(page_title="AI Workout & Diet Planner", layout="wide")
st.title("AI Personalized Workout & Diet Planner")

with st.sidebar:
    st.subheader("Your Health Profile")

    age = st.number_input("Age", 5, 100,
                          value=st.session_state['health_profile'].get('age', 25))

    gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                          index=["Male", "Female", "Other"].index(
                              st.session_state['health_profile'].get('gender', 'Male')))

    health_goals = st.text_area("Health Goals",
                                value=st.session_state['health_profile']['goals'])

    medical_conditions = st.text_area("Medical Conditions",
                                      value=st.session_state['health_profile']['conditions'])

    fitness_routines = st.text_area("Current Routines",
                                    value=st.session_state['health_profile']['routines'])

    food_preferences = st.text_area("Food Preferences",
                                    value=st.session_state['health_profile']['preferences'])

    restrictions = st.text_area("Dietary Restrictions",
                                value=st.session_state['health_profile']['restrictions'])

    if st.button("Update Profile"):
        st.session_state['health_profile'] = {
            'age': age,
            'gender': gender,
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preferences,
            'restrictions': restrictions
        }
        st.success("Profile Updated ✅")

tab1, tab2, tab3 = st.tabs(["Meal Planning", "Food Analysis", "Health Insights"])


# TAB 1 — MEAL PLANNING

with tab1:
    st.subheader("Personalized Meal Planning")

    col1, col2 = st.columns(2)

    with col1:
        user_input = st.text_area("Describe specific requirements",
                                  placeholder="e.g., 1500 kcal/day, high protein")

        generate_plan = st.button("Create Personalized Meal Plan")

    with col2:
        st.write("### Your Health Profile")
        st.json(st.session_state['health_profile'])

    if generate_plan:

        profile = st.session_state['health_profile']

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

            st.download_button("Download Meal Plan",
                               data=response,
                               file_name="meal_plan.txt",
                               mime="text/plain")


# TAB 2 — FOOD ANALYSIS

with tab2:
    st.subheader("Food Analysis")

    uploaded_file = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Analyze Food"):
        if uploaded_file:

            prompt = """
You are a nutrition expert.

Analyze the food and provide:
- Calories
- Macronutrients
- Health benefits
- Portion advice
"""

            response = get_gemini_response(prompt)

            st.subheader("Food Analysis Result")
            st.markdown(response)


#TAB 3 — HEALTH INSIGHTS

with tab3:
    st.subheader("Health & Nutrition Insights")

    health_query = st.text_input("Ask your health question")

    if st.button("Get Expert Insights"):

        profile = st.session_state['health_profile']

        prompt = f"""
Answer the following health question:

{health_query}

User Profile:
Age: {profile.get('age')}
Gender: {profile.get('gender')}
Goals: {profile.get('goals')}
Medical Conditions: {profile.get('conditions')}

Provide:
- Simple science explanation
- Practical advice
- Precautions
"""

        response = get_gemini_response(prompt)

        st.subheader("Expert Answer")
        st.markdown(response)