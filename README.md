# Task 5 – Fingerprint (Shazam-like App)

## Overview  
The Fingerprint (Shazam-like App) is a desktop application designed to identify audio signals (songs, music, or vocals) by analyzing their unique features. It showcases advanced signal processing techniques like spectrogram analysis, feature extraction, and perceptual hashing to match and compare audio files. The app also features a user-friendly GUI for visualizing results and experimenting with audio blending.

---

## Features  

- **Repository Management**  
  - Shared repository for audio files (full song, music, vocals).  
  - Enforces standardized naming for file organization and retrieval.  

- **Spectrogram Analysis**  
  - Generates spectrograms for the first 30 seconds of each audio file.  
  - Creates separate spectrograms for the full song, vocals, and music components.  

- **Feature Extraction and Hashing**  
  - Extracts key audio features like frequency peaks and energy bands.  
  - Utilizes perceptual hashing to create compact fingerprints for efficient comparison.  

- **Similarity Matching**  
  - Compares a given query file against the repository to identify similar songs.  
  - Displays results in a sorted table with similarity indices.  

- **Audio Blending**  
  - Combines two audio files with a slider-controlled weighted average.  
  - Treats the blended file as a new query for similarity analysis.  

- **Graphical User Interface (GUI)**  
  - Interactive GUI for managing audio files, generating fingerprints, and performing similarity searches.  
  - Includes real-time visualization of similarity results and audio blending adjustments.  

---

## Code Design Principles  

### **Object-Oriented Programming (OOP)**  
 Encapsulation of functionality into separate classes for better maintainability.

### **Logging**  
 Comprehensive logging using Python's `logging` library to track application flow and debug issues.  

---

## Requirements  

- Python 3.x
- Required libraries: matplotlib, numpy, logging
 
---

## Getting Started  

1. **Clone the repository:**  
   ```bash
   git clone <repository_url>
   ```  

2. **Navigate to the project directory:**  
   ```bash
   cd fingerprint-app
   ```  

3. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```  

4. **Run the application:**  
   ```bash
   python main.py
   ```  

---

## Usage  

1. **Load Audio Files:**  
   - Place your audio files in the `data/` folder with proper naming conventions.  

2. **Generate Fingerprints:**  
   - Use the GUI to generate spectrograms and extract features for audio files.  

3. **Similarity Search:**  
   - Load a query file and search for the most similar songs in the repository.  

4. **Audio Blending:**  
   - Combine two audio files using the slider, then perform a similarity search on the blended file.  

---

## Contributors  

- **[Your Name]**  

---

## Acknowledgments  

- Inspired by applications like Shazam and foundational concepts in digital signal processing.  
- Special thanks to instructors and team members for guidance and collaboration.  
