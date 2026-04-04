🤖 Tommy: The Interactive, Dancing Bipedal Robot
Tommy is a Python-controlled bipedal robot built using a Raspberry Pi. Utilizing the gpiozero library, Tommy uses sine-wave-based oscillation to achieve smooth walking, turning, and highly dynamic, multi-phase dance routines.

With recent hardware upgrades, Tommy now features an OLED face for expressions, an I2S microphone to listen to the environment, and a speaker to play music and respond!

✨ Features
Smooth Bipedal Locomotion: Walks forward and backward using synchronized sine waves.

In-Place Rotation: Can turn left and right by shifting the phase of its hip servos.

Auto-Stabilization: Automatically returns to a locked, balanced standing pose when idle.

The "Music Dance" Coreography: An extended, 20+ second dance routine featuring 5 unique phases.

Expressive Face (New!): Ready to display animated eyes or system status via an I2C OLED display.

Audio Capabilities (New!): Wired for an I2S microphone for voice recognition and an I2S DAC amplifier for playing music or speech.

🛠 Hardware Requirements
Brain: Raspberry Pi (e.g., Pi 3, Pi 4, or Pi Zero W)

Movement: 5x Micro Servos (e.g., SG90 or MG90S)

Face: 1x 0.96" I2C OLED Display (SSD1306)

Hearing: 1x I2S Omnidirectional Microphone (e.g., INMP441)

Voice/Music: 1x I2S Audio Amplifier (e.g., MAX98357A) + Small 3W Speaker

Power Warning: You must power the servos using a separate 5V power supply (like a BEC or buck converter). If you run 5 servos, a display, and a speaker directly off the Pi's 5V pins, the Pi will crash or reboot. Connect the ground (GND) of the external power supply to the Pi's GND.

🔌 Complete Wiring & Pinout
1. Servo Motors (Movement)

Servo Part	GPIO Pin (BCM)	Physical Board Pin
Left Hip	GPIO 4	Pin 7
Left Foot	GPIO 24	Pin 18
Right Hip	GPIO 6	Pin 31
Right Foot	GPIO 13	Pin 33
Left Hand	GPIO 26	Pin 37
2. I2C OLED Display (The Face)

Display Pin	Pi GPIO (BCM)	Physical Board Pin	Notes
VCC	3.3V	Pin 1	Power for the display
GND	GND	Pin 9	Ground
SDA	GPIO 2	Pin 3	I2C Data
SCL	GPIO 3	Pin 5	I2C Clock
3. I2S Audio Module (Mic & Speaker)

Note: I2S devices share the same clock pins (BCLK/SCK and LRC/WS).

Audio Pin	Pi GPIO (BCM)	Physical Board Pin	Device
BCLK / SCK	GPIO 18	Pin 12	Clock (Shared by Mic & Speaker)
LRC / WS	GPIO 19	Pin 35	Word Select (Shared by Mic & Speaker)
DIN	GPIO 21	Pin 40	Data IN (To Speaker Amp)
DOUT / SD	GPIO 20	Pin 38	Data OUT (From Microphone)
(Alternatively, you can use a standard USB plug-and-play Microphone/Speaker to skip the complex I2S wiring entirely!)

💻 Software Setup
Ensure your Raspberry Pi is running Raspberry Pi OS with Python 3 installed.

Enable I2C and I2S interfaces in the Raspberry Pi config menu:

Bash
sudo raspi-config
# Go to Interfacing Options -> Enable I2C
Install the required movement library:

Bash
pip install gpiozero
(Future Step) Install display and audio libraries:

Bash
pip install adafruit-circuitpython-ssd1306 Pillow pyaudio
🚀 How to Run Tommy
Navigate to the directory containing the script and run it using Python:

Bash
python3 tommy_robot.py
Upon running, Tommy will automatically stabilize and a command menu will appear in your terminal:

m : ♫ Start Long Dance Routine ♫

w : Walk Forward

a / d : Turn Left / Right

q : Quit program

🧠 Process of Implementation
Tommy's logic is built on Trigonometric Oscillation rather than hard-coded frames.

The Engine: The _oscillate(A, O, T, phase_diff) function calculates the position of every servo at a given moment using a Sine Wave (math.sin).

Amplitudes & Offsets: Amplitude (A) dictates how "big" a movement is, while Offset (O) dictates the center point (90 degrees for standing straight).

Phase Shifting: By shifting the sine wave of the feet by 90 
∘
  relative to the hips, the robot leans right before it lifts its foot, creating a balanced walk cycle.

Hardware Expansion: The OLED is configured on the I2C bus to eventually draw "eyes" using Python's Pillow library. The I2S audio bus is mapped out so Tommy can eventually run a script to listen for a beat and trigger the dance_music() function autonomously!
