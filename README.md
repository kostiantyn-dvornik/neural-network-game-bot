# neural-network-game-bot
Tool for record and playback game input based on neural networks image classification. Suitable for autotesting games, creating vison based bots

# Overview
https://www.youtube.com/watch?v=RrRIE1z0XGw

This tool is a game input recorder and player. The tool allows you to record input sequences while playing a game and later replay them for testing or automation purposes. Work together with TensorFlow based image classification.

# Features
- Record your keystrokes and mouse movements while playing a game.
- Replay the recorded input sequences, simulating the original gameplay.
- Text based recorded input.
- Adopted for Skyrim record/playback that analyze screen and do state based logic.
- Neural Network image classification for camera horizon stabilization, stuck, fight, road detection

# Installation
- Python 3.10
- pip install tensorflow-cpu==2.10 tensorflow-directml-plugin opencv-python matplotlib mss
- DX12 support for GPU training and execution acceleration
https://learn.microsoft.com/en-us/windows/ai/directml/gpu-tensorflow-plugin

# Getting Started
1. Put NN.txt in root of Skyrim. It contains console commands to set daytime, endless HP etc.
1. Run Skyrim in window mode 1440x810 on primary monitor. 
1. Don't use scaling in windows it will result wrong screenshot capture
1. Hit toggle and enter bat NN it will run scipt to have same conditions
1. Use non snow location
1. Run Bot.py (preffered to use visual studio code)
1. Hit Skyrim windows to make it active
1. Press ENTER to start autoplayback

# Changlelog
2023.07 
- Initial

2023.10
https://www.youtube.com/watch?v=ASy-2zOMj_Y
- Added Tensorflow Keras image classification for stabilize camera horizon
- Added windows auto layout for easier workflow
- Separate classic record and neural networks 

2024.11
https://www.youtube.com/watch?v=ofx753BbWDw
- Moved fully to Python
- Moved to vanilla Skyrim game (no mods)
- Added systemic approach for adding states with neural network detection and recorded playback
- Added tools for testing model in game and crop dataset
- Added script for consistent time of the day and weather for easier dataset 
- Added stuck detection, search for enemy, follow road

# Contact
For any questions or inquiries, please reach out to kostiantyn.dvornik@gmail.com
