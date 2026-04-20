# AI Fitness Coach
## *Your Personal AI-Powered Fitness Revolution*

> **Transform your fitness journey with intelligent AI coaching. Personalized meal plans. Smart workouts. Real-time progress tracking. All in one beautiful app.**

[![Streamlit Cloud](https://img.shields.io/badge/Deployed%20on-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://your-app-url.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![GPT-4o Mini](https://img.shields.io/badge/Powered%20by-GPT--4o%20Mini-10A37F?style=for-the-badge&logo=openai)](https://openai.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---
### Try it out - https://ai-fitnesscoach.streamlit.app/
---
## 🚀 What Makes This Special?

This isn't just another fitness app. It's a **production-ready, cloud-native application** that demonstrates:

✅ **Full-Stack Development** - Frontend (Streamlit), Backend (Python), Database (Supabase)  
✅ **AI Integration** - GPT-4o-mini for intelligent coaching  
✅ **Enterprise Code Quality** - 920+ lines of well-structured code  
✅ **Comprehensive Testing** - Unit tests + Databricks end-to-end testing  
✅ **Cloud Deployment** - Streamlit Cloud + Supabase PostgreSQL  
✅ **Real-World Fitness Science** - Mifflin-St Jeor & Deurenberg formulas  

---

## ⭐ Key Features

### 🤖 **AI-Powered Coaching**
Personalized guidance powered by GPT-4o-mini. The AI understands your fitness goals and provides customized advice, meal plans, and workout routines tailored specifically to you.

### 🍽️ **Smart Meal Planning**
Generates customized 2-day meal plans based on your daily calorie targets and dietary preferences (Vegetarian/Non-Vegetarian/Vegan).

### 💪 **Intelligent Workout Plans**
AI-created workout routines with exercises, sets, and reps tailored to your fitness goal (Weight Loss, Fat Loss, Muscle Gain, Maintenance).

### 📊 **Real-Time Progress Tracking**
- Interactive weight loss/gain graphs
- Body fat percentage estimation
- Workout streak counter
- Weekly/Monthly/Yearly consistency metrics
- Detailed progress dashboard

### 🎨 **Modern UI**
Beautiful dark mode interface with responsive design, smooth animations, and intuitive user experience.

---

## 🏗️ Technical Architecture

### **Tech Stack**
| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit (Python) - Modern, responsive UI |
| **Backend** | Python 3.10+ - Clean, scalable code |
| **AI Engine** | OpenAI GPT-4o-mini - Intelligent coaching |
| **Database** | Supabase (PostgreSQL) - Cloud-native, scalable |
| **Hosting** | Streamlit Cloud - Zero-config deployment|

### **Core Calculations**
- **BMI**: Standard body mass index with health categories
- **Daily Calories**: Mifflin-St Jeor equation (industry standard)
- **Body Fat %**: Deurenberg formula (gender-specific, age-adjusted)
- **Target Metrics**: Dynamic goal-based calculations

---

## 📈 Project Stats

| Metric | Value |
|--------|-------|
| **Lines of Code** | 720+ (main app) |
| **Test Coverage** | 100+ test cases |
| **Functions** | 20+ well-documented |
| **Database Tables** | 3 (optimized schema) |
| **Dependencies** | 10 (carefully selected) |
| **Documentation** | 4 professional markdown files |

---

## 🧪 Comprehensive Testing

### Unit Tests (`tests_fitness_calculations.py`)
- ✅ BMI calculations (4 categories)
- ✅ Calorie calculations (gender, age, activity variations)
- ✅ Body fat percentage (gender-specific)
- ✅ Target weight for all goals
- ✅ Integration tests

### End-to-End Testing (`databricks_testing_notebook.py`)
Runs on **Databricks** for production validation:
- ✅ TEST 1: Fitness calculations (3 profiles)
- ✅ TEST 2: Goal-based metrics (4 goals)
- ✅ TEST 3: Progress tracking (streaks & consistency)
- ✅ TEST 4: Data validation (9 fields)
- ✅ TEST 5: Performance benchmarks (3 functions)

---

## 🚀 Quick Start (60 seconds)

### Local Setup
```bash
# 1. Clone
git clone https://github.com/jpsahoo1609/ai-fitness-coach.git
cd ai-fitness-coach

# 2. Create environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add secrets
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY = "your-key"
SUPABASE_URL = "your-url"
SUPABASE_KEY = "your-key"
EOF

# 5. Run
streamlit run app_with_supabase.py
```

**App ready at**: `http://localhost:8501`

### Cloud Deployment (2 minutes)
1. Push repo to GitHub
2. Go to https://streamlit.io/cloud
3. Click "New app" → Select repo
4. Add secrets in Settings
5. **Live!** 🎉

---

## 💡 How It Works

```
User Input (Profile) 
    ↓
Fitness Calculations (BMI, Calories, Body Fat)
    ↓
Supabase Database (Cloud Storage)
    ↓
GPT-4o-mini AI (Personalized Coaching)
    ↓
Dashboard (Progress Tracking + Graphs)
```

### User Journey

1. **Signup**: Create profile with health metrics
2. **AI Analysis**: System calculates personalized targets
3. **Get Coached**: AI generates meal & workout plans
4. **Track Progress**: Log workouts, update weight
5. **See Results**: Real-time graphs + consistency tracking

---

## 📊 Database Schema

### Users Table
```sql
user_id (PK) | name | age | weight_kg | height_cm | gender | 
activity_level | goal | dietary_preference | created_at
```

### Weights Table
```sql
id (PK) | user_id (FK) | weight | timestamp
```

### Workouts Table
```sql
id (PK) | user_id (FK) | date | timestamp
```

---

## 🔐 Security & Best Practices

✅ Environment variables for all secrets  
✅ Row-Level Security policies available  
✅ Session token validation  
✅ No hardcoded credentials  
✅ HTTPS enforced  
✅ Proper error handling  
✅ Input validation  

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **README.md** | Overview (you are here) |
| **SETUP.md** | Detailed installation guide |
| **API.md** | Complete function reference |
| **PROJECT_STRUCTURE.md** | Repo organization |

---

## 🎯 What Recruiters Will See

✅ **Production-ready code** - Not a hobby project  
✅ **Full-stack expertise** - Frontend, backend, database, AI  
✅ **Cloud deployment** - Real-world infrastructure  
✅ **Testing mindset** - Unit + E2E tests on Databricks  
✅ **Documentation** - Professional standards  
✅ **Problem-solving** - Fitness science + AI integration  
✅ **Code quality** - Clean, organized, maintainable  
✅ **DevOps knowledge** - Secrets management, CI/CD ready  

---

## 🤝 Contributing

Found a bug? Have ideas? Open an [Issue](https://github.com/jpsahoo1609/ai-fitness-coach/issues) or submit a [Pull Request](https://github.com/jpsahoo1609/ai-fitness-coach/pulls).

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 About

Built to showcase:
- 🏢 Enterprise-grade Python development
- 🤖 AI/ML integration at scale
- ☁️ Cloud-native architecture
- 🧪 Professional testing practices
- 📊 Real-world fitness science

**Let's build something amazing together!**

---

## 📞 Connect

- GitHub: [link](https://github.com/jpsahoo1609)
- LinkedIn: [link](www.linkedin.com/in/jyoti-prakash-sahooo-95a542211)
- Email: jpsahoo1609@gmail.com

---

⭐ **If this impressed you, please give it a star!**
