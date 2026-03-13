import random
import re
import datetime
from music21 import stream, note, chord, instrument, interval, metadata, midi

DEFAULT_SONG_LENGTH = 16 # Defines the number of iterations for the main generation loop; can be adjusted for longer or shorter compositions

next_available_channel = 0 # Defines the next available MIDI channel for non-drum instruments

# Allows the manual assignment of instrument classes to MIDI channels; ensures drums have a dedicated channel slot
def create_musical_part(instrument_class):
    global next_available_channel

    # Checks if parameter instrument_class was of the drums class, maps it to MIDI channel 9 (Standard for drums/percussion)
    if isinstance(instrument_class, instrument.Percussion):
        instrument_class.midiChannel = 9
    else:
        if next_available_channel == 9: # Skips MIDI channel 9 for all non-drum instruments
            next_available_channel += 1

        instrument_class.midiChannel = next_available_channel # Maps a midi channel property from Music21 to the next available channel
        next_available_channel += 1 # Increases counter for next available channel slot

    return instrument_class

# Initialize the scores and parts of each instrument
score = stream.Score() # Container for the entire composition; holds all parts and metadata
score.metadata = metadata.Metadata(title='Typebeat AI v6.0 - Professional Refactor') # Initializes the "watermark" of the following composition, allows other systems to recognize a file generated from this specific engine

piano_part = stream.Part(id='Piano') # Initializes the track for a part
piano_part.insert(0, create_musical_part(instrument.Piano())) # Instrument mapping for a part (Includes MIDI channel and instrument route)

bass_part = stream.Part(id='Bass')
bass_part.insert(0, create_musical_part(instrument.ElectricBass()))

drum_part = stream.Part(id='Drums')
drum_part.insert(0, create_musical_part(instrument.Percussion()))

score.insert(0, piano_part) # Inserts the track into the score
score.insert(0, bass_part)
score.insert(0, drum_part)


# Keys: Current Note Name | Values: List of potential interval steps
GENRE_MAP = {
    'pop_punk': {
        'piano': {
            'C4': ['G4', 'F4', 'A4'],   # Still notes for now, but will eventually move to interval-based logic
            'G4': ['C4', 'A4'],         # Logic: The 'V' chord wants to resolve to 'I'
            'A4': ['F4', 'G4'],
            'F4': ['C4', 'G4']
        },
        'bass': {
            'C2': ['G2', 'F2'],         # Bass has its unique mapping
            'G2': ['C2', 'F2'],
            'F2': ['C2', 'G2'] 
        },
        'drums': {
            'kick':  ['C2'],            # Pattern mapping for drums
            'snare': ['D2']             
        }
    }
}


def generate_step(target_part, prev_note, genre, instrument_type):
    '''
    Performs a single stochastic iteration to determine the next note.
    Maps results to the target Music21 part and returns the next note for state tracking in the following iteration.
    '''
    # Retrieves the mapping for the specified genre and instrument type; if no mapping exists, defaults to C4 and logs a warning
    genre_data = GENRE_MAP.get(genre, {}) # Default to empty dict if genre not found, continues to next check
    if not genre_data:
        print(f"--- Warning: Genre {genre} not found. Defaulting to C4. ---")
        return 'C4' # Default note
    
    # Retrieves the mapping for the specified instrument type within the genre; if no mapping exists, defaults to C4 and logs a warning
    track_layer = genre_data.get(instrument_type, {})
    if not track_layer:
        print(f"--- Warning: Instrument type {instrument_type} not found in genre {genre}. Defaulting to C4. ---")
        return 'C4' # Default note

    note_choices = track_layer.get(prev_note, ['C4']) # Indexes the "track_layer" instrument within the designated genre for the value mapped to prev_note; default to C4 if no mapping exists

    next_note = random.choice(note_choices) # Picks a random note from the previous note's list of outcomes
    new_note = note.Note(next_note)         # Create Music21 note object and set duration
    new_note.quarterLength = 1.0            
    target_part.append(new_note)            # Append to track ("Full Stack Memory as it maps the data to target_part")

    return next_note # Update 'last_note' for next loop iteration


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


# Main execution flow: Generates a simple 16-step pattern for piano, bass, and drums based on the defined GENRE_MAP; allows user input for filename and includes safety fallback
save_name = input("Save file as: ")
if not save_name:
    save_name = "typebeat_default" # Safety fallback if the user only types in symbols

last_p_note = 'C4' # Default piano keynote
last_b_note = 'C2' # Default bass keynote

for count in range(DEFAULT_SONG_LENGTH):
    # Piano (Lead Track)
    last_p_note = generate_step(piano_part, last_p_note, 'pop_punk', 'piano')

    # Bass (Piano - 2 Octaves)
    last_b_note = generate_step(bass_part, last_b_note, 'pop_punk', 'bass')

    # Drums (Static pattern; kick on even, snare on odd)
    drum_note = 'C2' if count % 2 == 0 else 'D2'
    drum_part.append(note.Note(drum_note))

save_version(score, save_name) # Saves generated score