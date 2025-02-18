-- Create UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users (Doctors) table
CREATE TABLE users (
    user_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE patients (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID NOT NULL,                    -- Doctor who manages this patient
    patient_id VARCHAR(20) UNIQUE NOT NULL,   -- Business identifier
    name VARCHAR(100) NOT NULL,
    sex VARCHAR(10) CHECK (sex IN ('Male', 'Female', 'Other')),
    date_of_birth DATE NOT NULL,
    age INTEGER,                              -- Updated via trigger
    phone VARCHAR(20),
    address TEXT,
    past_medical_history TEXT,
    present_illness_history TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
);

-- Detection Sessions (formerly appointments) table
CREATE TABLE detection_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    patient_id UUID NOT NULL,
    user_id UUID NOT NULL,                    -- Doctor conducting detection
    detection_date TIMESTAMP WITH TIME ZONE NOT NULL,
    detection_result JSONB,                   -- Detection result based on one or multiple images
    diagnostic_result TEXT,                   -- Doctor's interpretation/notes
    follow_up_plan TEXT,                      -- Doctor's follow-up plan
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_patient
        FOREIGN KEY(patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
);

-- Detection images table
CREATE TABLE detection_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    detection_session_id UUID NOT NULL,
    image_path TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detection_session
        FOREIGN KEY(detection_session_id)
        REFERENCES detection_sessions(id)
        ON DELETE CASCADE
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create age calculation trigger function
CREATE OR REPLACE FUNCTION update_age_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.age = EXTRACT(YEAR FROM age(CURRENT_DATE, NEW.date_of_birth));
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_detection_sessions_updated_at
    BEFORE UPDATE ON detection_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for age calculation
CREATE TRIGGER update_patient_age
    BEFORE INSERT OR UPDATE OF date_of_birth ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_age_column();

-- Create indices for performance
CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_patients_user ON patients(user_id);
CREATE INDEX idx_patients_patient_id ON patients(patient_id);
CREATE INDEX idx_detection_sessions_patient ON detection_sessions(patient_id);
CREATE INDEX idx_detection_sessions_user ON detection_sessions(user_id);
CREATE INDEX idx_detection_sessions_date ON detection_sessions(detection_date);
CREATE INDEX idx_detection_images_session ON detection_images(detection_session_id);

-- Insert default admin user (password should be properly hashed in production)
INSERT INTO users (user_id, username, password_hash)
VALUES (uuid_generate_v4(), 'admin_user', 'admin123user')
ON CONFLICT (username) DO NOTHING;