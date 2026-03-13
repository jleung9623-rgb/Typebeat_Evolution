import sys
import random
from midiutil import MIDIFile

# Map each note of chromatic scale from 1-11 (Including both sharps and flats)
NOTE_MAP = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4,
    "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11
}


# Root - The starting point of the chord, set by the keynote
# 3rd Note (Major/Minor) - The "Personality" note; sets the chord progression path
# Perfect 5th - Constant node for "standard" chords in western music, set at a 7-semitone interval
# 7th Note (Major/Minor) - The "Sophistication" note; adds an extra layer of sound to current chord
CHORD_MAP = {
    "major": [0, 4, 7],         # Root, Major 3rd, Perfect 5th (Happy motif)
    "minor": [0, 3, 7],         # Root, Minor 3rd, Perfect 5th (Sad motif)
    "power": [0, 7],            # Root, Perfect 5th (Adaptable chord)
    "dom7": [0, 4, 7, 10],      # Root, Major 3rd, Perfect 5th, Minor 7th (Blues motif)
    "maj7": [0, 4, 7, 11]       # Root, Major 3rd, Perfect 5th, Major 7th (Jazz motif)
}


# Track "Profile", or the musical information to be applied to a specific MIDI track (e.g. instrument, volume, octave shift, etc.)
TRACK_PROFILES = [
        {
            "name": "Piano",    # Instrument name for user reference (Not read by MIDI player)
            "track": 0,         # Route to a track (0 is default for first track in MIDI file)
            "channel": 0,       # Route to an instrument type (0 is default for Acoustic Grand Piano)
            "instrument": 0,    # MIDI instrument number (0-127, 0 is Acoustic Grand Piano)
            "volume": 85,       # Volume of track (0-127, 127 is loudest)
            "octave": 60,       # Octave shift for track, A.K.A the keynote or anchor pitch (60 is MIDI note for Middle C, 48 is C3, 36 is C2, etc.)
            "mode": "poly"      # "mono" for single notes, "poly" for chords (Multiple notes at same time)
        },
        {
            "name": "Bass",
            "track": 1,
            "channel": 1,
            "instrument": 33,   # 33 is Acoustic Bass in MIDI instrument list; can be changed to any other instrument number for different sound (e.g. 32 is Electric Bass (finger), 34 is Electric Bass (pick))#
            "volume": 115,
            "octave": 36,
            "mode": "mono"
        },
        {
            "name": "High Strings",
            "track": 2,
            "channel": 2,
            "instrument": 48,  # 48 is String Ensemble 1 in MIDI instrument list; can be changed to any other instrument number for different sound (e.g. 49 is String Ensemble 2, 50 is Synth Strings 1, 51 is Synth Strings 2)
            "volume": 90,
            "octave": 60,
            "mode": "poly"
        }
    ]


# Represents note progressions now as a series of outcomes determined with stochastic logic (Navigation of the different probabilities in each genre map)
GENRE_MAP = {
    "pop_punk": {
        # Note sequences based on the I-V-vi-IV "Golden Circle"
        "C":    ["G", "G", "F", "Am"],      # 50% chance of G, 25% F, 25% Am
        "G":    ["Am", "Am", "F", "C"],     # Strong pull to the Relative Minor
        "F":    ["C", "C", "G"],            # Resolution to the Tonic (Returns to home note) or pull to the Dominant
        "Am":   ["F", "F", "G"],            # Leading to the subdominant
        "D":    ["G"],                      # Secondary Dominant Logic
    },
    "jazz_blues": {
        #Transitions based on ii-v-I turnarounds
        "C":    ["Dm7", "Am7", "G7"],       # ii-V-I in C Major
        "Dm7":  ["G7", "G7", "Cmaj7"],      # ii-V-I in C Major
        "G7":   ["Cmaj7", "Cmaj7", "Am7"],  # V-I in C Major, with a pull to the Relative Minor
        "Am7":  ["Dm7", "D7"],              # ii-V in A Minor, leading to a potential resolution to Dm7 or a secondary dominant pull to G7
    }
}


# List of valid track modes for user input validation
VALID_TRACK_MODES = ["mono", "poly", "default"]

# The "Stateful Memory" (The Playhead of the Brain)
last_note = None            # Tracks the previous note played to direct the AI through the map
current_genre = "pop_punk"  # Can be changed by the user


# Function to add MIDI objects to the MIDI file based on user input and track profiles
def add_midi_object(MyMIDI, current_note, note_chord_type, offset, duration, note_mode):

    # Reads a note in the 
    pitch_key = current_note
    if len(current_note) > 1:
        if current_note[1] in ['#', 'b']:
            pitch_key = current_note[:2]
        else:
            pitch_key = current_note[0]

    # Collects user input from their respective maps
    root_note = NOTE_MAP.get(pitch_key, None)           # Sets the keynote
    intervals = CHORD_MAP.get(note_chord_type, None)    # Sets the chord type

    # Security check for empty inputs
    if root_note is None or intervals is None:
        print(f"Error: '{pitch_key}' or '{note_chord_type}' is not recognized")
        return False

    # Adds MIDI objects to each track as musical data based on the "mode" (mono or poly) and "octave" shift specified in the profile
    for profile in TRACK_PROFILES:
        # Create a "Mode state" for each track based on if user selects mono/poly/default; if default, uses the mode specified in the track profile
        if note_mode != "default":
            current_mode = note_mode
        else:
            current_mode = profile["mode"]

        # Maps root notes based on Track Profile and MIDI object mode; applies intervals if chord (poly) mode is selected
        if current_mode == "mono":
            note = profile["octave"] + root_note
            MyMIDI.addNote(profile["track"], profile["channel"], note, offset, duration, profile["volume"])
        elif current_mode == "poly":
            chord_layer = [profile["octave"] + root_note + i for i in intervals]
            for note in chord_layer:
                MyMIDI.addNote(profile["track"], profile["channel"], note, offset, duration, profile["volume"])

    # Successful outcome that adds a chord
    return True


# Main function that gets user input for a keynote and chord type
def main():

    # Global variables to track the last note played and the current genre for the AI to reference in its decision making process; allows the AI to have a "memory" of past events to create a more cohesive composition
    global last_note
    global current_genre

    MyMIDI = MIDIFile(len(TRACK_PROFILES))  # Declare a MIDI object relative to the number of tracks in TRACK_PROFILES

    # Song "Profile" (Global information about the song that is applied to all notes in the track)
    offset = float(input("\n--- Offset ---\nType new offset or press Enter to leave as 0: ") or 0.0)        # Offset starting point in beats
    duration = 4.0                                                                                          # Length of chord
    rest = 4.0                                                                                              # Length of time between current offset and next chord

    # Apply track profiles to program (e.g. set instrument, tempo, etc.)
    for profile in TRACK_PROFILES:
        tr = profile["track"]                                               # Route to a MIDI instrument (Preset of time, duration, tempo, volume per instrument)
        ch = profile["channel"]                                             # Route to an instrument type (0 is default for Acoustic Grand Piano)
        MyMIDI.addTrackName(tr, offset, profile["name"])                    # Sets placeholder name for DAW/MIDI player to read
        MyMIDI.addProgramChange(tr, ch, 0, profile["instrument"])           # Sets the MIDI instrument for the track based on the profile  (track, channel, offset, instrument)
        MyMIDI.addTempo(tr, 0, 120)                                         # Determines tempo of track (120 BPM is default, but can be changed to user input if desired, offset is also hard coded here to 0 to prevent redundancy in loop)

    # Asks user input for genre selection, which will determine the note progression paths for the AI to follow; defaults to "pop_punk" if user presses Enter or types an invalid genre
    print("\nAvailable Genres: " + ", ".join(GENRE_MAP.keys())) # Dynamically displays available genres using the GENRE_MAP dictionary keys
    choice = input("Select Genre (or press Enter for Pop/Punk): ").lower() or "pop_punk"
    if choice in GENRE_MAP:
        current_genre = choice

    # Ask user for inputs regarding the keynote, chord type, chord duration, and rest duration. Loop continues until user type "save" to save the file and exit.
    while True:
        # Sets default song offset to 0, but allows user to select a custom offset
        user_input = input(f"\n--- Current Offset: {offset} ---\nEnter new offset, press Enter to keep current, or type in 'save': ")
        if user_input == 'save':
            break
        if user_input:
            try:
                offset = float(user_input)
            except ValueError:
                print("Invalid input! Please enter a number for the offset (e.g., 0, 4.5)")
                continue # Restarts loop if user offset input is invalid

        # Checks if the last note played is in the genre map; if so, selects the next note in the progression based on probability
        if last_note in GENRE_MAP[current_genre]:
            current_note = random.choice(GENRE_MAP[current_genre][last_note])
        else:
            current_note = "C" # Default note if memory is empty or last note isn't in genre map

        # Prints the current note selected by the AI for user reference
        print(f"| AI COMPOSER | Current Note: {current_note}")

        # Default settings for AI (Will acommodate SQL database data in V6.0)
        note_mode = "default"
        note_chord_type = "major"

        # Check for valid inputs in either field
        if add_midi_object(MyMIDI, current_note, note_chord_type, offset, duration, note_mode):
            last_note = current_note    # Updates "Stateful Memory" with the last note played for AI advisor to reference in next suggestion
            offset += rest              # Moves the "cursor" forward 4 beats
        
    # Teardown Phase (Save and exit)
    try:
        with open("my_song.mid", "wb") as new_song:
            MyMIDI.writeFile(new_song)
        print("Success! File saved.")
    except IOError:
        sys.exit("Error: Could not save.")

if __name__ == "__main__":
    main()