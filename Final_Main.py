from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QSizePolicy, QApplication, 
                            QMainWindow, QRadioButton, QButtonGroup, QFileDialog, QTabWidget)
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import librosa.display
import sys
import os
from scipy.io import wavfile
import logging
import sounddevice as sd
from PIL import Image, ImageQt, ImageEnhance
from numpy.fft import ifft2, ifftshift
from scipy.fft import fft2, fftshift
# from mplwidget import spec_Widget
from PyQt5 import QtCore
from Features import  AudioFingerprint
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
# Configure logging
logging.basicConfig(
    filemode="a",
    filename="our_log.log",
    format="(%(asctime)s) | %(name)s| %(levelname)s | => %(message)s",
    level=logging.INFO
)

# Load the UI file
Ui_MainWindow, QtBaseClass = uic.loadUiType("First_UI.ui")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
                # Initialize variables
        self.isplay = False
        self.first_file = None
        self.second_file = None
        self.mixed_file = None
        self.played_sound = None
        self.paused_sound = None
        self.match_songs = [None]*6
        self.database_folder = "Data_base"


        self.fingerprinter = AudioFingerprint()

        self.First_Song_Weight.sliderReleased.connect(lambda :self.mix_files(self.first_file, self.second_file))

        self.second_song_Weight.sliderReleased.connect(lambda :self.mix_files(self.first_file, self.second_file))
        
        # Connect buttons
        self.Upload_File_1_btn.clicked.connect(lambda :self.browse_file(1))
        self.Upload_File_2_btn.clicked.connect(lambda :self.browse_file(2))
        
        self.Del_1.clicked.connect(lambda :self.Delete_file(1))
        self.Del_2.clicked.connect(lambda :self.Delete_file(2))


        self.First_Song_Weight.setValue(0)
        self.second_song_Weight.setValue(0)
        self.First_Song_Weight.setEnabled(False)
        self.second_song_Weight.setEnabled(False)

        self.play_signal_mixed.clicked.connect(lambda: self.play_sound('mixed'))
        self.play_signal_1.clicked.connect(lambda: self.play_sound('first'))
        self.play_signal_2.clicked.connect(lambda: self.play_sound('second'))
        self.play_icon=QIcon("icons/soundIcon.png") 
        self.pause_icon=QIcon("icons/resumeIcon.png") 
    

        # Connect output buttons
        for i in range(6):
            button_name = f"play_output_{i+1}"
            button = getattr(self, button_name)
            button.clicked.connect(lambda checked, idx=i: self.play_sound(f'output_{idx}'))


        
        # Initialize media player
        self.player = QMediaPlayer()
        self.player.stateChanged.connect(self.handle_state_changed)
        
        # Initialize spectrogram and fingerprint
        # self.Spec_Org_obj = spec_Widget()
        # self.setup_widget_layout(self.Spec_Org_obj, self.Spec_Org)
        # self.fingerprinter = AudioFingerprint()
        self.query_path = None
    
    # def setup_widget_layout(self, spec_widget, target_widget):
    #     """Setup the layout for spectrogram widgets"""
    #     if isinstance(target_widget, QWidget):
    #         layout = QVBoxLayout(target_widget)
    #         layout.addWidget(spec_widget)
    #         target_widget.setLayout(layout)
    
    def handle_state_changed(self, state):
        """Handle media player state changes"""
        if state == QMediaPlayer.StoppedState:
            self.played_sound = None
            self.paused_sound = None
        elif state == QMediaPlayer.PausedState:
            self.paused_sound = self.played_sound
            self.played_sound = None
    

   
    def browse_file(self,file):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Query Audio", "", "Audio Files (*.mp3 *.wav)")
        
        if not file_path:
            return

        if file==1:
            self.first_file=file_path        
            self.label_song_1.setText(f"{os.path.splitext(os.path.basename(file_path))[0]}")
            self.First_Song_Weight.setEnabled(True)
            self.First_Song_Weight.setValue(100)
        

        else:
            self.second_file=file_path
            self.label_song_2.setText(f"{os.path.splitext(os.path.basename(file_path))[0]}")
            self.second_song_Weight.setEnabled(True)
            self.second_song_Weight.setValue(100)
        self.player.stop()
        self.mixed_file = self.mix_files(self.first_file, self.second_file)
    


  

    def play_sound(self, source):
        """Handle sound playback with proper pause/resume functionality"""
        if self.first_file is None and self.second_file is None and not source.startswith('output_'):
            return
            
        # Get the corresponding button based on source
        button = None
        if source == 'mixed':
            button = self.play_signal_mixed
        elif source == 'first':
            button = self.play_signal_1
        elif source == 'second':
            button = self.play_signal_2
        elif source.startswith('output_'):
            idx = int(source.split('_')[1])
            button_name = f"play_output_{idx+1}"
            button = getattr(self, button_name)

        # Rest of file path determination code...
        file_path = None
        if source == 'mixed' and self.mixed_file:
            file_path = self.mixed_file
        elif source == 'first' and self.first_file:
            file_path = self.first_file
        elif source == 'second' and self.second_file:
            file_path = self.second_file
        elif source.startswith('output_'):
            idx = int(source.split('_')[1])
            if idx < len(self.match_songs) and self.match_songs[idx] is not None:
                file_path = os.path.join(self.database_folder, self.match_songs[idx])
        
        if not file_path or not os.path.exists(file_path):
            print(f"Invalid file path: {file_path}")
            return
            
        # Handle play/pause logic with icon updates
        if self.played_sound == source:
            # If the same source is currently playing, pause it
            print("Pausing current playback")
            self.player.pause()
            self.paused_sound = source
            self.played_sound = None
            if button:
                button.setIcon(self.play_icon)
            
        elif self.paused_sound == source:
            # If this source was paused, resume it
            print("Resuming paused playback")
            self.player.play()
            self.played_sound = source
            self.paused_sound = None
            if button:
                button.setIcon(self.pause_icon)
            
        else:
            # If it's a new source, stop current playback and start new one
            print(f"Starting new playback: {file_path}")
            # Reset icon for previously playing button if exists
            if self.played_sound:
                prev_button = self._get_button_for_source(self.played_sound)
                if prev_button:
                    prev_button.setIcon(self.play_icon)
                    
            self.player.stop()
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.player.play()
            self.played_sound = source
            self.paused_sound = None
            if button:
                button.setIcon(self.pause_icon)
                
        print(f"State after operation - Playing: {self.played_sound}, Paused: {self.paused_sound}")

    def _get_button_for_source(self, source):
        """Helper method to get button object for a given source"""
        if source == 'mixed':
            return self.play_signal_mixed
        elif source == 'first':
            return self.play_signal_1
        elif source == 'second':
            return self.play_signal_2
        elif source.startswith('output_'):
            idx = int(source.split('_')[1])
            button_name = f"play_output_{idx+1}"
            return getattr(self, button_name, None)
        return None

    def handle_state_changed(self, state):
        """Handle media player state changes"""
        # Get current source button using helper method
        current_button = self._get_button_for_source(self.played_sound) if self.played_sound else None

        if state == QMediaPlayer.StoppedState:
            print("Player stopped")
            self.played_sound = None
            self.paused_sound = None
            if current_button:
                current_button.setIcon(self.play_icon)
        elif state == QMediaPlayer.PausedState:
            print("Player paused")
            if current_button:
                current_button.setIcon(self.play_icon)
        elif state == QMediaPlayer.PlayingState:
            print("Player playing")
            if current_button:
                current_button.setIcon(self.pause_icon)



    def Delete_file(self, file):        
        if file==1 and self.first_file is not None:
            self.first_file=None 
            
            self.First_Song_Weight.setValue(0)  
            self.First_Song_Weight.setEnabled(False)    
            self.label_song_1.setText(f"Input_1")
            self.mixed_file = self.mix_files(self.first_file, self.second_file)
            self.player.stop()
        elif file==2 and self.second_file is not None:
            self.second_file=None
            self.second_song_Weight.setValue(0)
            self.second_song_Weight.setEnabled(False)  
            self.label_song_2.setText(f"Input_2")
            self.mixed_file = self.mix_files(self.first_file, self.second_file)
            self.player.stop()
        if self.first_file is None and self.second_file is None:
            # self.Spec_Org_obj.clear()

            self.player.stop()
            self.played_sound = None
            self.paused_sound = None
            self.Reset_prograssbars()
            return
        
        








    def find_similar_songs(self, path):
        """Find similar songs to the query audio using precomputed fingerprints."""
        if not path or not self.database_folder:
            return
                # Get list of songs and their fingerprints from the precomputed database
        songs = list(self.fingerprinter.features.keys())
        self.progress_calculations.setMaximum(len(songs)+2)
        self.progress_calculations.setValue(1)
        # Generate fingerprint for the query audio
        query_fingerprint = self.fingerprinter.generate_fingerprint(path)
        self.progress_calculations.setValue(2)
        print("The song Readed correctly ")
        if not query_fingerprint:
            print("Failed to generate query fingerprint.")
            return
        

        
        
        
        similarities = []
        for i, song in enumerate(songs):
            song_fingerprint = self.fingerprinter.features[song]
            if song_fingerprint:
                similarity = self.fingerprinter.compute_similarity(
                    query_fingerprint, song_fingerprint)
                similarities.append((song, similarity))
            self.progress_calculations.setValue(i + 3)
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Update UI with results
        for i, (song, similarity) in enumerate(similarities[:6]):
            self.match_songs[i]=song
            
            # self.label_10.setText(f"Matching :{os.path.splitext(os.path.basename(path))[0]}")
            progress_bar = getattr(self, f"progressBar_{i+1}", None)
            if progress_bar:
                progress_bar.setValue(int(similarity * 100))
            label = getattr(self, f"label_{i+1}", None)
            if label:
                label.setText(str(song))
        print(self.match_songs)

    
    def Reset_prograssbars(self):
        """Reset all progress bars and labels"""
        
        
        self.groupBox_3.setTitle(f"Matching : ")
        self.progress_calculations.setValue(0)
        self.match_songs = [None]*6
        for i in range(6):
            progress_bar = getattr(self, f"progressBar_{i+1}", None)
            if progress_bar:
                progress_bar.setValue(0)
            label = getattr(self, f"label_{i+1}", None)
            if label:
                label.setText(f"Song_{i+1}")
        # self.label_8.setText(f"Song_{8}")
    
    def mix_files(self, file1, file2):
        """Mix two audio files with weights from sliders"""
        # Read the two wav files
        if file1 is None and file2 is None :
            return 
        self.Reset_prograssbars()
        if file1 is None or file2 is None:
            file=file1 if file1 is not None  else file2
            self.find_similar_songs(file) 
            self.player.stop()
            return
        
        rate1, data1 = wavfile.read(file1)
        rate2, data2 = wavfile.read(file2)
        
        # Ensure the sampling rates match
        if rate1 != rate2:
            rate1 = min(rate1, rate2)
        
        # Ensure the data lengths match by trimming
        min_length = min(len(data1), len(data2))
        data1 = data1[:min_length]
        data2 = data2[:min_length]
        
        # Normalize the data
        if np.issubdtype(data1.dtype, np.integer):
            data1 = data1 / np.iinfo(data1.dtype).max
        if np.issubdtype(data2.dtype, np.integer):
            data2 = data2 / np.iinfo(data2.dtype).max
        
        # Get weights from sliders
        weight1 = self.First_Song_Weight.value()
        weight2 = self.second_song_Weight.value()
    
        if weight1 == 0:
            mixed_data = data2  # Use second song as-is
        elif weight2 == 0:
            mixed_data = data1  # Use first song as-is
        else:
            # Normal mixing when both weights are non-zero
            mixed_data = ((weight1/100) * data1 + (weight2/100) * data2)
            # Normalize only when actually mixing
            mixed_data = mixed_data / np.max(np.abs(mixed_data))
       
       
       
        # Convert to 16-bit integer
        mixed_data = np.int16(mixed_data * 32767)
        
        # Save mixed file
        output_path = 'output_mix.wav'
        if os.path.exists(output_path):
            os.remove(output_path)
        wavfile.write(output_path, rate1, mixed_data)
        print(f"first_one : {file1}")
        print(f"first_two : {file2}")
        print("new mixxx")
        self.Reset_prograssbars()
        self.find_similar_songs(output_path)
        return output_path
 


if __name__ == "__main__":
    logging.info("----------------------the user open the app-------------------------------------")
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())