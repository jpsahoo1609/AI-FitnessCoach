# API Documentation - AI Fitness Coach

## Core Classes

### FitnessCoachAgent

Intelligent fitness coaching agent powered by GPT-4o-mini.

```python
coach = FitnessCoachAgent(
    user_id="user123",
    name="John",
    age=25,
    weight_kg=75,
    height_cm=180,
    gender="Male",
    activity_level="Moderate (3-5 days/week)",
    goal="Weight Loss",
    dietary_preference="Non-Vegetarian"
)
```

**Properties:**
- `bmi`: Calculated BMI value
- `bmi_category`: BMI category (Underweight/Normal/Overweight/Obese)
- `target_calories`: Daily calorie target
- `current_weight`: Current user weight
- `conversation_history`: List of chat messages

**Methods:**

#### `chat(user_message: str) -> str`
Send message to AI coach and get response.

```python
response = coach.chat("Give me a meal plan")
# Returns: "Here's your 2-day meal plan..."
```

**Parameters:**
- `user_message` (str): User query or command

**Returns:**
- (str): AI coach response

#### `update_weight(new_weight: float) -> None`
Update user weight and save to database.

```python
coach.update_weight(72.5)
```

---

## Fitness Calculations

### `calculate_bmi(weight_kg: float, height_cm: float) -> tuple`

Calculate Body Mass Index.

```python
bmi, category = calculate_bmi(75, 180)
# Returns: (21.1, "Normal")
```

**Parameters:**
- `weight_kg` (float): Weight in kilograms
- `height_cm` (float): Height in centimeters

**Returns:**
- (tuple): (bmi_value, category)

**Categories:**
- Underweight: < 18.5
- Normal: 18.5 - 24.9
- Overweight: 25 - 29.9
- Obese: ≥ 30

---

### `calculate_daily_calories(weight_kg, height_cm, age, gender, activity_level) -> int`

Calculate daily caloric needs using Mifflin-St Jeor equation.

```python
calories = calculate_daily_calories(75, 180, 25, "Male", "Moderate (3-5 days/week)")
# Returns: 2300
```

**Parameters:**
- `weight_kg` (float): Weight in kg
- `height_cm` (float): Height in cm
- `age` (int): Age in years
- `gender` (str): "Male" or "Female"
- `activity_level` (str): One of:
  - "Sedentary / Mostly Sitting" (1.2)
  - "Light (1-3 days/week)" (1.375)
  - "Moderate (3-5 days/week)" (1.55)
  - "Active (6-7 days/week)" (1.725)

**Returns:**
- (int): Daily calorie requirement

---

### `calculate_body_fat(weight_kg, height_cm, age, gender) -> float`

Estimate body fat percentage using Deurenberg formula.

```python
fat_percent = calculate_body_fat(75, 180, 25, "Male")
# Returns: 18.5
```

**Parameters:**
- `weight_kg` (float): Weight in kg
- `height_cm` (float): Height in cm
- `age` (int): Age in years
- `gender` (str): "Male" or "Female"

**Returns:**
- (float): Body fat percentage (minimum 10%)

---

### `calculate_target_weight(goal: str, current_weight: float) -> float`

Calculate goal weight based on fitness objective.

```python
target = calculate_target_weight("weight_loss", 75)
# Returns: 67.5
```

**Parameters:**
- `goal` (str): One of:
  - "weight_loss": 90% of current weight
  - "fat_loss": 90% of current weight
  - "muscle_gain": 110% of current weight
  - "maintenance": Current weight
- `current_weight` (float): Current weight in kg

**Returns:**
- (float): Target weight in kg

---

## Database Functions

### `save_user_profile(user_id: str, profile: dict) -> bool`

Save user profile to Supabase.

```python
profile = {
    "name": "John",
    "age": 25,
    "weight_kg": 75,
    "height_cm": 180,
    "gender": "Male",
    "activity_level": "Moderate (3-5 days/week)",
    "goal": "Weight Loss",
    "dietary_preference": "Non-Vegetarian"
}
save_user_profile("user123", profile)
```

**Parameters:**
- `user_id` (str): Unique user identifier
- `profile` (dict): User profile data

**Returns:**
- (bool): True if successful

---

### `load_user_profile(user_id: str) -> dict`

Retrieve user profile from Supabase.

```python
profile = load_user_profile("user123")
# Returns: {user_id, name, age, weight_kg, ...}
```

**Returns:**
- (dict): User profile or None if not found

---

### `save_weight(user_id: str, weight: float) -> bool`

Record weight entry with timestamp.

```python
save_weight("user123", 74.5)
```

**Returns:**
- (bool): True if successful

---

### `get_all_weights(user_id: str) -> list`

Retrieve weight history ordered by timestamp.

```python
weights = get_all_weights("user123")
# Returns: [{"weight": 75, "timestamp": "2024-01-01T..."}, ...]
```

**Returns:**
- (list): Weight entries with timestamps

---

### `get_latest_weight(user_id: str) -> float`

Get most recent weight entry.

```python
latest = get_latest_weight("user123")
# Returns: 74.5
```

**Returns:**
- (float): Latest weight value

---

### `save_workout(user_id: str) -> bool`

Log workout completion.

```python
save_workout("user123")
```

**Returns:**
- (bool): True if successful

---

### `get_workouts(user_id: str) -> list`

Retrieve workout history.

```python
workouts = get_workouts("user123")
# Returns: [{"date": "2024-01-01", "timestamp": "..."}, ...]
```

**Returns:**
- (list): Workout entries

---

## Progress Tracking

### `calculate_streak(workouts: list) -> int`

Calculate consecutive workout days.

```python
streak = calculate_streak(workouts)
# Returns: 5
```

**Parameters:**
- `workouts` (list): List of workout entries with dates

**Returns:**
- (int): Current streak count

---

### `get_consistency(filter_period: str, workouts: list) -> float`

Calculate workout consistency percentage.

```python
consistency = get_consistency("Week", workouts)
# Returns: 85.5
```

**Parameters:**
- `filter_period` (str): "Week", "Month", or "Year"
- `workouts` (list): Workout entries

**Returns:**
- (float): Consistency percentage (0-100)

---

## Error Handling

All functions return meaningful error messages via Streamlit:

```python
try:
    save_user_profile(user_id, profile)
except Exception as e:
    st.error(f"Error saving profile: {str(e)}")
```

---

## Rate Limits

- **OpenAI API**: Check account quota
- **Supabase**: Free tier: 500K API calls/month
- **Calculation Functions**: No limits (local)

---

## Best Practices

1. **Always validate inputs** before function calls
2. **Use session state** for performance
3. **Cache expensive operations** with `@st.cache_data`
4. **Handle exceptions gracefully** with try-except
5. **Use type hints** for clarity

---

## Examples

### Complete User Onboarding

```python
# 1. Create profile
profile = {
    "name": "Alice",
    "age": 28,
    "weight_kg": 70,
    "height_cm": 165,
    "gender": "Female",
    "activity_level": "Moderate (3-5 days/week)",
    "goal": "Fat Loss",
    "dietary_preference": "Vegetarian"
}
save_user_profile("user_alice", profile)

# 2. Initialize coach
coach = FitnessCoachAgent(**profile, user_id="user_alice")

# 3. Get personalized meal plan
meal_plan = coach.chat(f"Create 2-day meal plan for {coach.target_calories}kcal/day")

# 4. Track progress
save_weight("user_alice", 70)
save_workout("user_alice")

# 5. Get consistency
workouts = get_workouts("user_alice")
consistency = get_consistency("Week", workouts)
```

---

## Troubleshooting

**"Supabase connection error"**
- Verify credentials in secrets.toml
- Check internet connection
- Ensure RLS is disabled on tables

**"Invalid age/weight/height"**
- age: 10-100
- weight: 30-200 kg
- height: 100-250 cm

**"Empty workouts list"**
- User hasn't logged workouts yet
- Default to empty list, not error

