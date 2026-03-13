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


def create_midi_chord(user_note, user_chord_type):
    # Collects user input from main
    root_note = NOTE_MAP.get(user_note.capitalize(), None)      # Sets the keynote
    intervals = CHORD_MAP.get(user_chord_type.lower(), None)    # Sets the chord type

    # Security check for empty inputs
    if root_note is None or intervals is None:
        print(f"Error: '{user_note}' or '{user_chord_type}' is not recognized")
        return False

    # Maps root note to Middle C (Middle C is 60) and applies interval offsets
    notes = [60 + root_note + i for i in intervals]

    # Note "Profile", or the musical information to be applied to a specific note

    track = 0       # Route to a MIDI instrument (Preset of time, duration, tempo, volume per instrument)
    channel = 0     # Route to an instrument type (0 is default for Acoustic Grand Piano)
    time = 0        # Offset starting point in beats
    duration = 2    # Length of time between offset and track completion in beats
    tempo = 120     # Pace of song in BPM (Beats per minute)
    volume = 100    # Must be value of 0-127

    # 
    MyMIDI = MIDIFile(1)                                    # Declare a MIDI object with 1 track
    MyMIDI.addTrackName(track, time, "Chord Engine 2.0")    # Sets placeholder name for DAW/MIDI player to read
    MyMIDI.addTempo(track, time, tempo)                     # Determines temporal information of track

    # Loop for adding in a MIDI object (Adds the "profile" for a note)
    for note in notes:
        MyMIDI.addNote(track, channel, note, time, duration, volume)

    # Creates and writes to new MIDI file
    try:
        filename = f"{user_note} {user_chord_type}.mid"
        with open(filename, "wb") as output_file:
            MyMIDI.writeFile(output_file)
        print(f"Success! Created {filename}")
        return True
    except IOError:
        sys.exit("System Error: Could not write file. Check permissions.")



# Main function that gets user input for a keynote and chord type
while True:
    print("\n--- MIDI Chord Generator ---")

    # Get user input for keynote
    user_note = input("Enter Note (e.g. C, F#, Bb) or 'exit': ")

    # Feature to exit the program
    if user_note.lower() == 'exit': break     

    # Get user input for chord type
    user_chord_type = input("Enter Chord Type (major, minor, dom7, , maj7, power): ")

    # Check for valid inputs in either field
    if create_midi_chord(user_note, user_chord_type):
        print("Chord generated successfully.")
    else:
        print("Please try again with valid inputs.")