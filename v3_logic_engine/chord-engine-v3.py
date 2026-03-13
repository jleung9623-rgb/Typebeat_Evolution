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


def add_midi_chord(MyMIDI, user_note, user_chord_type, track, offset, duration):

    # Collects user input from their respective maps
    root_note = NOTE_MAP.get(user_note.capitalize(), None)      # Sets the keynote
    intervals = CHORD_MAP.get(user_chord_type.lower(), None)    # Sets the chord type

    # Security check for empty inputs
    if root_note is None or intervals is None:
        print(f"Error: '{user_note}' or '{user_chord_type}' is not recognized")
        return False
    
    # Note "Profile", or the musical information to be applied to a specific note

    treble_vol, bass_vol, chord_vol = 80, 115, 90       # Must be value of 0-127  
    treble_ch, bass_ch, chord_ch = 0, 1, 2              # Route to an instrument type (0 is default for Acoustic Grand Piano) 
    treble_track, bass_track, chord_track = 0, 1, 2     # Route to a track (0 is default for first track in MIDI file)        

    # Maps root notes to each layer (60 is MIDI note for Middle C, 36 is C2); applies interval offsets to chord layer
    treble_note = 60 + root_note
    bass_note = 36 + root_note
    chord_layer = [60 + root_note + i for i in intervals]

    # Adds a MIDI object as a single note for treble and bass layers
    MyMIDI.addNote(treble_track, treble_ch, treble_note, offset, duration, treble_vol)
    MyMIDI.addNote(bass_track, bass_ch, bass_note, offset, duration, bass_vol)

    # Loop for adding in a MIDI object as a chord (Adds the "profile" to each note in chord)
    for note in chord_layer:
        MyMIDI.addNote(chord_track, chord_ch, note, offset, duration, chord_vol)

    # Successful outcome that adds a chord
    return True



# Main function that gets user input for a keynote and chord type
def main():

    # Song "Profile" (Global information about the song that is applied to all notes in the track)

    track = 0           # Route to a MIDI instrument (Preset of time, duration, tempo, volume per instrument)
    offset = 0          # Offset starting point in beats
    tempo = 120         # Pace of song in BPM (Beats per minute)
    duration = 4.0      # Length of chord
    rest = 4.0          # Length of time between current offset and next chord

    MyMIDI = MIDIFile(1)                                                # Declare a MIDI object with 1 track
    MyMIDI.addTrackName(track, offset, "AI Progression Engine 3.0")     # Sets placeholder name for DAW/MIDI player to read
    MyMIDI.addTempo(track, offset, tempo)                               # Determines temporal information of track

    # Ask user for inputs regarding the keynote, chord type, chord duration, and rest duration. Loop continues until user type "save" to save the file and exit.
    while True:
        print(f"\n--- Beat: {offset} ---")
        user_note = input("Note (or 'save'): ")
        if user_note.lower() == 'save':
            break

        if user_note not in NOTE_MAP:
            print(f"Error: '{user_note}' is not a valid note. Please enter a note from the chromatic scale (e.g. C, D#, Eb).")
            continue # Restarts loop if user input is invalid

        user_chord_type = input("Chord Type: ")
        if user_chord_type not in CHORD_MAP:
            print(f"Error: '{user_chord_type}' is not a valid chord type. Please enter one of the following: {', '.join(CHORD_MAP.keys())}.")
            continue # Restarts loop if user input is invalid

        try:
            duration = float(input("Chord length (e.g. 2, 4): ") or 4.0)
            rest = float(input("Beats until next chord (e.g. 2, 4): ") or 4.0)
        except ValueError:
            print("Invalid input! Please enter numbers for length and rest (e.g., 2, 4.5)")
            continue # Restarts loop if user input is invalid

        
        # Check for valid inputs in either field
        if add_midi_chord(MyMIDI, user_note, user_chord_type, track, offset, duration):
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