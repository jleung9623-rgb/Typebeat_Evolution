import sys
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

VALID_TRACK_MODES = ["mono", "poly", "default"] # List of valid track modes for user input validation

# Function to add MIDI objects to the MIDI file based on user input and track profiles
def add_midi_object(MyMIDI, user_note, user_chord_type, offset, duration, user_mode):

    # Collects user input from their respective maps
    root_note = NOTE_MAP.get(user_note, None)      # Sets the keynote
    intervals = CHORD_MAP.get(user_chord_type, None)    # Sets the chord type

    # Security check for empty inputs
    if root_note is None or intervals is None:
        print(f"Error: '{user_note}' or '{user_chord_type}' is not recognized")
        return False

    # Adds MIDI objects to each track as musical data based on the "mode" (mono or poly) and "octave" shift specified in the profile
    for profile in TRACK_PROFILES:
        # Create a "Mode state" for each track based on if user selects mono/poly/default; if default, uses the mode specified in the track profile
        if user_mode != "default":
            object_mode = user_mode
        else:
            object_mode = profile["mode"]

        # Maps root notes based on Track Profile and MIDI object mode; applies intervals if chord (poly) mode is selected
        if object_mode == "mono":
            note = profile["octave"] + root_note
            MyMIDI.addNote(profile["track"], profile["channel"], note, offset, duration, profile["volume"])
        elif object_mode == "poly":
            chord_layer = [profile["octave"] + root_note + i for i in intervals]
            for note in chord_layer:
                MyMIDI.addNote(profile["track"], profile["channel"], note, offset, duration, profile["volume"])

    # Successful outcome that adds a chord
    return True


# Main function that gets user input for a keynote and chord type
def main():

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

    # Ask user for inputs regarding the keynote, chord type, chord duration, and rest duration. Loop continues until user type "save" to save the file and exit.
    while True:
        # Sets default song offset to 0, but allows user to select a custom offset
        user_offset = input(f"\n--- Current Offset: {offset} ---\nEnter new beat or press Enter to keep current: ")
        if user_offset:
            try:
                offset = float(user_offset)
            except ValueError:
                print("Invalid input! Please enter a number for the offset (e.g., 0, 4.5)")
                continue # Restarts loop if user offset input is invalid

        # If user types "save", exits loop early and goes to teardown phase to save file and exit program
        user_note = input("\nNote (or 'save'): ").capitalize()
        if user_note == 'Save':
            break

        # Validates user input for note
        if user_note.capitalize() not in NOTE_MAP:
            print(f"Error: '{user_note}' is not a valid note. Please enter a note from the chromatic scale (e.g. C, D#, Eb).")
            continue # Restarts loop if user note input is invalid

        user_mode = input("\nMode (mono/poly/default): ").lower() or "default"

        # Validates user input for track mode
        if user_mode not in VALID_TRACK_MODES:
            print(f"Error: '{user_mode}' is not a valid mode. Please enter one of the following: {', '.join(VALID_TRACK_MODES)}.")
            continue # Restarts loop if user mode input is invalid
        
        skip_chord_prompt = False # State variable to determine whether to skip chord prompt (If user selects mono mode, chord type is irrelevant and will be set to "major" by default)

        # Hides prompt for chord type if user types in "mono" or "default", or if the user presses Enter
        if user_mode == "mono":
            skip_chord_prompt = True
        elif user_mode == "default" and TRACK_PROFILES[0]["mode"] == "mono":
            skip_chord_prompt = True

        user_chord_type = "major" # Default chord type is "major" if user doesn't specify a chord type
        if not skip_chord_prompt:
            user_chord_type = input("\nChord Type (major/minor/power/dom7/maj7): ").lower() or "major" # Asks for chord type if user selects "poly"
        
        # Validates user input for chord type
        if user_chord_type not in CHORD_MAP:
            print(f"Error: '{user_chord_type}' is not a valid chord type. Please enter one of the following: {', '.join(CHORD_MAP.keys())}.")
            continue # Restarts loop if user chord input is invalid

        try:
            duration = float(input("\nChord length (e.g. 2, 4): ") or 4.0)
            rest = float(input("\nBeats until next chord (e.g. 2, 4): ") or 4.0)
        except ValueError:
            print("Invalid input! Please enter numbers for length and rest (e.g., 2, 4.5)")
            continue # Restarts loop if user input is invalid

        # Check for valid inputs in either field
        if add_midi_object(MyMIDI, user_note, user_chord_type, offset, duration, user_mode):
            offset += rest # Moves the "cursor" forward 4 beats

    # Teardown Phase (Save and exit)
    try:
        with open("my_song.mid", "wb") as new_song:
            MyMIDI.writeFile(new_song)
        print("Success! File saved.")
    except IOError:
        sys.exit("Error: Could not save.")

if __name__ == "__main__":
    main()