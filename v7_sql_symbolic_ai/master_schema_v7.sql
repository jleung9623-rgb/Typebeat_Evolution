-- ==========================================
-- TYPEBEAT AI V7.0 - MASTER SCHEMA (FINAL HARDENED)
-- ==========================================

-- DANGER: Uncomment the line below to wipe the city for a clean rebuild
-- DROP DATABASE IF EXISTS typebeat_ai_v7;

-- 1. Infrastructure Setup
CREATE DATABASE IF NOT EXISTS typebeat_ai_v7;
USE typebeat_ai_v7;

-- 2. Genre DNA Registry
CREATE TABLE IF NOT EXISTS genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(50) NOT NULL UNIQUE,
    default_tempo INT DEFAULT 120,
    time_signature VARCHAR(10) DEFAULT '4/4',
    entropy_pivot_bar INT DEFAULT 8,
    -- 2a Integrated root note into the base table for clean architecture
    default_root_note VARCHAR(10) DEFAULT 'C'
);

-- 2a. Add Pop-Punk genre
INSERT IGNORE INTO genres (genre_name, default_tempo, time_signature, entropy_pivot_bar, default_root_note)
VALUES ('Pop-Punk', 160, '4/4', 8, 'C');

-- 3. Hardware & Routing Registry
CREATE TABLE IF NOT EXISTS tracks (
    track_id INT AUTO_INCREMENT PRIMARY KEY,
    track_name VARCHAR(50) NOT NULL,
    midi_channel INT NOT NULL,
    instrument_name VARCHAR(50) DEFAULT 'Acoustic Grand Piano'
);

-- Seed: Standard Routing
INSERT IGNORE INTO tracks (track_name, midi_channel, instrument_name)
VALUES 
('Piano', 0, 'Acoustic Grand Piano'),
('Bass', 1, 'Electric Bass (finger)'),
('Drums', 10, 'Percussion');

-- 3a. Scale Registry (Law)
CREATE TABLE IF NOT EXISTS scales (
    scale_id INT AUTO_INCREMENT PRIMARY KEY,
    -- Suggestion #1: Added UNIQUE to prevent duplicate scale definitions
    scale_name VARCHAR(50) NOT NULL UNIQUE, 
    intervals VARCHAR(50) NOT NULL
);

-- 3b. C Major DNA
INSERT IGNORE INTO scales (scale_name, intervals) 
VALUES ('Major', '0,2,4,5,7,9,11');

-- 3c. Linking Scales to Genres
ALTER TABLE genres 
ADD COLUMN scale_id INT,
ADD FOREIGN KEY (scale_id) REFERENCES scales(scale_id) ON DELETE SET NULL;

-- 3d. Link Pop-Punk to Major Scale
UPDATE genres SET scale_id = 1 WHERE genre_name = 'Pop-Punk';

-- 3e. Adds a column for patch_number with a default value of 1 (Acoustic Grand Piano)
ALTER TABLE tracks 
ADD COLUMN patch_number INT DEFAULT 1;

-- Update the Electric Bass
UPDATE tracks 
SET patch_number = 34 
WHERE track_name = 'Bass';

-- Update the Drums
UPDATE tracks 
SET patch_number = 17 
WHERE track_name = 'Drums' AND midi_channel = 10;

-- 3f. Add genre_id as a foreign key
ALTER TABLE tracks ADD COLUMN genre_id INT;
ALTER TABLE tracks 
ADD CONSTRAINT fk_track_genre 
FOREIGN KEY (genre_id) REFERENCES genres(genre_id);
UPDATE tracks SET genre_id = 1;

-- 4. Stochastic Engine Room (Markov Chain Memory)
CREATE TABLE IF NOT EXISTS transitions (
    transition_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_id INT NOT NULL,
    track_id INT NOT NULL,
    prev_note VARCHAR(10) NOT NULL,
    next_note VARCHAR(10) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    duration_value FLOAT DEFAULT 1.0,
    -- Suggestion #7a: rest_value added here directly to avoid later ALTER/MODIFY bloat
    rest_value FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    micro_offset FLOAT DEFAULT 0.0,
    
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
);

-- 4a. These indexes ensure that fetching the "next note" stays under 1ms even with millions of rows.
CREATE INDEX idx_transition_lookup ON transitions(genre_id, track_id, prev_note, is_active);

-- 4b. Pop-Punk Piano Start
INSERT IGNORE INTO transitions (genre_id, track_id, prev_note, next_note, weight, duration_value)
VALUES (1, 1, 'START', 'C4', 1.0, 1.0);

-- 4c. Create a basic note sequence that loops back to C4
INSERT INTO transitions (genre_id, track_id, prev_note, next_note, weight) VALUES (1, 1, 'C4', 'G4', 100);
INSERT INTO transitions (genre_id, track_id, prev_note, next_note, weight) VALUES (1, 1, 'G4', 'A4', 100);
INSERT INTO transitions (genre_id, track_id, prev_note, next_note, weight) VALUES (1, 1, 'A4', 'C4', 100);

-- 5. Artist DNA Registry
CREATE TABLE IF NOT EXISTS artists (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    artist_name VARCHAR(50) NOT NULL UNIQUE,
    genre_id INT NOT NULL,
    scale_id INT,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE,
    FOREIGN KEY (scale_id) REFERENCES scales(scale_id) ON DELETE SET NULL
);

-- 6. Harmonic Infrastructure
CREATE TABLE IF NOT EXISTS chords (
    chord_id INT AUTO_INCREMENT PRIMARY KEY,
    chord_name VARCHAR(20) NOT NULL UNIQUE,
    vibe_tag VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS chord_notes (
    note_id INT AUTO_INCREMENT PRIMARY KEY,
    chord_id INT NOT NULL,
    note_name VARCHAR(10) NOT NULL,
    FOREIGN KEY (chord_id) REFERENCES chords(chord_id) ON DELETE CASCADE
);

-- 7. Macro Intelligence (Motifs)
CREATE TABLE IF NOT EXISTS motifs (
    motif_id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT NOT NULL,
    motif_name VARCHAR(50),
    sequence_data TEXT NOT NULL,
    -- 7a: rest_value positioned surgically after sequence_data
    rest_value FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    micro_offset FLOAT DEFAULT 0.0,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE
);

-- 8. The Registry (Audit Trail)
CREATE TABLE IF NOT EXISTS compositions (
    comp_id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    -- 8a. Added root_note directly for transposition tracking
    root_note VARCHAR(10) DEFAULT 'C',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id) ON DELETE CASCADE
);

-- 9. Global Dashboard (User Preferences)
CREATE TABLE IF NOT EXISTS user_preferences (
    pref_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(50) UNIQUE,
    setting_value VARCHAR(100)
);

-- 9a. Add default option set into user preferences
INSERT INTO user_preferences (setting_key, setting_value)
VALUES 
    ('default_bpm', '145'),
    ('composition_title', 'Pop-Punk Default');

-- 9b. Add the Universal Fallback to your 10-Table City
INSERT INTO user_preferences (setting_key, setting_value) 
VALUES ('default_start_note', 'C4');