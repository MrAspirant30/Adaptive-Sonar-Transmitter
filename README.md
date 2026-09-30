# AE-Sonar — Adaptive Energy-Aware Sonar Transmitter

> **Software-defined, adaptive waveform generation for resource-constrained Autonomous Underwater Vehicles (AUVs).**

AE-Sonar is a prototype software architecture for an **adaptive, energy-aware sonar transmitter** intended for autonomous underwater vehicles.

The system separates **transmission decision-making, DSP waveform generation, and embedded waveform delivery** into independent modules. Environmental and mission-state information is converted into a transmission strategy, which is then used to generate a parameterized **Linear Frequency Modulated (LFM) chirp** and prepare an embedded waveform buffer.

> **Current milestone: Software-verified adaptive waveform-generation pipeline + ESP32 firmware build.**

Physical acoustic transmission and underwater validation are planned for the next development phase.

---

## 1. Project Overview

Autonomous underwater vehicles operate under changing environmental and mission conditions while having limited onboard energy.

A fixed transmission configuration may not remain suitable across all operating conditions. AE-Sonar explores a software-defined approach in which the transmitter can select different waveform parameters according to the current operating state.

The project is built around three functional layers:

```text
┌──────────────────────────┐
│       ADAPTATION         │
│  Decides WHAT to transmit│
└────────────┬─────────────┘
             │
             │ f0, BW, T, A
             ▼
┌──────────────────────────┐
│           DSP            │
│ Generates & verifies LFM │
└────────────┬─────────────┘
             │
             │ 8-bit waveform
             ▼
┌──────────────────────────┐
│        EMBEDDED          │
│  Prepares waveform for   │
│      ESP32 delivery      │
└──────────────────────────┘
```

### Core principle

> **Transmit the minimum acoustic energy necessary for the required sensing objective.**

This is currently a **design objective**, not a measured energy-saving result.

---

## 2. System Architecture

The current software pipeline is:

```text
Environment / Mission State
            │
            ▼
     State Estimation
            │
            ▼
    Adaptation Engine
            │
            ▼
     Transmission Profile
       f0 | BW | T | A
            │
            ▼
    LFM Waveform Generator
            │
            ▼
      FFT Verification
            │
            ▼
    8-bit Waveform Buffer
            │
            ▼
       ESP32 Firmware
```

The architecture intentionally separates responsibilities:

| Layer      | Responsibility                                   |
| ---------- | ------------------------------------------------ |
| Adaptation | Selects the transmission strategy                |
| DSP        | Generates and verifies the waveform              |
| Embedded   | Prepares the waveform for deterministic delivery |

---

## 3. Adaptation Layer

The adaptation layer uses environmental and mission-state inputs to select a transmission profile.

The current prototype uses a deterministic rule-based approach rather than machine learning.

The prototype contains multiple predefined transmission profiles (**A1–A9**), each containing parameters such as:

* Starting frequency `f0`
* Bandwidth `BW`
* Chirp duration `T`
* Amplitude `A`
* Operating mode

The purpose of the profiles is to provide different transmission strategies for different operating states.

The exact decision thresholds and profile-selection rules are intentionally kept separate from the public project overview.

---

## 4. DSP Layer

Once the adaptation layer selects the transmission parameters, the DSP module generates an LFM chirp.

The waveform is represented as:

```text
s(t) = A sin(2π(f0t + ½kt²))
```

where:

```text
k = BW / T
```

and:

```text
fmax = f0 + BW
```

The waveform generator validates the input parameters before generating the signal.

### Sampling validation

The sampling frequency must satisfy the Nyquist condition:

```text
fs > 2 × fmax
```

This prevents an invalid digital representation of the selected waveform.

---

## 5. FFT Verification

The generated LFM waveform is analyzed using an FFT as a **software verification step**.

The FFT is used to inspect the frequency characteristics of the generated signal and verify that the waveform behaves consistently with the selected parameters.

This is computational verification.

It should **not** be interpreted as physical oscilloscope or acoustic measurement.

---

## 6. 8-bit Waveform Buffer

After waveform generation, the signal is converted into an **8-bit representation** suitable for embedded waveform delivery.

The generated data is exported into:

```text
waveform_buffer.h
```

The C header contains the waveform samples used by the ESP32 firmware.

The project also performs a **Python-to-C verification** to confirm that the waveform generated in Python corresponds to the waveform stored in the embedded C array.

---

## 7. ESP32 Firmware

The embedded portion of the project is implemented as a PlatformIO ESP32 project.

Current embedded stack:

```text
PlatformIO
    │
    ├── ESP32 DevKit
    ├── Arduino framework
    └── waveform_buffer.h
```

The firmware is designed around timer-driven waveform delivery and the classic ESP32 DAC output path.

The current firmware project has been successfully compiled.

### Important

Successful firmware compilation does **not** prove physical DAC output.

Physical DAC measurement using an oscilloscope remains part of the next validation phase.

---

## 8. Current Prototype Status

### Implemented

* [x] Deterministic adaptation algorithm
* [x] A1–A9 transmission profiles
* [x] Parameterized LFM waveform generation
* [x] Input validation
* [x] Nyquist validation
* [x] FFT-based software verification
* [x] 8-bit waveform buffer generation
* [x] Python-to-C waveform verification
* [x] ESP32 PlatformIO project
* [x] ESP32 firmware compilation

### Not Yet Physically Validated

* [ ] Physical ADC input
* [ ] Physical DAC output
* [ ] Oscilloscope measurement
* [ ] Analog filtering/amplification
* [ ] Acoustic transducer
* [ ] Underwater acoustic transmission
* [ ] Measured energy consumption/savings

Therefore, the current project should be considered a:

> **Software-verified prototype, not a physically validated underwater sonar transmitter.**

---

## 9. Sampling-Rate Integration Constraint

One important engineering constraint has been identified during integration.

The adaptation profiles contain frequencies significantly higher than the **100 kHz sampling rate used in the current software demonstration**.

For example, a profile containing:

```text
f0 = 250 kHz
BW = 80 kHz
```

has:

```text
fmax = 330 kHz
```

Therefore:

```text
fs > 660 kHz
```

would be required to satisfy the Nyquist condition.

The current 100 kHz sampling configuration therefore cannot directly support every adaptation profile.

This has **not been silently changed** in the adaptation algorithm.

The final embedded sampling configuration will need to be resolved during hardware integration.

The lower-frequency LFM examples currently used are **software verification cases**, not claims about the final underwater operating frequency.

---

## 10. Example Software Test

A representative DSP software test uses:

```text
Starting frequency (f0): 5 kHz
Bandwidth (BW):          2 kHz
Duration (T):            0.01 s
Amplitude (A):            0.7
Sampling frequency (fs): 100 kHz
```

This produces a:

```text
5 kHz → 7 kHz
```

LFM sweep.

The generated waveform contains:

```text
N = fs × T
  = 100000 × 0.01
  = 1000 samples
```

The generated waveform and exported C buffer were successfully verified in the software pipeline.

This example is used for **DSP/software validation only**.

---

## 11. Repository Structure

The current project is organized approximately as follows:

```text
AE-Sonar/
│
├── adaptation.py
├── waveform_generator.py
├── README.md
├── .gitignore
│
└── sih_esp32/
    │
    ├── platformio.ini
    │
    ├── include/
    │   └── waveform_buffer.h
    │
    └── src/
        └── main.cpp
```

Generated audio/test artifacts can be kept outside the repository when appropriate.

---

## 12. Development Flow

The project follows a staged development approach:

```text
Adaptation
    ↓
DSP
    ↓
Embedded
    ↓
Physical Output
    ↓
Acoustic Validation
    ↓
Underwater Testing
    ↓
Energy Measurement
```

The current implementation focuses on establishing correctness in the first three stages before moving to physical validation.

---

## 13. Planned Next Phase

The next development phase will focus on physical validation:

### Step 1 — ADC validation

Connect a controllable input/environment proxy to the ESP32 ADC.

### Step 2 — DAC validation

Generate a simple test waveform and verify the physical DAC output.

### Step 3 — LFM validation

Generate the LFM waveform through the embedded output path and inspect it using an oscilloscope.

### Step 4 — Signal conditioning

Introduce appropriate filtering and amplification for the intended analog signal path.

### Step 5 — Transducer integration

Connect and characterize the acoustic transducer.

### Step 6 — Underwater testing

Evaluate the acoustic transmission chain under controlled conditions.

### Step 7 — Energy measurement

Measure voltage, current and transmission duration before making quantitative energy-efficiency claims.

---

## 14. Research Direction

AE-Sonar is informed by research in:

* Adaptive underwater acoustic transmission
* Energy-aware transmission
* Time-varying underwater channels
* Adaptive modulation and transmission
* Resource-constrained underwater systems

Selected references include:

1. Fan et al. (2023), *Energy-efficient underwater acoustic communication based on Dyna-Q with an adaptive action space*, Physical Communication 61, 102218.

2. Cen et al. (2021), *Double-Scale Adaptive Transmission in Time-Varying Channel for Underwater Acoustic Sensor Networks*, Sensors.

3. Jing et al. (2022), *Adaptive Modulation and Coding for Underwater Acoustic Communications Based on Data-Driven Learning Algorithm*, Remote Sensing.

4. Kadali et al. (2025), *AI-powered cognitive modulation adaptation for energy-efficient underwater acoustic communication*, Intelligent Marine Technology and Systems.

These works provide research context for adaptive and energy-aware underwater transmission. They do not constitute experimental validation of AE-Sonar.

---

## 15. Team

**Team MUZAN 2.0**

| Member       | Role                   |
| ------------ | ---------------------- |
| Jyotiraditya | Software + Adaptation  |
| Raktim       | Software + Hardware    |
| Rajnil       | Adaptation + Hardware  |
| Dipika       | Integration + DSP      |
| Mrinmoy      | Embedded + Integration |
| Jyotiprasad  | DSP + Embedded         |

---

## 16. Project Status

**Current milestone:**

### Software-verified adaptive waveform-generation pipeline + ESP32 firmware build

The project is being developed as part of **Smart India Hackathon 2026 — Problem Statement 26058**.

The present repository focuses on the software/DSP foundation. Physical acoustic and underwater validation remain future development stages.

---

## 17. Disclaimer

AE-Sonar is currently a prototype/research implementation.

The repository does **not** claim:

* experimentally measured energy savings
* validated underwater acoustic performance
* complete sonar-system operation
* optimal transmission parameters
* universal relationships between turbidity and frequency
* physical DAC/transducer validation

Such claims require experimental hardware and underwater testing.

---

## License

Add an appropriate open-source license before publishing the repository if you intend to make the code reusable by others.
