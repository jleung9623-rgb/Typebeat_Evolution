# Typebeat AI Composer V6 (The Music21 Re-Model) --- Completed on 02/25/2026

## **Quick Start**
1. **Install Dependencies**: `pip install music21`
2. **Run Engine**: `python typebeat-v7.py`
3. **Output**: MIDI files are generated in the root directory with timestamped filenames.

## Description: Building off the previous Version 5.0 model, the concept of my basic musical AI was integrated into **Music21**. The main talking point of Version 6.0 is the move over to an industry-standard framework that streamlines and heavily improves upon the functionality of my previous engine. However, due to the "proof of concept" built and validated through all the previous versions, many of the core functions remained consistent and were simple to port over (Writing a MIDI file of notes generated using **Stochastic Navigation**, where the "Previous note" logs a state that determines the next note using a probabilistic outcome). What were known as the "Track Profiles" in Version 5.0 or the musical data pertaining to a designated instrument were now imported from Music21 using 'stream.Part()' and 'instrument.Instrument()', with the overall composition container imported using 'stream.Score()'. Furthermore, the basic MIDI object for a note was imported using 'note.Note()', so when the note data is retreived from the 'GENRE_MAP', the corresponding MIDI object from Music21 has already been initialized without the need for a hard-coded chromatic scale. A core function that was to be improved upon from the previous iteration was the ability to write dynamic save names, as the previous version only saved to one file repeatedly. Version 6.0 goes a step further, and "sanitizes" the user's input for the file name, removing all ineligble characters using a regular expression. Another important function added in this iteration was track-specific (Or "Part-specific" in 6.0) generated note sequences. The 'GENRE_MAP' has been transformed into a nested dictionary where each genre is broken down into their respective part, which now has their own unique mappings. Finally, the previous 'add_midi_object' function has now become 'generate_step', with the term "step" now referencing a traditional "beat" in a musical composition, as the function itself was coded to only generate quarter notes for now to reduce hard-coded inefficiency ahead of the 7.0 SQL integration. 

## Design Decisions: One of the main things to note is the lack of chord integration, despite their inclusion in the program's dependencies. This decision was made to future-proof a function of the AI that will be inevitable once SQL is integration. While the 'create_musical_part' function was also added in this version, it merely runs to create the tracks that were hard-coded into the program (Piano, bass, drums). The ability to add more tracks based on user input will again be added once SQL is integrated. At this time, however, hard-coding chords into the 'GENRE_MAP' would exponentially increase the complexity of the nested dictionary itself, whereas the data itself can be easily traced and weaved into a progression once the corresponding information is sorted into interconnected tables. In terms of the **Regex** logic used to filter characters in the file name, the raw string designation ('r) is used to encapsulate the '\w' within the pattern of the regular expression, which is then used to only allow '-' characters and word characters ('\w') into a user's input for the file name. 'datetime' was added as a core dependency as a way to not only accommodate multiple save files, but to differentiate them and log the time and date ('timestamp') the user saved the file to allow for chronological organization. For the drum part in particular, I kept the note transition simple for the prototyping phase, where it will generate a "kick" note on even beats, and a "snare" note on odd beats. Finally, the decision was made to set a global variable for DEFAULT_SONG_LENGTH, as I wanted visual clarity in case I wanted to test varying composition lengths.

## Other Details: Specific error paths were designated in the 'save_version' function to differentiate between file writing errors ('IOError') caused by issues like user permissions, insufficient disk space, or invalid file names and other unexpected errors ('Exception'). The 'create_musical_part' crucially implements logic pertaining to the drums instrument, where in accordance to the **General MIDI (GM) Standard**, the channel designation count of 10 (9 in Python) is strictly reserved for drums and percussion, hence the decision to skip MIDI channel 9 when appending a musical part to the list for any non-drum instrument.

### **Changes (Version 6.0)**

#### **Hardware & MIDI**
* Added `create_musical_part` function to automate track initialization.
* Designated specific audio channel (9) for drum-class instruments.

#### **Core Architecture**
* Set `DEFAULT_SONG_LENGTH` constant (16 steps).
* Initialized `Music21` score object and multi-track parts (Piano, Bass, Drums).
* Developed separate stochastic sub-maps for each musical part within the `GENRE_MAP`.
* Implemented state-logging for note sequences using stochastic navigation.

#### **IO & Security**
* Implemented Regex-based sanitization function (`sanitize_filename`) to filter illegal characters from filenames.
* Added `save_version` function with timestamping and error handling.
* Integrated user input for custom, sanitized file naming.

#### ** Next Steps (Version 7.0): **
* SQL Database Integration
* Note Transposition
* Note Rest and Duration Functionality
* Development of genre motifs (Note Progressions)
* Cyclical Markov Chains (Entropy reduction, recursive motifs)
* Reinforcement learning
* Micro Offsets (A.K.A "Human Timing")
* Implement "Save as" functionality

#### Dependencies: re, random, datetime, music21
#### Music21 Dependencies: stream, note, chord, instrument, interval, metadata, midi