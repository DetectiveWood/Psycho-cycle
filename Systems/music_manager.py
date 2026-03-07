# -*- coding: utf-8 -*-
import pygame
import random

class MusicManager:
    def __init__(self):
        self.current_playlist = None
        self.current_track_index = 0
        self.track_start_time = 0
        self.min_track_duration = 20000  # 20 seconds minimum
        self.fade_duration = 2000  # 2 seconds fade
        self.is_fading = False
        self.fade_start_time = 0
        self.next_playlist = None
        self.volume = 0.3  # Background music volume

        # Music playlists - automatically load from directories
        self.playlists = self.load_music_playlists()

        # Ending music tracks
        self.ending_tracks = self.load_ending_music()

        # Try to load sounds, fallback to silence if files don't exist
        self.sounds_loaded = self.load_sounds()

        # Whisper system for paranoia effects
        self.whisper_sounds = self.load_whisper_sounds()
        self.last_whisper_time = 0
        self.whisper_finished_time = 0  # Track when last whisper finished
        self.whisper_cooldown = 20000  # 20 seconds minimum between whispers
        self.whisper_volume = 0.12  # Base whisper volume (slightly higher)

        # Fade-in system for music startup
        self.is_fading_in = False
        self.fade_in_start_time = 0
        self.fade_in_duration = 3000  # 3 seconds fade-in

    def load_music_playlists(self):
        """Automatically load music files from directories"""
        import os
        import glob

        playlists = {
            'normal': [],
            'tense': [],
            'paranoid': []
        }

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        for playlist_name in playlists.keys():
            playlist_dir = f'music/{playlist_name}'

            # Check if directory exists
            if os.path.exists(playlist_dir) and os.path.isdir(playlist_dir):
                # Scan for all supported audio files
                for extension in audio_extensions:
                    pattern = os.path.join(playlist_dir, extension)
                    files = glob.glob(pattern)
                    playlists[playlist_name].extend(files)

                # Sort files for consistent ordering
                playlists[playlist_name].sort()

                pass  # Playlist loaded successfully
            else:
                pass  # Directory not found

        # Fallback to empty lists if no files found
        if not any(playlists.values()):
            playlists = {
                'normal': ['silent'],
                'tense': ['silent'],
                'paranoid': ['silent']
            }

        return playlists

    def load_ending_music(self):
        """Load ending music tracks from music/end directory"""
        import os
        import glob

        ending_tracks = {
            'good': None,  # music/end/1.*
            'neutral': None,  # music/end/2.*
            'bad': None,  # music/end/3.*
            'perfect': None,  # music/end/4.*
            'breakthrough': None,  # music/end/5.*
            'control': None  # music/end/6.*
        }

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        end_dir = 'end'

        if os.path.exists(end_dir) and os.path.isdir(end_dir):
            # Look for specific numbered tracks
            track_mappings = {
                'good': '1',
                'neutral': '2',
                'bad': '3',
                'special_both': '4',
                'special_cats': '5',
                'special_doubt': '6'
            }

            for ending_type, track_number in track_mappings.items():
                for extension in audio_extensions:
                    pattern = os.path.join(end_dir, f"{track_number}.*")
                    files = glob.glob(pattern)
                    if files:
                        # Take the first matching file
                        ending_tracks[ending_type] = files[0]
                        break

        return ending_tracks

    def load_whisper_sounds(self):
        """Load whisper sound effects for paranoia system"""
        import os
        import glob

        whisper_sounds = []

        # Supported audio formats
        audio_extensions = ['*.ogg', '*.wav', '*.mp3', '*.flac', '*.aac']

        whisper_dir = 'whisper'

        # Check if whisper directory exists
        if os.path.exists(whisper_dir) and os.path.isdir(whisper_dir):
            # Scan for all supported audio files
            for extension in audio_extensions:
                pattern = os.path.join(whisper_dir, extension)
                files = glob.glob(pattern)
                whisper_sounds.extend(files)

            # Sort files for consistent ordering
            whisper_sounds.sort()

            pass  # Whisper sounds loaded successfully
        else:
            pass  # Directory not found

        # If no whisper sounds found, create empty list
        if not whisper_sounds:
            pass  # No whisper sounds found
            whisper_sounds = []

        return whisper_sounds

    def load_sounds(self):
        """Try to load sound files, return True if successful"""
        try:
            # Test loading one file from each playlist
            for playlist_name, tracks in self.playlists.items():
                if tracks and tracks[0] != 'silent':
                    # Try to load first track to test (skip 'silent' placeholder)
                    test_sound = pygame.mixer.Sound(tracks[0])
                    del test_sound  # Clean up test
            return True
        except (pygame.error, FileNotFoundError):
            # If sounds can't be loaded, create silent placeholders
            self.create_silent_placeholders()
            return False

    def create_silent_placeholders(self):
        """Create silent audio for when music files aren't available"""

        # Replace all tracks with silence
        for playlist_name in self.playlists:
            self.playlists[playlist_name] = ['silent']

    def get_target_playlist(self, stress, paranoia):
        """Determine which playlist should be playing based on mental state"""
        if paranoia >= 40:
            if stress >= 50:
                return 'paranoid'
            else:
                return 'tense'
        elif stress >= 40:
            return 'tense'
        else:
            return 'normal'

    def update(self, stress, paranoia):
        """Update music system based on current mental state"""
        if not self.sounds_loaded:
            return  # Skip if no sounds available

        # Don't update music during ending
        if self.current_playlist and self.current_playlist.startswith('ending_'):
            return  # Keep ending music playing without interruption

        current_time = pygame.time.get_ticks()
        target_playlist = self.get_target_playlist(stress, paranoia)

        # Check if we need to change playlist
        if target_playlist != self.current_playlist and not self.is_fading:
            # Only change if current track has played for minimum duration
            track_duration = current_time - self.track_start_time
            if track_duration >= self.min_track_duration or self.current_playlist is None:
                self.start_fade_to_playlist(target_playlist)

        # Handle fade-in from startup
        if self.is_fading_in:
            fade_in_progress = (current_time - self.fade_in_start_time) / self.fade_in_duration
            if fade_in_progress >= 1.0:
                # Fade-in complete
                self.is_fading_in = False
                pygame.mixer.music.set_volume(self.volume)
            else:
                # Apply fade-in effect (gradual volume increase)
                fade_in_volume = self.volume * fade_in_progress
                pygame.mixer.music.set_volume(fade_in_volume)

        # Handle regular fading (between playlists)
        elif self.is_fading:
            fade_progress = (current_time - self.fade_start_time) / self.fade_duration
            if fade_progress >= 1.0:
                # Fade complete, switch to new playlist
                self.complete_fade()
            else:
                # Apply fade effect
                fade_volume = self.volume * (1.0 - fade_progress)
                pygame.mixer.music.set_volume(fade_volume)

        # Check if current track finished and start next (don't interfere with fade-in)
        if not pygame.mixer.music.get_busy() and self.current_playlist and not self.is_fading and not self.is_fading_in:
            self.play_next_track()

        # Handle whisper system for paranoia
        self.update_whisper_system(paranoia, current_time)

    def start_fade_to_playlist(self, new_playlist):
        """Start fading current music to switch to new playlist"""
        self.is_fading = True
        self.fade_start_time = pygame.time.get_ticks()
        self.next_playlist = new_playlist

    def complete_fade(self):
        """Complete the fade transition and start new playlist"""
        self.is_fading = False
        self.current_playlist = self.next_playlist
        self.next_playlist = None

        # Start with random track instead of first track
        import random
        playlist = self.playlists[self.current_playlist]
        if playlist:
            self.current_track_index = random.randint(0, len(playlist) - 1)
        else:
            self.current_track_index = 0

        self.play_current_track()

    def play_current_track(self):
        """Play the current track in the current playlist"""
        if not self.sounds_loaded or not self.current_playlist:
            return

        playlist = self.playlists[self.current_playlist]
        if not playlist:
            return

        track_path = playlist[self.current_track_index]

        try:
            if track_path == 'silent':
                # For silent placeholder, just set a timer
                self.track_start_time = pygame.time.get_ticks()
                return

            pygame.mixer.music.load(track_path)
            # Set volume based on current fade state
            if self.is_fading_in:
                # During fade-in, volume will be controlled by update method
                pygame.mixer.music.set_volume(0)
            else:
                pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.track_start_time = pygame.time.get_ticks()

            # Track is now playing
            pass

        except (pygame.error, FileNotFoundError) as e:
            # Skip to next track if current one fails
            self.play_next_track()

    def play_next_track(self):
        """Move to next track in current playlist"""
        if not self.current_playlist:
            return

        playlist = self.playlists[self.current_playlist]
        self.current_track_index = (self.current_track_index + 1) % len(playlist)
        self.play_current_track()

    def start_playlist(self, playlist_name):
        """Start playing a specific playlist immediately"""
        if playlist_name in self.playlists:
            self.current_playlist = playlist_name
            self.is_fading = False

            # Start with random track instead of first track
            import random
            playlist = self.playlists[playlist_name]
            if playlist:
                self.current_track_index = random.randint(0, len(playlist) - 1)
            else:
                self.current_track_index = 0

            self.play_current_track()

    def start_fade_in(self):
        """Start fade-in effect for music at game startup"""
        self.is_fading_in = True
        self.fade_in_start_time = pygame.time.get_ticks()
        # Set initial volume to 0 for fade-in
        pygame.mixer.music.set_volume(0)

    def stop(self):
        """Stop all music"""
        pygame.mixer.music.stop()
        self.current_playlist = None
        self.is_fading = False

    def update_whisper_system(self, paranoia, current_time):
        """Handle whisper sound effects based on paranoia level"""
        if paranoia <= 30 or not self.whisper_sounds:
            return  # No whispers below 30% paranoia or if no sounds available

        # Calculate whisper frequency based on paranoia level
        # Higher paranoia = more frequent whispers
        # At 30% paranoia: 60 seconds, at 100% paranoia: 20 seconds
        max_interval = 60000  # 60 seconds at 30% paranoia
        min_interval = 20000  # 20 seconds at 100% paranoia
        paranoia_factor = (paranoia - 30) / 70  # 0.0 to 1.0 for paranoia 30-100
        whisper_interval = max_interval - (paranoia_factor * (max_interval - min_interval))

        # Check if enough time has passed since last whisper FINISHED
        # Use whisper_finished_time instead of last_whisper_time
        time_since_last_finished = current_time - self.whisper_finished_time
        if time_since_last_finished >= whisper_interval:
            # Random chance to play whisper (higher paranoia = higher chance)
            whisper_chance = 0.3 + (paranoia_factor * 0.4)  # 30% to 70% chance

            if random.random() < whisper_chance:
                self.play_whisper(paranoia)
                self.last_whisper_time = current_time

    def play_whisper(self, paranoia):
        """Play a random whisper sound with volume based on paranoia level"""
        if not self.whisper_sounds:
            return

        try:
            # Select random whisper sound
            whisper_file = random.choice(self.whisper_sounds)

            # Calculate volume based on paranoia (30-100 -> 0.08-0.25 volume)
            paranoia_factor = (paranoia - 30) / 70  # 0.0 to 1.0
            volume = 0.08 + (paranoia_factor * 0.17)  # 0.08 to 0.25 volume (slightly louder)

            # Load and play whisper on a separate channel
            whisper_sound = pygame.mixer.Sound(whisper_file)
            whisper_sound.set_volume(volume)

            # Play on any available channel
            channel = whisper_sound.play()

            # Set when this whisper will finish (estimate based on sound length)
            if channel:
                # Get sound length in milliseconds
                sound_length_ms = int(whisper_sound.get_length() * 1000)
                self.whisper_finished_time = pygame.time.get_ticks() + sound_length_ms
            else:
                # Fallback if channel info unavailable - assume 2 second whisper
                self.whisper_finished_time = pygame.time.get_ticks() + 2000

            # Whisper sound is playing
            pass

        except (pygame.error, FileNotFoundError) as e:
            # Error playing whisper sound
            pass

    def play_ending_music(self, ending_type):
        """Play ending music based on ending type"""
        if not self.sounds_loaded:
            return

        track_path = self.ending_tracks.get(ending_type)
        if not track_path:
            return  # No ending music found for this type

        try:
            # Stop current music and start ending track
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.volume * 1.2)  # Slightly louder for dramatic effect
            pygame.mixer.music.play(-1)  # Loop ending music indefinitely

            # Update current playlist to indicate ending music is playing
            self.current_playlist = f'ending_{ending_type}'
            self.is_fading = False
            self.is_fading_in = False

        except (pygame.error, FileNotFoundError):
            pass  # Silently fail if ending music can't be played

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        # Don't change volume immediately if we're in any fade state
        if not self.is_fading and not self.is_fading_in:
            pygame.mixer.music.set_volume(self.volume)
