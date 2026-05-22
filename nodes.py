"""
ii | nodes.py — Visual Automation Graph
Edit this file. ii.py hot-reloads it automatically.

Available nodes: Const, LFO, BeatLFO, Seq, Ramp, Noise, BeatPulse,
                 AudioLevel, AudioPeak, AudioTrigger,
                 CameraMotion, CameraBrightness, CameraPresence,
                 Math, Clamp, Mix, Select, Hold, Scale, Gate,
                 Out, IntOut, BoolOut, ArtNetOut, ArtNetRGB
"""
from node_lib import *

# Hardware sources.
#
# /dev/video4 is intended for the Insta360 or main audience camera.
# /dev/video2 is intended for a second interactive camera.
# If OpenCV/sounddevice are missing or a source is offline, these nodes return 0.

MIC_LEVEL = AudioLevel(gain=9.0, smoothing=0.78)
MIC_PEAK = AudioPeak(gain=11.0)
MIC_KICK = AudioTrigger(threshold=0.50, cooldown=5, gain=11.0)

CAM_MAIN_MOTION = CameraMotion(source='/dev/video4', fps=15, gain=7.0, smoothing=0.70)
CAM_MAIN_BRIGHTNESS = CameraBrightness(source='/dev/video4', fps=10, smoothing=0.80)
CAM_MAIN_PRESENCE = CameraPresence(source='/dev/video4', fps=8)

CAM_SIDE_MOTION = CameraMotion(source='/dev/video2', fps=15, gain=7.0, smoothing=0.70)
CAM_SIDE_BRIGHTNESS = CameraBrightness(source='/dev/video2', fps=10, smoothing=0.80)
CAM_SIDE_PRESENCE = CameraPresence(source='/dev/video2', fps=8)

GRAPH = [

    # ── Clock ────────────────────────────────────────────────────────────────
    Out('bpm',      Const(140)),
    BoolOut('bpm_sync', Const(1)),

    # ── Source monitors visible in ii.py ─────────────────────────────────────
    Out('audio_level', MIC_LEVEL),
    Out('audio_peak', MIC_PEAK),
    Out('camera4_motion', CAM_MAIN_MOTION),
    Out('camera4_brightness', CAM_MAIN_BRIGHTNESS),
    BoolOut('camera4_online', CAM_MAIN_PRESENCE),
    Out('camera2_motion', CAM_SIDE_MOTION),
    Out('camera2_brightness', CAM_SIDE_BRIGHTNESS),
    BoolOut('camera2_online', CAM_SIDE_PRESENCE),

    # ── Mode flow: MUTATION 2 — dark techno sequence with EYE ────────────────
    IntOut('mode',    Seq([13, 7, 22, 2, 9, 8, 17, 16, 15, 7], beats=8)),
    IntOut('mode_b',  Select([Const(2), Const(13), Const(15), Const(16)], Scale(CAM_SIDE_MOTION, out_min=0, out_max=3.99))),

    # ── Palette: BLOOD + EMBER dominant, DEEP and VOID for depth ─────────────
    IntOut('palette', Mix(Seq([6, 6, 7, 6, 5, 6, 7, 2], beats=32), Scale(CAM_MAIN_BRIGHTNESS, out_min=5, out_max=7), CAM_MAIN_PRESENCE)),

    # ── Visual energy ─────────────────────────────────────────────────────────
    Out('wave_amplitude',   Mix(LFO(freq=0.18, shape='sin', min=0.20, max=0.48), Scale(MIC_LEVEL, out_min=0.22, out_max=0.50), 0.55)),
    Out('glitch_intensity', Mix(LFO(freq=0.07, shape='square', min=0.15, max=0.75), Scale(CAM_MAIN_MOTION, out_min=0.15, out_max=1.00), 0.70)),
    Out('rain_density',     Mix(LFO(freq=0.11, shape='tri', min=0.40, max=0.95), Scale(MIC_PEAK, out_min=0.45, out_max=1.00), 0.50)),
    Out('frame_delay',      Mix(LFO(freq=0.04, shape='sin', min=0.030, max=0.060), Scale(MIC_LEVEL, out_min=0.018, out_max=0.050), 0.40)),
    Out('strobe_speed',     BeatLFO(beats=2, shape='saw', min=2, max=8)),

    # ── Live switches from sources ───────────────────────────────────────────
    BoolOut('flash_active', MIC_KICK),
    BoolOut('layer_b_enabled', Mix(MIC_LEVEL, CAM_SIDE_MOTION, 0.5), threshold=0.20),

    # ── Art-Net examples. Set enabled=True and host to your Art-Net node/IP.
    # ArtNetOut(1, Scale(MIC_LEVEL, out_min=0, out_max=255), host='2.0.0.10', universe=0, enabled=True),
    # ArtNetRGB(1, MIC_LEVEL, CAM_MAIN_MOTION, CAM_SIDE_MOTION, host='2.0.0.10', universe=0, enabled=True),

]

# ─────────────────────────────────────────────────────────────────────────────
# Examples (uncomment to use):
#
# Override a single mode manually:
#   IntOut('mode', Const(7)),          # lock to TUNNEL
#
# Random palette every 4 beats:
#   IntOut('palette', Seq([0,1,2,3,4,5], beats=4)),
#
# Glitch ramps up over 16 seconds then resets:
#   Out('glitch_intensity', Ramp(seconds=16, loop=True)),
#
# Blackout fires on every 8th beat for 2 frames:
#   BoolOut('blackout', BeatPulse(div=8, hold=2)),
#
# Mix two speeds based on slow LFO:
#   Out('frame_delay', Mix(Const(0.03), Const(0.08), LFO(freq=0.05))),
#
# Hold a random mode until the next beat pulse:
#   IntOut('mode', Hold(Noise(every=0, min=0, max=16), BeatPulse(div=4))),
#
# Camera movement drives glitch amount:
#   Out('glitch_intensity', Scale(CameraMotion(source='/dev/video4', gain=7.0), out_min=0.05, out_max=1.0)),
#
# Dark/bright room shifts palette:
#   IntOut('palette', Scale(CameraBrightness(source='/dev/video2'), in_min=0.0, in_max=1.0, out_min=0, out_max=5)),
#
# Kick from microphone toggles flash overlay:
#   BoolOut('flash_active', AudioTrigger(threshold=0.55, cooldown=8, gain=10.0)),
#
# Mic energy feeds layer B and mode B:
#   BoolOut('layer_b_enabled', AudioLevel(gain=7.0), threshold=0.28),
#   IntOut('mode_b', Mix(Const(3), Const(13), AudioPeak(gain=9.0))),
#
# Send mic energy to DMX channel 1 over Art-Net:
#   ArtNetOut(1, AudioLevel(gain=8.0), host='2.0.0.10', universe=0, enabled=True),
# ─────────────────────────────────────────────────────────────────────────────
