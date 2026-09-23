import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write

# ---------------------------------------
# LFM WAVEFORM GENERATOR
# ---------------------------------------

print("===================================")
print("       LFM WAVEFORM GENERATOR")
print("===================================")

# ---------------------------------------
# STEP 1 — LFM PARAMETERS
# ---------------------------------------

f0 = float(input("Enter starting frequency (Hz): "))
BW = float(input("Enter bandwidth (Hz): "))
T = float(input("Enter chirp duration (seconds): "))
A = float(input("Enter amplitude (0 to 1): "))
fs = float(input("Enter sampling frequency (Hz): "))

# ---------------------------------------
# INPUT VALIDATION
# ---------------------------------------

if f0 <= 0:
    print("Error: Starting frequency must be greater than 0.")
    exit()

if BW <= 0:
    print("Error: Bandwidth must be greater than 0.")
    exit()

if T <= 0:
    print("Error: Chirp duration must be greater than 0.")
    exit()

if A < 0 or A > 1:
    print("Error: Amplitude must be between 0 and 1.")
    exit()

# Highest frequency in the chirp
f_max = f0 + BW

# Nyquist check
if fs <= 2 * f_max:
    print("\nError: Sampling frequency is too low.")
    print("Highest chirp frequency :", f_max, "Hz")
    print("Minimum required fs     :", 2 * f_max, "Hz")
    exit()

# ---------------------------------------
# CHIRP RATE
# ---------------------------------------

k = BW / T

# ---------------------------------------
# DISPLAY PARAMETERS
# ---------------------------------------

print("\nLFM Parameters")
print("-----------------------------------")
print("Starting Frequency :", f0, "Hz")
print("Ending Frequency   :", f_max, "Hz")
print("Bandwidth          :", BW, "Hz")
print("Duration           :", T, "seconds")
print("Amplitude          :", A)
print("Sampling Frequency :", fs, "Hz")
print("Chirp Rate         :", k, "Hz/s")

# ---------------------------------------
# STEP 2 — DISCRETE TIME ARRAY
# ---------------------------------------

num_samples = int(fs * T)

if num_samples < 2:
    print("Error: Not enough samples. Increase duration or sampling frequency.")
    exit()

t = np.arange(num_samples) / fs

print("\nSampling Information")
print("-----------------------------------")
print("Number of Samples :", num_samples)
print("First Time Value  :", t[0], "seconds")
print("Last Time Value   :", t[-1], "seconds")

# ---------------------------------------
# STEP 3 — LFM WAVEFORM GENERATION
# ---------------------------------------

waveform = A * np.sin(
    2 * np.pi * (
        f0 * t +
        0.5 * k * t**2
    )
)

print("\nLFM Waveform Generated")
print("-----------------------------------")
print("Number of Samples :", len(waveform))
print("Maximum Amplitude :", np.max(waveform))
print("Minimum Amplitude :", np.min(waveform))

# ---------------------------------------
# ESP32 DAC BUFFER CONVERSION
# ---------------------------------------

dac_waveform = np.uint8(
    np.clip((waveform + 1) * 127.5, 0, 255)
)

print("\nESP32 DAC Buffer")
print("-----------------------------------")
print("Buffer Size :", len(dac_waveform))
print("Minimum     :", np.min(dac_waveform))
print("Maximum     :", np.max(dac_waveform))

# ---------------------------------------
# EXPORT ESP32 WAVEFORM BUFFER
# ---------------------------------------

with open("waveform_buffer.h", "w") as file:

    file.write("#ifndef WAVEFORM_BUFFER_H\n")
    file.write("#define WAVEFORM_BUFFER_H\n\n")

    file.write("#include <stdint.h>\n\n")

    file.write(f"const uint16_t WAVEFORM_SIZE = {len(dac_waveform)};\n\n")

    file.write("const uint8_t waveform_buffer[] = {\n")

    for i in range(0, len(dac_waveform), 16):
        values = dac_waveform[i:i + 16]
        file.write("    ")
        file.write(", ".join(map(str, values)))
        file.write(",\n")

    file.write("};\n\n")
    file.write("#endif\n")

print("\nESP32 waveform buffer exported!")
print("File: waveform_buffer.h")

# ---------------------------------------
# STEP 4 — TIME DOMAIN PLOT
# ---------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(t, waveform)

plt.title("LFM Chirp - Time Domain")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)

plt.show()

# ---------------------------------------
# STEP 4 — FFT
# ---------------------------------------

fft_result = np.fft.fft(waveform)

freq = np.fft.fftfreq(
    num_samples,
    1 / fs
)

fft_magnitude = np.abs(fft_result)

# Keep only positive frequencies
positive_freq = freq[:num_samples // 2]
positive_magnitude = fft_magnitude[:num_samples // 2]

# ---------------------------------------
# FFT PLOT
# ---------------------------------------

plt.figure(figsize=(10, 5))

plt.plot(
    positive_freq,
    positive_magnitude
)

plt.title("LFM Chirp - FFT")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

# Focus on the useful frequency region
plt.xlim(
    max(0, f0 - BW),
    f_max + BW
)

plt.show()

# ---------------------------------------
# STEP 5 — EXPORT WAVEFORM
# ---------------------------------------

waveform_16bit = np.int16(
    waveform * 32767
)

write(
    "lfm_chirp.wav",
    int(fs),
    waveform_16bit
)

# ---------------------------------------
# FINAL SUMMARY
# ---------------------------------------

print("\n===================================")
print("      LFM GENERATION COMPLETE")
print("===================================")

print("Frequency Sweep :", f0, "Hz ->", f_max, "Hz")
print("Bandwidth       :", BW, "Hz")
print("Duration        :", T, "seconds")
print("Chirp Rate      :", k, "Hz/s")
print("Samples         :", len(waveform))
print("Sampling Rate   :", fs, "Hz")

print("\nWaveform exported successfully!")
print("File: lfm_chirp.wav")

# ---------------------------------------
# VERIFY ESP32 WAVEFORM BUFFER
# ---------------------------------------

import re

with open("waveform_buffer.h", "r") as file:
    header_content = file.read()

# Extract waveform values from the C array
match = re.search(
    r"const uint8_t waveform_buffer\[\] = \{(.*?)\};",
    header_content,
    re.S
)

if match is None:
    print("\nError: waveform_buffer[] not found in header file.")
    exit()

header_values = [
    int(value)
    for value in re.findall(r"\d+", match.group(1))
]

# Compare Python buffer with C header buffer
python_values = dac_waveform.tolist()

if header_values == python_values:
    print("\nESP32 BUFFER VERIFICATION")
    print("-----------------------------------")
    print("Verification : PASSED")
    print("Samples      :", len(header_values))
    print("Data Match   : Python = Header")
else:
    print("\nESP32 BUFFER VERIFICATION")
    print("-----------------------------------")
    print("Verification : FAILED")
    print("Python Samples :", len(python_values))
    print("Header Samples :", len(header_values))