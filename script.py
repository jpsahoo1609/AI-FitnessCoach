import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time
from supabase import create_client, Client

# Initialize Supabase Client
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test Supabase connection on startup
@st.cache_resource
def test_supabase_connection():
    try:
        response = supabase.table("users").select("count").execute()
        return True
    except Exception as e:
        st.error(f"Supabase connection error: {str(e)}")
        return False

# ==================== UTILITY FUNCTIONS ====================

def calculate_bmi(weight_kg, height_cm):
    bmi = weight_kg / (height_cm / 100) ** 2
    if bmi < 18.5: category = "Underweight"
    elif bmi < 25: category = "Normal"
    elif bmi < 30: category = "Overweight"
    else: category = "Obese"
    return round(bmi, 1), category

def calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level):
    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    multipliers = {"Sedentary / Mostly Sitting": 1.2, "Light (1-3 days/week)": 1.375, "Moderate (3-5 days/week)": 1.55, "Active (6-7 days/week)": 1.725}
    return int(bmr * multipliers[activity_level])

def normalize_goal(goal):
    goals = {"Weight Loss": "weight_loss", "Fat Loss": "fat_loss", "Muscle Gain": "muscle_gain", "Maintenance": "maintenance"}
    return goals.get(goal, "maintenance")

def calculate_target_weight(goal, current_weight):
    if goal in ["weight_loss", "fat_loss"]:
        return round(current_weight * 0.9, 1)
    elif goal == "muscle_gain":
        return round(current_weight * 1.1, 1)
    return current_weight

def calculate_body_fat(weight_kg, height_cm, age, gender):
    bmi = weight_kg / (height_cm / 100) ** 2
    if gender == "Male":
        fat_percent = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        fat_percent = (1.20 * bmi) + (0.23 * age) - 5.4
    return round(max(fat_percent, 10), 1)

def calculate_target_fat(goal, current_fat):
    if goal == "fat_loss":
        return round(current_fat - 5, 1)
    return round(current_fat, 1)

# ==================== SUPABASE DATABASE FUNCTIONS ====================

def save_user_profile(user_id, profile):
    try:
        supabase.table("users").insert({
            "user_id": user_id,
            "name": profile["name"],
            "age": int(profile["age"]),
            "weight_kg": float(profile["weight_kg"]),
            "height_cm": float(profile["height_cm"]),
            "gender": profile["gender"],
            "activity_level": profile["activity_level"],
            "goal": profile["goal"],
            "dietary_preference": profile["dietary_preference"]
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error saving profile: {str(e)}")
        return False

def load_user_profile(user_id):
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        return None

def save_weight(user_id, weight):
    try:
        supabase.table("weights").insert({
            "user_id": user_id,
            "weight": float(weight),
            "timestamp": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error saving weight: {str(e)}")
        return False

def get_latest_weight(user_id):
    try:
        response = supabase.table("weights").select("weight").eq("user_id", user_id).order("timestamp", desc=True).limit(1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["weight"]
        profile = load_user_profile(user_id)
        if profile:
            return profile.get("weight_kg", 70.0)
        return 70.0
    except Exception as e:
        st.error(f"Error getting latest weight: {str(e)}")
        return 70.0

def get_all_weights(user_id):
    try:
        response = supabase.table("weights").select("*").eq("user_id", user_id).order("timestamp", desc=False).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error getting all weights: {str(e)}")
        return []

def save_workout(user_id):
    try:
        supabase.table("workouts").insert({
            "user_id": user_id,
            "date": datetime.now().date().isoformat(),
            "timestamp": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error saving workout: {str(e)}")
        return False

def get_workouts(user_id):
    try:
        response = supabase.table("workouts").select("*").eq("user_id", user_id).order("timestamp", desc=False).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error getting workouts: {str(e)}")
        return []

def get_progress_summary(user_id):
    weights = get_all_weights(user_id)
    if len(weights) > 1:
        return f"Started: {weights[0]['weight']}kg, Now: {weights[-1]['weight']}kg"
    return "Just started"

def calculate_streak(workouts):
    if not workouts:
        return 0
    today = datetime.now().date()
    workout_dates = set(datetime.fromisoformat(w['date']).date() for w in workouts)
    streak = 0
    check_date = today
    while check_date in workout_dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak

def get_consistency(filter_period, workouts):
    today = datetime.now().date()
    if filter_period == "Week":
        total_days = 7
        start_date = today - timedelta(days=7)
    elif filter_period == "Month":
        total_days = 30
        start_date = today - timedelta(days=30)
    else:
        total_days = 365
        start_date = today - timedelta(days=365)
    filtered = [w for w in workouts if datetime.fromisoformat(w['date']).date() >= start_date]
    return round((len(filtered) / total_days) * 100, 2)

# ==================== OPENAI FITNESS COACH AGENT ====================

class FitnessCoachAgent:
    def __init__(self, user_id, name, age, weight_kg, height_cm, gender, activity_level, goal, dietary_preference):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        self.conversation_history = []
        self.user_id = user_id
        self.current_weight = weight_kg
        self.name = name
        self.age = age
        self.height_cm = height_cm
        self.gender = gender
        self.goal = goal
        self.dietary_preference = dietary_preference
        
        bmi, bmi_cat = calculate_bmi(weight_kg, height_cm)
        daily_calories = calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level)
        normalized_goal = normalize_goal(goal)
        
        if normalized_goal in ["weight_loss", "fat_loss"]:
            target_calories = daily_calories - 500
        elif normalized_goal == "muscle_gain":
            target_calories = daily_calories + 300
        else:
            target_calories = daily_calories
        
        progress = get_progress_summary(user_id)
        self.system_prompt = f"""Fitness Coach. {name}, Goal: {goal}, {dietary_preference}, {target_calories}kcal/day. {progress}. SHORT, CONCISE. Max 100 tokens. Indian food."""
        self.bmi = bmi
        self.bmi_category = bmi_cat
        self.target_calories = target_calories
    
    def chat(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": self.system_prompt}, *self.conversation_history],
            max_tokens=250
        )
        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply
    
    def update_weight(self, new_weight):
        self.current_weight = new_weight
        save_weight(self.user_id, new_weight)

# ==================== UI COMPONENTS ====================

def display_progress_table(workouts_done, weight_loss, fat_loss):
    html_table = f"""
    <style>
    .progress-wrapper {{
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 20px auto !important;
        padding: 0 !important;
    }}
    .progress-container {{
        width: 100% !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }}
    .progress-table {{
        width: 100% !important;
        background: #2d1b2e !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0 !important;
        color: #ffffff !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
        overflow: hidden !important;
    }}
    .progress-table table {{
        width: 100% !important;
        border-collapse: collapse !important;
        border-spacing: 0 !important;
    }}
    .progress-table th {{
        background: linear-gradient(135deg, #4a7c9e 0%, #3d6a8f 100%) !important;
        padding: 18px 25px !important;
        text-align: left !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border: none !important;
        border-bottom: 3px solid #2a4a6f !important;
    }}
    .progress-table td {{
        padding: 18px 25px !important;
        border: none !important;
        text-align: left !important;
        font-size: 15px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    .progress-table tr:last-child td {{
        border-bottom: none !important;
    }}
    .progress-table tbody tr:nth-child(1) {{
        background-color: rgba(107, 168, 196, 0.12) !important;
    }}
    .progress-table tbody tr:nth-child(1) td:last-child {{
        color: #87ceeb !important;
        font-weight: bold !important;
    }}
    .progress-table tbody tr:nth-child(2) {{
        background-color: rgba(255, 107, 107, 0.12) !important;
    }}
    .progress-table tbody tr:nth-child(2) td:last-child {{
        color: #ff6b6b !important;
        font-weight: bold !important;
    }}
    .progress-table tbody tr:nth-child(3) {{
        background-color: rgba(81, 207, 102, 0.12) !important;
    }}
    .progress-table tbody tr:nth-child(3) td:last-child {{
        color: #51cf66 !important;
        font-weight: bold !important;
    }}
    </style>
    <div class="progress-wrapper">
        <div class="progress-container">
            <div class="progress-table">
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Workouts Completed</td>
                        <td>{workouts_done} days</td>
                    </tr>
                    <tr>
                        <td>Weight Lost</td>
                        <td>{weight_loss} kg</td>
                    </tr>
                    <tr>
                        <td>Fat Lost %</td>
                        <td>{fat_loss} %</td>
                    </tr>
                </tbody>
            </table>
            </div>
        </div>
    </div>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# ==================== MAIN APP ====================

st.set_page_config(page_title="Your AI Fitness Coach", page_icon="💪", layout="wide")
st.markdown('''<style>
[data-testid="stAppViewContainer"]{background: linear-gradient(135deg, #2d1b2e 0%, #5a1a1a 50%, #1a1a1a 100%);}
[data-testid="stSidebar"]{background: linear-gradient(135deg, #1a0f10 0%, #3d1515 100%);}
h1, h2, h3, h4, h5, h6 {color: #ffffff !important;}
p, span, label {color: #ffffff !important;}
[data-testid="stMarkdownContainer"] {color: #ffffff !important;}
[data-testid="stMarkdownContainer"] p {color: #ffffff !important;}
[data-testid="stMarkdownContainer"] strong {color: #ffffff !important;}
[data-testid="stMetricLabel"] {color: #ffffff !important;}
[data-testid="stMetricValue"] {color: #ffffff !important;}
.stRadio label {color: #ffffff !important;}
.stTextInput label {color: #ffffff !important;}
.stNumberInput label {color: #ffffff !important;}
.stSelectbox label {color: #ffffff !important;}
[data-testid="stWidgetLabel"] {color: #ffffff !important;}
.stButton button {
    background-color: #1a1a2e !important;
    color: #ffffff !important;
    border: 1px solid #2a2a3e !important;
}
.stButton button:hover {
    background-color: #0f0f1a !important;
    color: #ffffff !important;
    border: 1px solid #3a3a4e !important;
}
.stButton button:active, .stButton button:focus {
    background-color: #0a0a14 !important;
    color: #ffffff !important;
}
</style>''', unsafe_allow_html=True)
st.title("Your AI Fitness Coach")

# Initialize session state
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "coach" not in st.session_state: st.session_state.coach = None
if "user_id" not in st.session_state: st.session_state.user_id = None
if "is_new_user" not in st.session_state: st.session_state.is_new_user = False
if "greeted" not in st.session_state: st.session_state.greeted = False
if "active_page" not in st.session_state: st.session_state.active_page = None
if "filter_period" not in st.session_state: st.session_state.filter_period = "Week"

# Auto-login if session exists
if st.session_state.user_id and st.session_state.logged_in and st.session_state.coach:
    pass
elif st.session_state.user_id and not st.session_state.coach:
    profile = load_user_profile(st.session_state.user_id)
    if profile:
        latest_weight = get_latest_weight(st.session_state.user_id)
        st.session_state.coach = FitnessCoachAgent(user_id=st.session_state.user_id, name=profile['name'], age=profile['age'],
            weight_kg=latest_weight, height_cm=profile['height_cm'], gender=profile['gender'],
            activity_level=profile['activity_level'], goal=profile['goal'], dietary_preference=profile['dietary_preference'])
        st.session_state.logged_in = True

# LOGIN / CREATE PROFILE
if not st.session_state.logged_in:
    st.subheader("Welcome")
    mode = st.radio("Select:", ["Login", "Create Profile"], horizontal=True)
    
    if mode == "Login":
        user_id = st.text_input("User ID")
        if st.button("Login", use_container_width=True):
            profile = load_user_profile(user_id)
            if profile:
                latest_weight = get_latest_weight(user_id)
                st.session_state.user_id = user_id
                st.session_state.coach = FitnessCoachAgent(user_id=user_id, name=profile['name'], age=profile['age'],
                    weight_kg=latest_weight, height_cm=profile['height_cm'], gender=profile['gender'],
                    activity_level=profile['activity_level'], goal=profile['goal'], dietary_preference=profile['dietary_preference'])
                st.session_state.logged_in = True
                st.session_state.is_new_user = False
                st.session_state.greeted = False
                st.rerun()
            else:
                st.error("User not found")
    else:
        st.subheader("Create Profile")
        with st.form("profile_form"):
            user_id = st.text_input("User ID")
            name = st.text_input("Name")
            age = st.number_input("Age", 10, 100, 25)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            height = st.number_input("Height (cm)", 100.0, 250.0, 170.0)
            gender = st.selectbox("Gender", ["Male", "Female"])
            activity = st.selectbox("Activity", ["Sedentary / Mostly Sitting", "Light (1-3 days/week)", "Moderate (3-5 days/week)", "Active (6-7 days/week)"])
            goal = st.selectbox("Goal", ["Weight Loss", "Fat Loss", "Muscle Gain", "Maintenance"])
            diet = st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            submitted = st.form_submit_button("Create", use_container_width=True)
        
        if submitted and user_id and name:
            with st.spinner("🔄 Creating profile..."):
                time.sleep(1.5)
                profile = {"user_id": user_id, "name": name, "age": age, "weight_kg": weight, "height_cm": height, "gender": gender, "activity_level": activity, "goal": goal, "dietary_preference": diet}
                if save_user_profile(user_id, profile):
                    save_weight(user_id, weight)
                    st.session_state.user_id = user_id
                    st.session_state.coach = FitnessCoachAgent(user_id=user_id, name=name, age=age, weight_kg=weight, height_cm=height, gender=gender, activity_level=activity, goal=goal, dietary_preference=diet)
                    st.session_state.logged_in = True
                    st.session_state.is_new_user = True
                    st.session_state.greeted = False
                    st.success(f"✅ Profile created! Welcome {name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create profile. Please try again.")

# MAIN DASHBOARD
else:
    coach = st.session_state.coach
    profile = load_user_profile(st.session_state.user_id)
    target_weight = calculate_target_weight(normalize_goal(profile['goal']), coach.current_weight)
    current_fat = calculate_body_fat(coach.current_weight, coach.height_cm, coach.age, coach.gender)
    target_fat = calculate_target_fat(normalize_goal(profile['goal']), current_fat)
    goal_norm = normalize_goal(profile['goal'])
    all_weights = get_all_weights(st.session_state.user_id)
    all_workouts = get_workouts(st.session_state.user_id)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Name", profile['name'][:12])
    col2.metric("BMI", f"{coach.bmi}")
    col3.metric("Daily Calories Hit", f"{coach.target_calories}kcal")
    col4.metric("Current Weight", f"{coach.current_weight}kg")
    col5.metric("Target Weight", f"{target_weight}kg")
    
    st.divider()
    
    # SIDEBAR
    with st.sidebar:
        st.write("### Quick Tabs")
        if st.button("Fat % Tracker", use_container_width=True, key="fat_btn"):
            if st.session_state.active_page == "fat":
                st.session_state.active_page = None
            else:
                st.session_state.active_page = "fat"
            st.rerun()
        
        if st.button("Weight Management Tracker", use_container_width=True, key="weight_btn"):
            if st.session_state.active_page == "weight":
                st.session_state.active_page = None
            else:
                st.session_state.active_page = "weight"
            st.rerun()
        
        if st.button("Muscle Gain Tracker", use_container_width=True, key="muscle_btn"):
            if st.session_state.active_page == "muscle":
                st.session_state.active_page = None
            else:
                st.session_state.active_page = "muscle"
            st.rerun()
        
        if st.button("My Progress", use_container_width=True, key="progress_btn"):
            if st.session_state.active_page == "progress":
                st.session_state.active_page = None
            else:
                st.session_state.active_page = "progress"
            st.rerun()
        
        st.divider()
        st.write("### Your Goal")
        st.write(f"**{profile['goal']}**")
        
        st.divider()
        st.write("### Update Weight")
        new_weight = st.number_input("Weight (kg)", 30.0, 200.0, coach.current_weight, key="weight")
        if st.button("Save", use_container_width=True, key="save_weight"):
            if new_weight != coach.current_weight:
                with st.spinner("⏳ Updating weight..."):
                    time.sleep(1.5)
                    save_weight(st.session_state.user_id, new_weight)
                    coach.current_weight = new_weight
                
                st.success("✅ Congratulations! Your progress is amazing, you're doing really well. Keep going!")
                time.sleep(2)
                st.rerun()
            else:
                st.info("Weight unchanged")
    
    # STATS SECTION
    st.write("### Stats")
    st.session_state.filter_period = st.radio("Filter by:", ["Week", "Month", "Year"], horizontal=True, key="filter_radio")
    
    today = datetime.now().date()
    if st.session_state.filter_period == "Week":
        start_date = today - timedelta(days=7)
        days_label = "Days/Week"
        consistency_label = "Week Consistency"
        total_days = 7
    elif st.session_state.filter_period == "Month":
        start_date = today - timedelta(days=30)
        days_label = "Days/Month"
        consistency_label = "Month Consistency"
        total_days = 30
    else:
        start_date = today - timedelta(days=365)
        days_label = "Days/Year"
        consistency_label = "Year Consistency"
        total_days = 365
    
    filtered_workouts = [w for w in all_workouts if datetime.fromisoformat(w['date']).date() >= start_date]
    workouts_count = len(filtered_workouts)
    consistency = get_consistency(st.session_state.filter_period, all_workouts)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Workouts", workouts_count)
    col2.metric("Max Streak", f"{calculate_streak(all_workouts)} days")
    col3.metric(days_label, f"{workouts_count}/{total_days}")
    col4.metric(consistency_label, f"{consistency}%")
    
    st.divider()
    
    # QUICK TABS CONTENT
    if st.session_state.active_page == "progress":
        st.write("### Your Progress")
        
        workouts_done = len(all_workouts)
        weight_loss = 0.0
        fat_loss = 0.0
        
        if len(all_weights) > 1:
            weight_loss = round(all_weights[0]['weight'] - all_weights[-1]['weight'], 1)
            initial_fat = calculate_body_fat(all_weights[0]['weight'], coach.height_cm, coach.age, coach.gender)
            current_fat_calc = calculate_body_fat(all_weights[-1]['weight'], coach.height_cm, coach.age, coach.gender)
            fat_loss = round(initial_fat - current_fat_calc, 1)
        
        col_empty1, col_table, col_empty2 = st.columns([1, 2, 1])
        with col_table:
            display_progress_table(workouts_done, weight_loss, fat_loss)
    
    elif st.session_state.active_page == "fat":
        with st.container(border=True):
            st.write("### Fat % Tracker")
            st.write("Track your body fat percentage progress")
            st.write(f"**Current Fat: {current_fat}%** | **Target Fat: {target_fat}%**")
            
            if len(all_weights) > 1:
                dates = [datetime.fromisoformat(w['timestamp']).strftime('%m-%d') for w in all_weights]
                fat_percents = [calculate_body_fat(w['weight'], coach.height_cm, coach.age, coach.gender) for w in all_weights]
                
                fig, ax = plt.subplots(figsize=(16, 7))
                ax.plot(dates, fat_percents, marker='o', color='#ff6b6b', linewidth=4, markersize=12)
                ax.fill_between(range(len(dates)), fat_percents, alpha=0.4, color='#ff6b6b')
                for i, (d, v) in enumerate(zip(dates, fat_percents)):
                    ax.text(i, v + 1, f'{v}%', ha='center', fontsize=11, color='#ff6b6b', weight='bold')
                
                ax.set_facecolor('#2d1b2e')
                fig.patch.set_facecolor('#2d1b2e')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#999')
                ax.spines['bottom'].set_color('#999')
                ax.tick_params(colors='#999', labelsize=12)
                ax.grid(True, alpha=0.3, color='#999', linewidth=1)
                ax.set_xlabel('')
                ax.set_ylabel('')
                y_min = min(fat_percents) - 3
                y_max = max(fat_percents) + 3
                ax.set_ylim(y_min, y_max)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No progress yet. Start following your meal and workout plan!")
    
    elif st.session_state.active_page == "weight":
        with st.container(border=True):
            st.write("### Weight Management Tracker")
            st.write("Track your weight progress over time")
            st.write(f"**Current Weight: {coach.current_weight}kg** | **Target Weight: {target_weight}kg**")
            
            if len(all_weights) > 1:
                dates = [datetime.fromisoformat(w['timestamp']).strftime('%m-%d') for w in all_weights]
                weights = [w['weight'] for w in all_weights]
                
                fig, ax = plt.subplots(figsize=(16, 7))
                ax.plot(dates, weights, marker='o', color='#6ba8c4', linewidth=4, markersize=12)
                ax.fill_between(range(len(dates)), weights, alpha=0.4, color='#87ceeb')
                for i, (d, v) in enumerate(zip(dates, weights)):
                    ax.text(i, v + 1, f'{v}kg', ha='center', fontsize=11, color='#6ba8c4', weight='bold')
                
                ax.set_facecolor('#2d1b2e')
                fig.patch.set_facecolor('#2d1b2e')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#999')
                ax.spines['bottom'].set_color('#999')
                ax.tick_params(colors='#999', labelsize=12)
                ax.grid(True, alpha=0.3, color='#999', linewidth=1)
                ax.set_xlabel('')
                ax.set_ylabel('')
                y_min = min(weights) - 3
                y_max = max(weights) + 3
                ax.set_ylim(y_min, y_max)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No progress yet. Start following your meal and workout plan!")
    
    elif st.session_state.active_page == "muscle":
        with st.container(border=True):
            st.write("### Muscle Gain Tracker")
            st.write("Track your muscle gain progress")
            st.write(f"**Current Weight: {coach.current_weight}kg** | **Target Weight: {target_weight}kg**")
            
            if len(all_weights) > 1:
                dates = [datetime.fromisoformat(w['timestamp']).strftime('%m-%d') for w in all_weights]
                weights = [w['weight'] for w in all_weights]
                
                fig, ax = plt.subplots(figsize=(16, 7))
                ax.plot(dates, weights, marker='o', color='#51cf66', linewidth=4, markersize=12)
                ax.fill_between(range(len(dates)), weights, alpha=0.4, color='#51cf66')
                for i, (d, v) in enumerate(zip(dates, weights)):
                    ax.text(i, v + 1, f'{v}kg', ha='center', fontsize=11, color='#51cf66', weight='bold')
                
                ax.set_facecolor('#2d1b2e')
                fig.patch.set_facecolor('#2d1b2e')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#999')
                ax.spines['bottom'].set_color('#999')
                ax.tick_params(colors='#999', labelsize=12)
                ax.grid(True, alpha=0.3, color='#999', linewidth=1)
                ax.set_xlabel('')
                ax.set_ylabel('')
                y_min = min(weights) - 3
                y_max = max(weights) + 3
                ax.set_ylim(y_min, y_max)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No progress yet. Start following your meal and workout plan!")
    
    st.divider()
    
    # NEW USER GREETING
    if st.session_state.is_new_user and not st.session_state.greeted:
        greeting = coach.chat("Greet new user. Ask energy levels. Short and motivating.")
        st.session_state.greeted = True
        st.session_state.coach.conversation_history = [{"role": "assistant", "content": greeting}]
    
    if st.session_state.is_new_user and st.session_state.greeted:
        with st.chat_message("assistant"):
            st.write(st.session_state.coach.conversation_history[0]['content'])
        
        st.divider()
        st.write("### Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Workout done for the day", use_container_width=True, key="new_wd"):
                save_workout(st.session_state.user_id)
                reply = coach.chat("Acknowledge workout completed. Motivate in 1 sentence.")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.success("✅ Logged!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("Meal plan for my goal", use_container_width=True, key="new_mp"):
                reply = coach.chat(f"Give FULL 2-day meal plan {coach.target_calories}kcal/day with breakfast, lunch, dinner, snacks for each day. End with exactly: Follow this and come back to tell me how it went")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.rerun()
        
        with col3:
            if st.button("Workout plan for my goal", use_container_width=True, key="new_wp"):
                reply = coach.chat(f"Give FULL 2-day workout plan with exercises, sets, reps for each day. End with exactly: Follow this and come back to tell me how it went")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.rerun()
    else:
        st.write("### Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Workout done for the day", use_container_width=True, key="ret_wd"):
                save_workout(st.session_state.user_id)
                reply = coach.chat("Acknowledge workout completed. Motivate in 1 sentence.")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.success("✅ Logged!")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("Meal plan for my goal", use_container_width=True, key="ret_mp"):
                reply = coach.chat(f"Give FULL 2-day meal plan {coach.target_calories}kcal/day with breakfast, lunch, dinner, snacks for each day. End with exactly: Follow this and come back to tell me how it went")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.rerun()
        
        with col3:
            if st.button("Workout plan for my goal", use_container_width=True, key="ret_wp"):
                reply = coach.chat(f"Give FULL 2-day workout plan with exercises, sets, reps for each day. End with exactly: Follow this and come back to tell me how it went")
                with st.chat_message("assistant"):
                    st.write(reply)
                st.rerun()
    
    st.divider()
    for msg in coach.conversation_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    user_input = st.chat_input("Ask...")
    if user_input:
        reply = coach.chat(user_input)
        st.rerun()
    
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
