"""
consts.py - Constants and configuration values for Launchpad95

This module centralizes all constant values used throughout the Launchpad95
control surface script. Organizing constants here improves maintainability
and makes it easier to adjust values without searching through multiple files.

Categories:
    - Button Colors: LED color configurations
    - MIDI Channels: Channel assignments per mode
    - Mode Indices: Numeric identifiers for each mode
    - Timing Constants: Button press durations
    - Quantization: Step sequencer quantization values
    - Velocity: Note velocity levels
"""

# =============================================================================
# BUTTON COLORS
# =============================================================================

ACTION_BUTTON_COLORS = dict(
    color='DefaultButton.Off',
    pressed_color='DefaultButton.On',
    disabled_color='DefaultButton.Disabled'
)

# =============================================================================
# MIDI CHANNELS
# =============================================================================

# Each mode uses specific MIDI channels for communication
MIDI_CHANNEL_SESSION = 0
MIDI_CHANNEL_DRUM_STEPSEQ = 1
MIDI_CHANNEL_MELODIC_STEPSEQ = 2
MIDI_CHANNEL_DEVICE = 3
MIDI_CHANNEL_USER1 = 4
MIDI_CHANNEL_USER2 = 5
MIDI_CHANNEL_MIXER_BASE = 6
MIDI_CHANNEL_MIXER_VOLUME = 7
MIDI_CHANNEL_MIXER_PAN = 8
MIDI_CHANNEL_MIXER_SEND_A = 9
MIDI_CHANNEL_MIXER_SEND_B = 10
MIDI_CHANNEL_INSTRUMENT_BASE = 11

# =============================================================================
# MODE INDICES
# =============================================================================

# Main mode indices (for mode buttons and switching)
MODE_SESSION = 0
MODE_USER1 = 1
MODE_USER2 = 2
MODE_MIXER = 3

# Sub-mode indices for User1 button
SUBMODE_INSTRUMENT = 0
SUBMODE_DEVICE = 1
SUBMODE_USER1_PLAIN = 2

# Sub-mode indices for User2 button
SUBMODE_DRUM_STEPSEQ = 0
SUBMODE_MELODIC_STEPSEQ = 1
SUBMODE_USER2_PLAIN = 2

# Step sequencer modes
STEPSEQ_MODE_NORMAL = 1
STEPSEQ_MODE_MULTINOTE = 2
STEPSEQ_MODE_SCALE_EDIT = 10

# Melodic step sequencer editing modes
MELODIC_MODE_NOTES = 1
MELODIC_MODE_NOTES_OCTAVES = 2
MELODIC_MODE_NOTES_VELOCITIES = 3
MELODIC_MODE_NOTES_LENGTHS = 4

# =============================================================================
# TIMING CONSTANTS (milliseconds)
# =============================================================================

# Button press duration thresholds
LONG_BUTTON_PRESS = 500        # Long press threshold (e.g., for redo, mute)
VERY_LONG_BUTTON_PRESS = 2000  # Very long press (e.g., implicit arm toggle)
DOUBLE_CLICK_TIME = 250        # Double-click detection window

# Display timing
PAGE_DISPLAY_TIME = 250        # Duration to show page indicator

# =============================================================================
# QUANTIZATION
# =============================================================================

# Quantization values in beats (1 = quarter note)
QUANTIZATION_MAP = [1.0, 0.5, 0.25, 0.125]  # 1/4, 1/8, 1/16, 1/32

# Display names for quantization levels
QUANTIZATION_NAMES = ["1/4", "1/8", "1/16", "1/32"]

# Number of quantization levels
NUM_QUANTIZATION_LEVELS = 4

# =============================================================================
# VELOCITY
# =============================================================================

# Velocity levels for step sequencer (5 levels)
VELOCITY_LEVELS = [20, 50, 80, 105, 127]

# Default velocity index (index 2 = velocity 80)
DEFAULT_VELOCITY_INDEX = 2

# Melodic sequencer velocity map (7 levels)
MELODIC_VELOCITY_MAP = [0, 30, 60, 80, 100, 115, 127]

# =============================================================================
# NOTE LENGTHS
# =============================================================================

# Note length values in steps for melodic sequencer
NOTE_LENGTH_MAP = [1, 2, 3, 4, 8, 16, 32]

# =============================================================================
# GRID DIMENSIONS
# =============================================================================

GRID_WIDTH = 8
GRID_HEIGHT = 8
NUM_MATRIX_BUTTONS = GRID_WIDTH * GRID_HEIGHT  # 64
NUM_TOP_BUTTONS = 8
NUM_SIDE_BUTTONS = 8
NUM_TOTAL_BUTTONS = NUM_MATRIX_BUTTONS + NUM_TOP_BUTTONS + NUM_SIDE_BUTTONS  # 80

# =============================================================================
# DEVICE CONTROLLER
# =============================================================================

# Number of device lock slots
NUM_DEVICE_LOCKS = 4

# Long press threshold for device lock (seconds)
DEVICE_LOCK_LONG_PRESS = 0.4

# =============================================================================
# OCTAVE RANGE
# =============================================================================

# Octave limits by mode
OCTAVE_MIN_MELODIC = -2
OCTAVE_MAX_MELODIC = 10
OCTAVE_MIN_DRUMRACK = 0
OCTAVE_MAX_DRUMRACK = 8

# Default octave
DEFAULT_OCTAVE = 3

# =============================================================================
# MIXER
# =============================================================================

# Volume slider value map (8 steps, 0.0 to 1.0)
VOLUME_MAP = [0.0, 0.142882, 0.302414, 0.4, 0.55, 0.7, 0.85, 1.0]

# Pan slider value map (8 steps, -1.0 to 1.0)
PAN_MAP = [-1.0, -0.634921, -0.31746, 0.0, 0.0, 0.31746, 0.634921, 1.0]

# Send slider value map (8 steps, 0.0 to 1.0)
SEND_MAP = [0.0, 0.103536, 0.164219, 0.238439, 0.343664, 0.55, 0.774942, 1.0]

# =============================================================================
# SCALE COMPONENT
# =============================================================================

# Quick scale preset indices
QUICK_SCALE_INDICES = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 18, 24]

# Minor mode indices for major/minor toggle
MINOR_MODES = [1, 13, 14]  # Natural, Harmonic, Melodic

# =============================================================================
# HARDWARE
# =============================================================================

# Novation vendor ID
VENDOR_ID_NOVATION = 4661

# USB product IDs (legacy, non RGB Launchpad family only)
PRODUCT_ID_LAUNCHPAD = 14
PRODUCT_ID_LAUNCHPAD_S = 32
PRODUCT_ID_LAUNCHPAD_MINI = 54
