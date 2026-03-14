import random
import re
import datetime
import mysql.connector 
from mysql.connector import Error
import os
from dotenv import load_dotenv
from music21 import stream, note, chord, instrument, interval, metadata, midi, tempo

DEFAULT_STEPS = 16 # Initialize default length of song (16 = 4 bars)

class DatabaseManager:
    """Handles all communication with the MySQL database"""

    def __init__(self, host='localhost', user='root', database='typebeat_ai_v7'):
        # Load .env file into the environment, overrides system defaults
        load_dotenv(override=True)
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "typebeat_ai_v7")

        print(f"--- Logging in as '{db_user}' ---")

        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name
            )
            if self.connection.is_connected():
                print(f"--- SUCCESS: Established connection with {db_name} ---")
        except Error as e:
            print(f"--- ERROR: Could not connect to database: {e} ---") # Error message for SQL-side initialization and connection errors
            exit()
    
    def fetch_user_preferences(self):
        """Fetches the EAV Key-Value pairs and converts them to a Python Dictionary."""
        query = "SELECT setting_key, setting_value FROM user_preferences"
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        # Convert List of rows into a dictionary
        # e.g., {'default_bpm': '145', 'theme': 'dark'}
        return {row['setting_key']: row['setting_value'] for row in rows}
    
    # Import track data
    def fetch_track_data(self, genre_name):
        """Fetches all MIDI instruments associated with a specific genre"""
        query = """
            SELECT t.track_id, t.track_name, t.midi_channel, t.patch_number
            FROM tracks AS t
            JOIN genres AS g ON t.genre_id = g.genre_id
            WHERE g.genre_name = %s
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (genre_name,))
        return cursor.fetchall()
    
    # Import data for note/chord transitions (Profiles)
    def fetch_transitions(self, genre_name):
        """Fetches the Markov Chain data for the AI's decision-making"""
        query = """
            SELECT t.prev_note AS current_note, t.next_note, t.weight
            FROM transitions AS t
            JOIN genres AS g ON t.genre_id = g.genre_id
            WHERE g.genre_name = %s
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (genre_name,))
        return cursor.fetchall()
    
    # Import data for motifs (Note/chord sequences)
    def fetch_motifs(self, genre_name):
        """Fetches all curated motifs for the specified genre."""
        query = """
            SELECT m.motif_id, m.motif_name, m.sequence_data
            FROM motifs AS m
            JOIN artists AS a ON m.artist_id = a.artist_id
            JOIN genres AS g ON a.genre_id = g.genre_id
            WHERE g.genre_name = %s
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (genre_name,))
        return cursor.fetchall()
    
    # Import data for chord names and notes
    def fetch_chord_library(self):
        """Fetches the musical data of every chord type in the database"""
        query = """
            SELECT c.chord_name, cn.note_name
            FROM chords AS c
            JOIN chord_notes AS cn ON c.chord_id = cn.chord_id
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query) # Placeholders omitted from this query
        return cursor.fetchall()
    
    # Disconnects from SQL Server
    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("--- SUCCESS: Connection terminated safely ---")


class MusicEngine:
    """Converts raw SQL data into Music21 objects"""

    def __init__(self):
        """Initializes container for a musical composition"""
        self.score = stream.Score()
        self.parts = {} # Empty dictionary for active instrument tracks

    def initialize_tracks(self, track_rows):
        """Maps SQL rows to music21 Part objects."""
        # Designates a "Unique" grouping, to be filled with non-repetitive instrument channels
        unique_channels = set()

        for row in track_rows:
            new_part = stream.Part()    # Initialize the MIDI object for an instrument part
            name = row['track_name']    # Visual clarity to represent track names from database
            track_name = name.lower()   # "Clean" tuple data for indexing
            new_part.id = name          # Maps the current instrument name to the MIDI object

            instrument_channel = row['midi_channel'] # Visual clarity to represent MIDI channel numbers from database

            if "drums" in track_name:
                instrument_channel = 10 # Sets "Drums" MIDI channel to 10 (Per General MIDI Standard)

            elif instrument_channel == 10 and "drums" not in track_name:
                # Uses a fallback channel to stay in the range of 16 MIDI tracks using modulo logic to map MIDI channels 1-15 (Per General MIDI Standard)
                fallback = (row['track_id'] % 15) + 1
                instrument_channel = 11 if fallback == 10 else fallback
                print(f"--- WARNING: Moved {track_name} from Channel 10 to {instrument_channel} ---")
            
            # Notifies user that the MIDI track has overlapped
            if instrument_channel in unique_channels and "drums" not in track_name:
                print(f"--- {name} is sharing MIDI Channel {instrument_channel} ---")

            unique_channels.add(instrument_channel) # Adds MIDI channel value to "Unique" grouping

            # Map the MIDI Channel from SQL to the Part
            new_part.insert(0, instrument.Instrument(track_name))
            new_part.midiChannel = instrument_channel - 1 # Subtract by 1 to align with 0-indexed counting in Music21

            self.parts[track_name] = new_part
            self.score.insert(0, new_part)
            print(f"--- READY: Mapped {name} to Channel {instrument_channel} ---")

    def import_user_preferences(self, preferences):
        """Sets the Tempo and Metadata based on SQL 'Constitution'."""
        # BPM - Uses .get() with a fallback to 120 if the key is missing from SQL
        bpm = int(preferences.get('default_bpm', 120))
        self.score.insert(0, tempo.MetronomeMark(number=bpm))

        # Metadata - Engraves the composition title into the MIDI file headers
        self.score.metadata = metadata.Metadata()
        self.score.metadata.title = preferences.get('composition_title', 'Typebeat AI V7 Generated Score')

        print(f"--- Preferences: --- \n--- Default Tempo: {bpm} BPM | Title: {self.score.metadata.title} ---")

    def generate_sequence(self, track_name, transition_rows, preferences, steps=DEFAULT_STEPS):
        """Uses SQL Markov weights to generate a stochastic musical phrase."""
        if not transition_rows:
            print(f"---WARNING: {track_name} not found. Skipping. ---")
            return # Exit early to prevent crashes
        
        # Initialize an empty dict to group all designated "current notes" for the function to index
        transition_map = {}
        for r in transition_rows:
            curr = r['current_note']
            if curr not in transition_map:
                transition_map[curr] = []
            transition_map[curr].append(r)

        # Grabs default note settings from 'user_preferences' table to set first note of Markov Chain
        start_options = transition_map.get("START", [])

        # Applies default note settings from 'user_preferences' if availableto set the "START" note. Otherwise, use the local 'next' note if a 'START' note exists in the 'tracks' table
        if start_options:
            next_notes = [o['next_note'] for o in start_options]
            weights = [o['weight'] for o in start_options]
            current_state = random.choices(next_notes, weights=weights, k=1)[0]
        else:
            current_state = preferences.get('default_start_note', 'C4')
            print(f"---No selected START note for {track_name}. Using {current_state} as default ---")

        first_note = note.Note(current_state)       # Maps the first note (State created from SQL database 'START' note) to a MIDI object
        first_note.quarterLength = 1.0
        self.parts[track_name].append(first_note)   # Appends note to track data
        
        # Iterates through 'DEFAULT_STEPS' to map next_note states based on weighted probabilities
        for i in range(steps - 1):
            # Adds each row's current note, or r['current_note'] to list of options for potential next_note
            options = transition_map.get(current_state, [])          
            if not options:
                break # Exits loop if there are no values in options list
            
            next_notes = [o['next_note'] for o in options]  # Adds each row's next note per option available (Previous note)
            weights = [o['weight'] for o in options]        # Adds each row's note weighting per option available

            # Selects current note from a random outcome of 'next_note' choices, determined based on note weight probability
            # Extracts a single note (The first note) from the list returned by random.choices
            current_state = random.choices(next_notes, weights=weights, k=1)[0]

            new_note = note.Note(current_state)         # Maps the new note (State created from the previous note's path) to a MIDI object
            new_note.quarterLength = 1.0                # Set a default "Quarter Note" duration
            self.parts[track_name].append(new_note)     # Appends note to track data
    
        print(f"--- GENERATED: {len(self.parts[track_name])} steps for {track_name} ---")


# Filters any ineligible characters from filename input to prevent file system errors; allows only letters, numbers, dashes, underscores, and periods
def sanitize_filename(name):
    return re.sub(r'(?u)[^-\w.]', '', name)


# Saves the generated score to a MIDI file with a timestamped filename; includes error handling for file writing issues and unexpected exceptions
def save_version(score, save_name="typebeat"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")   # Generates a timestamp in the format YYYYMMDD_HHMMSS for iterative purposes
        filename = f"{sanitize_filename(save_name)}_{timestamp}.mid"    # Runs save file through sanitization function to ensure it's a valid filename; appends timestamp for versioning and uniqueness

        midi_file = midi.translate.streamToMidiFile(score)  # Translates Music21 score object to a MIDI file format
        midi_file.open(filename, 'wb')                      # Opens the MIDI file in binary write mode
        midi_file.write()                                   # Writes the MIDI data to the file
        midi_file.close()                                   # Closes the file to ensure data is saved properly and resources are released
        print(f"--- SUCCESS! Created {filename} ---")
    except IOError as write_error:
        print(f"--- ERROR: Could not write file. {write_error} ---") # Catches file writing errors such as permission issues, disk space problems, or invalid filenames
    except Exception as system_error:
        print(f"--- UNEXPECTED ERROR: {system_error} ---") # Catches any other unforeseen exceptions


# Track information overlay for user viewing
db = DatabaseManager()
preferences = db.fetch_user_preferences()           # Fetch set of user preferences from SQL database
pop_punk_tracks = db.fetch_track_data("Pop-Punk")   # Fetch data for current genre

engine = MusicEngine()
engine.import_user_preferences(preferences)
engine.initialize_tracks(pop_punk_tracks)

# References the dict 'self.parts' and lists the active instruments for user viewing
for track in engine.parts:
    print(f"--- {track} is now active in Typebeat. ---")

transitions = db.fetch_transitions("Pop-Punk")

# Generates notes and note sequences for each active instrument
for track_name in engine.parts:
    engine.generate_sequence(track_name, transitions, preferences)

# Main execution flow: Generates a simple 16-step pattern for piano, bass, and drums based on the defined GENRE_MAP; allows user input for filename and includes safety fallback
save_name = input("Save file as: ")
if not save_name:
    save_name = "typebeat_default" # Safety fallback if the user only types in symbols

# Stochastic loop goes here to generate steps of each part of the score
print("--- Finalizing Score Structure ---")

save_version(engine.score, save_name) # Saves generated score

db.close()