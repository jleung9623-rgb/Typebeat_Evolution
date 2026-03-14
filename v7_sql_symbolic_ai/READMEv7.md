# Typebeat Musical Governance AI V7 (A Symbolic Quality Control System) --- Completed on 02/28/2026

## **Quick Start**
### Install Dependencies
The engine requires **Python 3.8+** and a **MySQL** server. 

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd typebeat-ai-v7
   ```
2. **Install Core Libraries:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Create and Activate Virtual Environment:**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Configure Environment:**
    Create a .env file in the root directory:
    ```text
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_HOST=localhost
    DB_NAME=typebeat_ai_v7
    ```
5. **Run Engine:**
    Ensure the Master Schema is imported into MySQL before execution.
    ```python typebeat-v7.py```
6. **Output:** 

    * **Dynamic Music Engine**: Uses Music21 to generate note sequences from multiple instruments as MIDI objects.
    * **Sanitized Filenames**: Automatically filters illegal characters and timestamped to prevent overwrites.
    * **Protocol-Compliant Routing**: Implements a Guardrail for the **Percussion Channel (10)** to ensure newly appended instruments do not conflict with the dedicated 'Drums/Percussion' MIDI channel.
    * **SQL Server Integration**: Environment-driven access to a **MySQL** database that utilizes a .env configuration for database access across different local or server environments.

## Description
The Typebeat Musical Governance AI is a symbolic musical engine designed to generate musically coherent MIDI sequences across diverse genres using **stochastic logic** and state-based navigation. This Version 7.0 model can be used to condition other **Neuro-symbolic AI** or **Neural Networks** by filtering their learning material through my framework of musical "Laws" and regulations, thus providing a much clearer frame of reference when defining a certain type of "Song". By increasing the scalability of the previous model's logic mapped from a nested dictionary to a **MySQL database**, the program has now become an exponentially scalable platform for **Music Information Retrieval (MIR)** that ensures generated content undergoes a "Quality Control Audit" primed by a customizable matrix of genre-specific regulations while also adhering to MIDI 1.0 hardware protocols and **General MIDI (GM)** Standards.

## Design Decisions

* **MySQL Database Upscale**: Transitioned from a series of hard-coded dictionary storage containers to a relational MySQL database to expand the scalability of applicable musical data to streamline the process of appending new Markov Chains and metadata without modifying the core Python engine, becoming a dynamic platform.
* **Environment Isolation & Portability**: Implemented Virtual Environment (.venv) integration to ensure project-specific dependency management. This architectural choice prevents "Dependency Hell" (version conflicts) and guarantees bit-perfect reproducibility across different local or server environments. 
* **Hybrid Note Generation Processing Model**: Implemented a scalable "Pre-mapping" strategy for note generation at a O(n) computational speed for the `generate_sequence` function, requiring the filtering of SQL rows into designated groups before the stochastic logic of the Markov Chains are built using these rows at a constant iterative speed of O(1).
* **Modular Object-Oriented Design**: Minimizes conflict at a systemic level by segregating the SQL-side and musical initialization into two separate classes, where interaction between the two is solely limited to instances where I can set the terms, thus protecting the state of the composition.

## Edge Case Mitigation
Several automated guardrails have been implemented to ensure consistency with production-grade reliability in the program's current set of core features

* **MySQL Database Connection Failure**: Implements **Graceful Failure** for SQL connection errors, where the system audits a user's credentials via a .env check and provides a clear notification before a clean exit in error cases, preventing unhandled traceback crashes.
* **Hardware Conflict Resolution**: Melodic instruments assigned to the hardware-reserved **Percussion Channel (10)** are automatically re-routed using a **Modulo Fallback** logic to prevent auditory corruption.
* **Protocol Enforcement**: Monitors active MIDI tracks to ensure the system never exceeds the **16-channel hardware limit**, providing user notifications for channel overlaps.
* **Input Sanitization**: Implements **Regex-based filtering** and unique **timestamping** for all file exports to prevent OS-level filename errors and data overwrites.
* **Stochastic Dead-End Protection**: Includes automated breaks and **START note fallbacks** to prevent program crashes if the Markov Chain reaches an undefined musical state.
* **Key-Error Normalization**: Utilizes lowercase string normalization for internal dictionary lookups while preserving "Pretty Case" metadata for the final MIDI display.
* **User Preference Fallback Settings**: Applies a "Contingent default" fallback setting for keys missing from the 'user_preferences' table in the SQL database (e.g. setting a default BPM of 120, or a default composition title of 'Typebeat AI V7 Generated Score' using the `.get('key', default)` dictionary method).
* **Save File I/O Protection**: Implemented a guardrail to differentiate between writing errors (Permission issues, insufficient disk space, invalid filenames) and other unexpected system errors during the MIDI export phase.

#### Core Technologies

* **Music21**: Specialized toolkit for computer-aided musicology and MIDI object manipulation.
* **MySQL Connector**: High-performance driver for relational music data and Markov state persistence.
* **Python-Dotenv**: Manages environment-based configuration for modular database access.

### SQL Database Architecture
The engine is powered by a relational MySQL schema optimized for **stochastic memory persistence**.

* **Visual Schema**: [View Interactive ERD on dbdiagram.io](https://dbdiagram.io/d/Typebeat-7-0-69a48308a3f0aa31e172e557)

* **`genres`**: The defining registry of "Song Archetypes" containing default tempo, root notes, and scale associations.
* **`tracks`**: Hardware routing table mapping MIDI instruments and patch numbers to specific genres.
* **`transitions`**: The stochastic network that stores Markov state weights and rhythmic profiles.
* **`scales` / `chords` / `chord_notes`**: The musical foundation providing interval and harmonic structures.
* **`artists` / `motifs`**: High-level curated sequences and artist-specific style profiles.
* **`compositions`**: Table for generated scores, file paths, and session metadata.
* **`user_preferences`**: EAV-pattern table for session-persistent global configurations.

> **Architecture Note**: The `transitions` table is optimized with **composite indexing** (`idx_transition_lookup`) to ensure sub-millisecond query response times during the Markov walk.

#### **Changelog**

* **V7.0 (Current)**: Ported musical logic framework to a **Relational MySQL database**, complete with a foreign key-connected 10-table schema; implemented modular database access and virtual environments
* **V6.0**: Transitioned to **Music21 framework** for MIDI integration; enhanced scalability of Markov Chain management with a nested dictionary to achieve **O(1) lookup efficiency**
* **V5.0**: Implemented a basic AI model in a **stochastic engine** where **Markov Chains** were built on state-based navigation and previous/next note memory
* **V4.0**: Enhanced scalability of MIDI track data with a **linear data structure**, added more useability features
* **V3.0**: Implemented multi-track integration and the first iteration of **stochastic logic**, using states to create a sequence of notes
* **V2.0**: Migrated program to a professional Python framework using `midiutil` to convert generated notes into MIDI files
* **V1.0**: Created a chord generator display as a **C-Based final project for CS50x**

#### **Future Roadmap** 
* Implement .csv file uploads to streamline data inflow
* Add note context column into transitions table to support Markov Chains of a second-order or higher tier
* Implement Hierarchical Pitch Transposition, allowing for global (user-level) and local (track-level) octave offsets to enhance harmonic flexibility
* Implement naming schema for database [ROOT]_[CHORD_TYPE]_[OBJECT_TYPE]_[VERSION]
* Begin populating database to accommodate motif variations
* Expand routing registry for tracks table (To expand library of instruments, perhaps routing through a DAW)
* API integration for DAWs (Ableton, etc.)
* Add note velocity designation into 'transitions', 'motifs', 'chord_notes'
* Add Spatial Imaging to the Hardware Registry
* Add protocol for unit testing
* Heavier encryption ahead of a public-facing model
* Integrate 'AuthN' and 'AuthZ' into program
* Import NumPy, PyTorch libraries for neuro-symbolic transition