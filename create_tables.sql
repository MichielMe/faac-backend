-- Create tables without foreign key constraints first
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    pictogram_url TEXT,
    language VARCHAR NOT NULL DEFAULT 'en',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    audio_id INTEGER
);

-- Create index on keywords.name
CREATE INDEX IF NOT EXISTS idx_keywords_name ON keywords(name);

-- Create audio_files table
CREATE TABLE IF NOT EXISTS audio_files (
    id SERIAL PRIMARY KEY,
    voice_man VARCHAR,
    voice_woman VARCHAR,
    keyword_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraints after both tables exist
ALTER TABLE audio_files 
ADD CONSTRAINT fk_keyword FOREIGN KEY (keyword_id) REFERENCES keywords(id);

ALTER TABLE keywords 
ADD CONSTRAINT fk_audio FOREIGN KEY (audio_id) REFERENCES audio_files(id); 