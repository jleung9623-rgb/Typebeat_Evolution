#include <cs50.h> // Use of cs50 tools (If needed!)
#include <stdio.h> // For printf, fgets, stdin
#include <stdlib.h> // For malloc, free
#include <string.h> // For strcspn
#include <strings.h> // For strcasecmp

// Step 1. Define global "map" for each musical note
const char *map[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

// Step 2. Define a structure for a chord
typedef struct {
    char *name;
    int *notes;
    int num_notes;
} Chord;

Chord new_chord(int root_index, int intervals[], int count);

// Step 3. Execute program to display chords associated with a note
int main(void) {

    // Create buffer for 10 characters in user input
    char input[10];
    // Prompt user to enter a note
    printf("Enter a note: ");
    // Point towards user input and reads the data from whatever the keyboard presses
    fgets(input, sizeof(input), stdin);
    // Remove the trailing newline to allow string matching to function
    input[strcspn(input, "\n")] = 0;

    // Find corresponding index of note from the map array
    int root_index = -1;
    for (int i = 0; i < 12; i++)
    {
        // If user's note matches a value in the map, set its index
        if (strcasecmp(input, map[i]) == 0) {
            root_index = i;
            break;
        }
    }

    // Check for invalid user input
    if (root_index == -1) {
        printf("Invalid note!\n");
        return 1;
    }

    // Set intervals for basic triad and dominant 7th chords of any note
    int maj_f[] = {0, 4, 7};
    int min_f[] = {0, 3, 7};
    int d7_f[] = {0, 4, 7, 10};

    // Build their "chord profiles" using the struct "Chord"
    Chord major_triad = new_chord(root_index, maj_f, 3);
    Chord minor_triad = new_chord(root_index, min_f, 3);
    Chord dominant_7th = new_chord(root_index, d7_f, 4);

    // Displays the notes of each chord type for the designated input
    printf("\nMajor Chord: ");
    for (int i = 0; i < major_triad.num_notes; i++)
    {
        printf("%s ", map[major_triad.notes[i]]);
    } 
    printf("\n");

    printf("Minor Chord: ");
    for (int i = 0; i < minor_triad.num_notes; i++)
    {
        printf("%s ", map[minor_triad.notes[i]]);
    } 
    printf("\n");

    printf("Dominant 7th Chord: ");
    for (int i = 0; i < dominant_7th.num_notes; i++)
    {
        printf("%s ", map[dominant_7th.notes[i]]);
    }
    printf("\n\n");

    // De-allocate each instance of memory allocation to prevent leaks
    free(major_triad.notes);
    free(minor_triad.notes);
    free(dominant_7th.notes);

    // Returns successful outcome
    return 0;
}

// Helper Function: Create dynamic function to hold 3-4 note chords
Chord new_chord(int root_index, int intervals[], int count) {
    Chord new_chord;
    new_chord.num_notes = count;

    // Allocate memory based on exact number of notes in chord
    new_chord.notes = malloc(sizeof(int) * count);

    // Return if no note data found in new chord
    if (new_chord.notes == NULL) {
        return new_chord;
    }
    // Map new chord to our 12-note array
    else {
        // Loop through each note in chord
        for (int i = 0; i < count; i++) {
            // Map value of note = Found note + chord semitone intervals
            new_chord.notes[i] = (root_index + intervals[i]) % 12; 
        } // Modulo 12 is applied to limit note to the scope of our map
    }
    return new_chord;
}