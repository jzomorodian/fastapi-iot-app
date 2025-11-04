-- init-data.sql
-- Create tables (ensure your app handles table creation if not using migrations)
CREATE TABLE IF NOT EXISTS units (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    location VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensor_data (
    id UUID PRIMARY KEY,
    unit_id UUID REFERENCES units(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    temperature NUMERIC,
    humidity NUMERIC,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    is_archived BOOLEAN NOT NULL DEFAULT FALSE
);

-- Insert sample data for units
INSERT INTO units (id, name, location) VALUES
('b08499c7-5e6a-4d9b-a7f4-21915f01198c', 'Assembly-Line-1', 'Factory Floor 1'),
('1a3b5c7d-9e0f-11a2-b3c4-5d6e7f8a9b0c', 'HVAC-Rooftop-7', 'Building A Roof')
ON CONFLICT (id) DO NOTHING;

-- Insert sample sensor data
INSERT INTO sensor_data (id, unit_id, temperature, humidity, status) VALUES
('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'b08499c7-5e6a-4d9b-a7f4-21915f01198c', 23.5, 45.2, 'VALIDATED'),
('550e8400-e29b-41d4-a716-446655440000', 'b08499c7-5e6a-4d9b-a7f4-21915f01198c', 24.1, 46.0, 'PENDING'),
('6ba7b810-9dad-11d1-80b4-00c04fd430c8', '1a3b5c7d-9e0f-11a2-b3c4-5d6e7f8a9b0c', 19.8, 52.3, 'PENDING')
ON CONFLICT (id) DO NOTHING;
