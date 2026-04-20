# Setup Guide - AI Fitness Coach

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- Supabase account (free at https://supabase.com)
- OpenAI API key (https://platform.openai.com/api-keys)

## 🔧 Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/jpsahoo1609/ai-fitness-coach.git
cd ai-fitness-coach
```

### Step 2: Virtual Environment
```bash
# Create
python -m venv venv

# Activate
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Supabase Setup

1. **Create Project**
   - Go to https://supabase.com
   - Create new project
   - Copy Project URL and anon public key

2. **Create Tables**
   - Go to SQL Editor in Supabase
   - Copy entire content from `supabase_setup.sql`
   - Execute the SQL

3. **Disable RLS** (for development)
   ```sql
   ALTER TABLE users DISABLE ROW LEVEL SECURITY;
   ALTER TABLE weights DISABLE ROW LEVEL SECURITY;
   ALTER TABLE workouts DISABLE ROW LEVEL SECURITY;
   ```

### Step 5: Configure Secrets
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY = "sk-proj-your-key-here"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
EOF
```

### Step 6: Run Application
```bash
streamlit run app_with_supabase.py
```

Visit `http://localhost:8501`

## 🚀 Streamlit Cloud Deployment

### Prerequisites
- GitHub account with repo pushed
- Streamlit Cloud account (https://streamlit.io/cloud)

### Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select repository, branch, and `app_with_supabase.py`
   - Click Deploy

3. **Add Secrets**
   - After deployment, click "..." → Settings
   - Go to "Secrets"
   - Add:
   ```toml
   OPENAI_API_KEY = "your-key"
   SUPABASE_URL = "your-url"
   SUPABASE_KEY = "your-key"
   ```

4. **Done!**
   - App auto-deploys with secrets
   - Live URL: `https://yourusername-app-name.streamlit.app`

## 🧪 Running Tests

### Unit Tests
```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_fitness_calculations.py -v

# With coverage
pytest --cov=. tests/
```

### Databricks Testing
```bash
python databricks_testing_notebook.py
```

## 🐛 Troubleshooting

### "Supabase connection error"
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in secrets
- Check internet connection
- Ensure Supabase project is active

### "Error saving profile"
- Ensure RLS is disabled on tables
- Check that tables exist in Supabase
- Verify no duplicate user_id

### "OpenAI API error"
- Verify `OPENAI_API_KEY` is correct
- Check OpenAI account has credits
- Ensure API key has no restrictions

### "Port 8501 already in use"
```bash
streamlit run app_with_supabase.py --server.port 8502
```

## 📊 Database Schema

### users table
```
user_id (TEXT, PK)
name (TEXT)
age (INTEGER)
weight_kg (DECIMAL)
height_cm (DECIMAL)
gender (TEXT)
activity_level (TEXT)
goal (TEXT)
dietary_preference (TEXT)
created_at (TIMESTAMP)
```

### weights table
```
id (BIGINT, PK)
user_id (TEXT, FK)
weight (DECIMAL)
timestamp (TIMESTAMP)
```

### workouts table
```
id (BIGINT, PK)
user_id (TEXT, FK)
date (TEXT)
timestamp (TIMESTAMP)
```

## 🔐 Security Notes

- Never commit `.streamlit/secrets.toml` to git
- Add to `.gitignore`:
  ```
  .streamlit/secrets.toml
  __pycache__/
  .pytest_cache/
  *.pyc
  venv/
  .DS_Store
  ```
- Use environment variables for all secrets
- Enable RLS policies in production (see `rls_policies.sql`)

## 📈 Performance Tips

- Cache expensive computations with `@st.cache_data`
- Use `st.session_state` for persistent data
- Limit graph data points for faster rendering
- Use connection pooling for Supabase queries

## 🆘 Need Help?

- Check GitHub Issues
- Read Streamlit docs: https://docs.streamlit.io
- Supabase guide: https://supabase.com/docs
- OpenAI docs: https://platform.openai.com/docs
