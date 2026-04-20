-- Create users table
CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  age INTEGER NOT NULL,
  weight_kg DECIMAL(10, 2) NOT NULL,
  height_cm DECIMAL(10, 2) NOT NULL,
  gender TEXT NOT NULL,
  activity_level TEXT NOT NULL,
  goal TEXT NOT NULL,
  dietary_preference TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create weights table for tracking weight history
CREATE TABLE weights (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  weight DECIMAL(10, 2) NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create workouts table for tracking workout history
CREATE TABLE workouts (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  date TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_weights_user_id ON weights(user_id);
CREATE INDEX idx_workouts_user_id ON workouts(user_id);
CREATE INDEX idx_weights_timestamp ON weights(timestamp);
CREATE INDEX idx_workouts_date ON workouts(date);

-- Enable Row Level Security (optional but recommended for security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE weights ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;