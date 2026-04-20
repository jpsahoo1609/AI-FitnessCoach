# Databricks notebook source
# MAGIC %pip install openai

# COMMAND ----------

# After installing a new library, Python needs a restart to recognize it.
dbutils.library.restartPython()

# COMMAND ----------

# Loading my apikey from secret scope 
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="OpenAPIkey", key="openai-api-key")
print("Loaded ✅")

# COMMAND ----------

# Restarting kernel 
dbutils.library.restartPython()

# COMMAND ----------

# Loaing api key import os
import os
os.environ["OPENAI_API_KEY"] = dbutils.secrets.get(scope="OpenAPIkey", key="openai-api-key")
print("API key loaded ✅")


# COMMAND ----------

# First LLM call
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful fitness coach."},
        {"role": "user", "content": "Give me a simple 3-meal diet plan for weight loss."}
    ]
)

print(response.choices[0].message.content)

# COMMAND ----------

# Chekcing how billing works 
print("Input tokens:", response.usage.prompt_tokens)
print("Output tokens:", response.usage.completion_tokens)
print("Total tokens:", response.usage.total_tokens)
print("Approx cost: $", round(response.usage.total_tokens / 1_000_000 * 0.6, 6))

# COMMAND ----------

# MAGIC %md
# MAGIC The LLM has zero memory by itself — it's stateless. We fake memory by sending the full conversation history every time. The *conversation_history* unpacks the list into the messages. This is the most important concept in agents.

# COMMAND ----------

# Adding memory

conversation_history = []

def chat_with_memory(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert fitness coach."},
            *conversation_history
        ]
    )
    
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    return reply

print(chat_with_memory("My name is Jyoti, I weigh 80kg and want to lose weight"))
print("---")
print(chat_with_memory("What should I eat for breakfast?"))
print("---")
print(chat_with_memory("Make it vegetarian"))

# COMMAND ----------

# MAGIC %md
# MAGIC LLM for reasoning, my code for precise calculation. Never trust the LLM to do math. You calculate BMI/calories accurately, then pass the results into the LLM's context.

# COMMAND ----------

# BMI & Calorie Tools

def calculate_bmi(weight_kg, height_cm):
    bmi = weight_kg / (height_cm / 100) ** 2
    if bmi < 18.5: category = "Underweight"
    elif bmi < 25: category = "Normal"
    elif bmi < 30: category = "Overweight"
    else: category = "Obese"
    return round(bmi, 1), category

def calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level):
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    multipliers = {
    "sedentary": 1.2,
    "mostly sitting": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725
}
    return int(bmr * multipliers[activity_level])

# Test
bmi, category = calculate_bmi(80, 175)
calories = calculate_daily_calories(80, 175, 25, "male", "sedentary")
print(f"BMI: {bmi} ({category})")
print(f"Daily calories: {calories} kcal")

# COMMAND ----------

# Setting up the user goal function (weight loss, fat loss, muscle gain, maintenance)
def normalize_goal(user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Classify this fitness goal into exactly one of these: weight_loss, fat_loss, muscle_gain, maintenance. User said: '{user_input}'. Reply with only the classification word, nothing else."
        }]
    )
    return response.choices[0].message.content.strip()

# COMMAND ----------

# MAGIC %md
# MAGIC A class bundles the user profile, memory, and chat logic into one clean object. The system prompt is dynamically built with real calculated data — not guesses by the LLM. Every .chat() call automatically maintains memory.

# COMMAND ----------

class FitnessCoachAgent:
    
    def __init__(self, name, age, weight_kg, height_cm, gender, activity_level, goal, dietary_preference):
        self.client = OpenAI()
        self.conversation_history = []
        
        bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
        daily_calories = calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level)
        normalized_goal = normalize_goal(goal) 
        if normalized_goal in ["weight_loss", "fat_loss"]:
            target_calories = daily_calories - 500
        elif normalized_goal == "muscle_gain":
            target_calories = daily_calories + 300
        else:  # maintenance
            target_calories = daily_calories
        
        self.system_prompt = f"""
        You are an expert AI fitness coach. Your client's profile:
        Name: {name} | Age: {age} | Weight: {weight_kg}kg | Height: {height_cm}cm
        BMI: {bmi} ({bmi_category}) | Goal: {goal} | Diet: {dietary_preference}
        Target Calories: {target_calories} kcal/day
        
        Always give personalized advice based on this profile.
        Suggest Indian food options wherever possible.
        Be specific, motivating, and data-driven.
        """
        
        print(f"✅ Coach ready for {name}!")
        print(f"   BMI: {bmi} ({bmi_category})")
        print(f"   Target Calories: {target_calories} kcal/day")
    
    def chat(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
        )
        
        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

# COMMAND ----------

#Testing my FitnessCoachAgent

coach = FitnessCoachAgent(
    name="Jyoti",
    age=25,
    weight_kg=80,
    height_cm=175,
    gender="male",
    activity_level="sedentary",
    goal="weight_loss",
    dietary_preference="vegetarian"
)

print(coach.chat("Give me a full Monday meal plan"))

# COMMAND ----------

# Testing scenarios 
print(coach.chat("Give me a workout plan for this week"))

# COMMAND ----------

# Checking if my Agent remembers me or not 
print(coach.chat("I completed Monday workout but feeling tired, any tips?"))

# COMMAND ----------

#Testing my agen if he remembers , what i did on Monday 
print(coach.chat("Tell me what exercise you told me to do on Monday"))

# COMMAND ----------

# Testing memory 
print(coach.chat("Can you tell me what I ate on Monday "))

# COMMAND ----------

# MAGIC %md
# MAGIC Creating delta tables in databricks 

# COMMAND ----------

spark.sql("CREATE DATABASE IF NOT EXISTS fitness_db")
spark.sql("USE fitness_db")

# COMMAND ----------

#Saving the history form of delta table in Databricks db for long term memory 
from datetime import datetime

def save_progress(user_id, weight_kg, notes):
    data = [{
        "user_id": user_id,
        "date": datetime.now().isoformat(),
        "weight_kg": weight_kg,
        "notes": notes
    }]
    df = spark.createDataFrame(data)
    df.write.mode("append").saveAsTable("fitness_progress")
    print(f"Progress saved ✅")

def load_progress(user_id):
    return spark.sql(f"""
        SELECT * FROM fitness_progress 
        WHERE user_id = '{user_id}' 
        ORDER BY date DESC 
        LIMIT 10
    """)

# Test it
save_progress("jyoti_001", 80.0, "Completed Monday workout, felt tired")
load_progress("jyoti_001").show()

# COMMAND ----------

# Loading past progress back into the agent for long term memory 
def get_progress_summary(user_id):
    try:
        df = spark.sql(f"""
            SELECT * FROM fitness_db.fitness_progress 
            WHERE user_id = '{user_id}' 
            ORDER BY date DESC 
            LIMIT 5
        """)
        rows = df.collect()
        if not rows:
            return "No previous progress recorded."
        
        summary = "User's recent progress:\n"
        for row in rows:
            summary += f"- {row['date'][:10]}: Weight {row['weight_kg']}kg — {row['notes']}\n"
        return summary
    except:
        return "No previous progress recorded."

# Test it
print(get_progress_summary("jyoti_001"))

# COMMAND ----------

# Rewriting the full agent class with everything integrated — dynamic progress loading, automatic progress saving, all in one.

class FitnessCoachAgent:
    
    def __init__(self, user_id, name, age, weight_kg, height_cm, gender, activity_level, goal, dietary_preference):
        self.client = OpenAI()
        self.conversation_history = []
        self.user_id = user_id
        self.current_weight = weight_kg
        
        bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
        daily_calories = calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level)
        
        # Normalize goal from natural language
        normalized_goal = normalize_goal(goal)
        
        if normalized_goal in ["weight_loss", "fat_loss"]:
            target_calories = daily_calories - 500
        elif normalized_goal == "muscle_gain":
            target_calories = daily_calories + 300
        else:
            target_calories = daily_calories
        
        # Automatically load past progress from Delta table
        progress_summary = get_progress_summary(user_id)
        
        self.system_prompt = f"""
        You are an expert AI fitness coach. Your client's profile:
        Name: {name} | Age: {age} | Weight: {weight_kg}kg | Height: {height_cm}cm
        BMI: {bmi} ({bmi_category}) | Goal: {normalized_goal} | Diet: {dietary_preference}
        Target Calories: {target_calories} kcal/day
        
        Client's past progress history (use this to personalize advice):
        {progress_summary}
        
        Rules:
        - Always give personalized advice based on profile and past progress
        - Suggest Indian food options wherever possible
        - Be specific, motivating, and data-driven
        - When user mentions completing a workout or shares their weight, acknowledge progress
        """
        
        print(f"✅ Coach ready for {name}!")
        print(f"   BMI: {bmi} ({bmi_category})")
        print(f"   Normalized Goal: {normalized_goal}")
        print(f"   Target Calories: {target_calories} kcal/day")
        print(f"   Past progress loaded: {progress_summary[:50]}...")
    
    def chat(self, user_message):
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ]
        )
        
        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})
        self._auto_save_progress(user_message)
        
        return reply
    
    def _auto_save_progress(self, user_message):
        triggers = ["completed", "finished", "done", "kg", "weight", "workout", "tired", "feeling"]
        if any(word in user_message.lower() for word in triggers):
            save_progress(self.user_id, self.current_weight, user_message)
            print("📝 Progress auto-saved!")
    
    def update_weight(self, new_weight):
        self.current_weight = new_weight
        save_progress(self.user_id, new_weight, f"Weight updated to {new_weight}kg")
        print(f"⚖️ Weight updated to {new_weight}kg and saved!")


# Test with natural language goal
coach = FitnessCoachAgent(
    user_id="john_001",
    name="John",
    age=35,
    weight_kg=86,
    height_cm=174,
    gender="male",
    activity_level="mostly sitting",
    goal="fat loss",
    dietary_preference="non-vegetarian"
)

print(coach.chat("Good morning! What should I eat today?"))

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from fitness_db.fitness_progress

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS fitness_db.profiles (
# MAGIC     user_id STRING PRIMARY KEY,
# MAGIC     name STRING,
# MAGIC     age INT,
# MAGIC     weight_kg FLOAT,
# MAGIC     height_cm FLOAT,
# MAGIC     gender STRING,
# MAGIC     activity_level STRING,
# MAGIC     goal STRING,
# MAGIC     dietary_preference STRING,
# MAGIC     created_at TIMESTAMP
# MAGIC );
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS fitness_db.progress (
# MAGIC     user_id STRING,
# MAGIC     weight_kg FLOAT,
# MAGIC     message STRING,
# MAGIC     timestamp TIMESTAMP
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS fitness_db.progress;
# MAGIC CREATE TABLE fitness_db.progress (
# MAGIC     user_id STRING,
# MAGIC     weight_kg FLOAT,
# MAGIC     timestamp TIMESTAMP
# MAGIC );

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP TABLE IF EXISTS fitness_db.workouts;
# MAGIC CREATE TABLE fitness_db.workouts (
# MAGIC     user_id STRING,
# MAGIC     date DATE,
# MAGIC     workout_type STRING,
# MAGIC     duration_minutes INT,
# MAGIC     timestamp TIMESTAMP
# MAGIC );

# COMMAND ----------

