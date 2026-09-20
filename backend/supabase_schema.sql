-- Darukaa.Earth Database Schema for Supabase
-- Run this in your Supabase SQL Editor to create the necessary tables

-- Enable PostGIS extension for geographic data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sites table with geographic polygon support
CREATE TABLE IF NOT EXISTS sites (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    project_id BIGINT REFERENCES projects(id) ON DELETE CASCADE,
    geometry JSONB NOT NULL, -- GeoJSON geometry stored as JSONB
    area_hectares DECIMAL(10, 2),
    location_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_sites_project_id ON sites(project_id);
CREATE INDEX IF NOT EXISTS idx_sites_geometry ON sites USING GIN(geometry);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to automatically update updated_at
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sites_updated_at BEFORE UPDATE ON sites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample project (optional)
INSERT INTO projects (name, description, status) 
VALUES ('Default Project', 'Default conservation project', 'active')
ON CONFLICT DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE projects IS 'Conservation projects';
COMMENT ON TABLE sites IS 'Conservation sites with polygon geometries';
COMMENT ON COLUMN sites.geometry IS 'GeoJSON geometry (Polygon or MultiPolygon)';
COMMENT ON COLUMN sites.area_hectares IS 'Area of the site in hectares';
