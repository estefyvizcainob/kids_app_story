import os
import base64
import requests
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for Azure OpenAI
API_KEY = os.getenv("API_KEY")
ENDPOINT = "https://GENAISUSANA.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"
HEADERS = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Validate API Key and Endpoint
if not API_KEY or not ENDPOINT:
    st.error("API Key or Endpoint is missing. Please check your configuration.")

# Function to set background image
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{data}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(bg_img, unsafe_allow_html=True)

# Function to display floating stars animation
def show_stars():
    stars_css = """
    <style>
    @keyframes float {
        0% { transform: translateY(120vh) scale(0.5); opacity: 0; }
        50% { opacity: 1; }
        100% { transform: translateY(-10vh) scale(1.5); opacity: 0; }
    }
    .star {
        position: fixed;
        width: 10px;
        height: 10px;
        background: #FFD700;
        border-radius: 50%;
        box-shadow: 0 0 8px #FFD700;
        animation: float 10s linear infinite;
        z-index: 10;
    }
    </style>
    <div>
    """ + ''.join(
        f'<div class="star" style="left: {(i * 13) % 100}vw; top: {(i * 7) % 100}vh; animation-delay: {(i % 10) * 0.5}s;"></div>'
        for i in range(50)
    ) + "</div>"
    st.markdown(stars_css, unsafe_allow_html=True)

# Function to fetch story from Azure OpenAI
def get_story_from_azure(learning_goal, animal, user_choice=""):
    payload = {
        "messages": [
            {"role": "system", "content": """
You are a children's story writer. Create an engaging, educational story for kids aged 3-5.
1. The story has 3 parts.
2. Include two decision points where the child selects:
   - Option A: Correct choice that progresses the story.
   - Option B: A gentle consequence, explaining why it is not the best choice.
3. Teach two animal facts in Part 1.
4. Pause after each decision point, waiting for input.
5. The story should reinforce learning and have a happy ending.
""" },
            {"role": "user", "content": f"The lesson is about {learning_goal}. The story features a {animal}. {user_choice}"}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800,
    }
    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No content returned")
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except requests.RequestException as e:
        st.error(f"Error fetching story: {e}")
    return "Unable to fetch the story due to an error."

# Function to parse choices from the story
def parse_story_with_choices(content):
    story_text = ""
    options = {}
    lines = content.split("\n")
    for line in lines:
        if "Option A:" in line:
            options["Option A"] = line.split("Option A:")[1].strip()
        elif "Option B:" in line:
            options["Option B"] = line.split("Option B:")[1].strip()
        else:
            story_text += line + "\n"
    return story_text.strip(), options

# Function to explain Option B choice morally
def get_moral_explanation(goal, animal):
    payload = {
        "messages": [
            {"role": "system", "content": """
You are an educational assistant for children aged 3-5. Explain moral lessons gently and clearly.
When a child makes an incorrect choice (Option B), explain why it is not the best choice in a kind and moral way.
The explanation should relate to the story, teaching a positive value or lesson.
""" },
            {"role": "user", "content": f"The story features a {animal}, and the goal is to teach {goal}. Provide a short, concise moral explanation for why Option B is not the best choice."}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 100,
    }
    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        st.error(f"Error generating moral explanation: {e}")
    return "Unable to fetch moral explanation."

# Set Background Image
set_bg_image("lit_lum.png")

# Initialize session state
if "progress" not in st.session_state:
    st.session_state["progress"] = 0
    st.session_state["story"] = []
    st.session_state["choices"] = {}
    st.session_state["goal"] = ""
    st.session_state["animal"] = ""

# Start of App
if st.session_state["progress"] == 0:

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    learning_goal = st.text_input("Enter a learning goal (e.g., kindness, teamwork):")
    animal = st.selectbox("Choose an animal:", ["Lion", "Elephant", "Penguin", "Dolphin"])
    
    if st.button("Start Story"):
        st.session_state["goal"] = learning_goal
        st.session_state["animal"] = animal
        response = get_story_from_azure(learning_goal, animal)
        if "Error" in response:
            st.warning("There was an issue fetching the story. Please try again.")
        else:
            story, choices = parse_story_with_choices(response)
            st.session_state["story"] = [story]
            st.session_state["choices"] = choices
            st.session_state["progress"] = 1
            st.rerun()

# Story Progression
elif 0 < st.session_state["progress"] < 4:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <style>
        .story-container {{
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 15px;
            margin: 20px auto;
            font-size: 20px;
            line-height: 1.6;
            color: #333;
            width: 80%;
            text-align: justify;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        }}
        </style>
            {st.session_state['story'][-1]}
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    if st.session_state["choices"]:
        with col1:
            if st.button(f"Option A: {st.session_state['choices']['Option A']}", key="OptionA"):
                response = get_story_from_azure(
                    st.session_state["goal"], 
                    st.session_state["animal"], 
                    "Child chose Option A"
                )
                story, choices = parse_story_with_choices(response)
                st.session_state["story"].append(story)
                st.session_state["choices"] = choices
                st.session_state["progress"] += 1
                st.rerun()
        with col2:
            if st.button(f"Option B: {st.session_state['choices']['Option B']}", key="OptionB"):
                moral_explanation = get_moral_explanation(st.session_state["goal"], st.session_state["animal"])
                st.markdown(
                    f"""
                    <div style='background-color:rgba(255, 99, 71, 0.85); color:#FFF; padding:15px; border-radius:10px; margin:20px auto; text-align:center;'>
                        That wasn't the best choice. Here's something to learn:<br>{moral_explanation}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# End of Story
if st.session_state["progress"] == 4:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; font-size:36px; font-weight:bold; color:beige;'>Congrats!!! 🎉 You finished the adventure! Thank you for playing!</div>", unsafe_allow_html=True)
    show_stars()
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()



