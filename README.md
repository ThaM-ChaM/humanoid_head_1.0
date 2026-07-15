# Articulated Humanoid Head for a Robot Receptionist

An expressive humanoid robot head designed for receptionist applications, capable of natural human interaction. The system balances mechanical simplicity with expressive capability, addressing the gap between complex, costly designs (Ameca, Mesmer) and overly limited ones (EVA, EMO).

Presented at the **IEEE/ASME International Conference on Advanced Intelligent Mechatronics (AIM 2026)**, Genoa, Italy.

<p align="center">
  <img src="docs/images/robot_head.jpg" alt="Humanoid robot head with silicone skin" width="400"/>
</p>

## Overview

The head features a simplified **21-DoF mechanical design** (mouth, eyes, eyebrows, and neck) driven by 22 servomotors and covered with realistic silicone skin, attached through a novel hybrid system of snap fasteners and magnets. It expresses the six basic emotions defined by the Facial Action Coding System, achieving an average human-likeness rating of **4.13/5** in a 60-participant user study.

Beyond expression, the robot interacts naturally with people:

- **Human re-identification** — detects, tracks, and remembers users in real time using SCRFD, BYTETrack, and ArcFace, including multi-user settings
- **Natural conversation** — LLaMA 3.1 with a RAG knowledge base for domain-specific responses, FasterWhisper speech-to-text, MeloTTS speech synthesis, and speech-synchronized jaw motion
- **Edge deployment** — the full perception and interaction pipeline runs in real time on an NVIDIA Jetson AGX Xavier, integrated with ROS2

The complete mechanical design and code are released to support reproducibility.


```

## Acknowledgments

Developed at the Department of Electronic and Telecommunication Engineering, University of Moratuwa, Sri Lanka, under the supervision of Dr. Wageesha N. Manamperi, Dr. Udaya S. K. Perera Miriya Thanthrige, and Dr. Peshala Jayasekara. The silicone skin mold design was adapted from the open-source [EVA robot head](https://doi.org/10.1016/j.ohx.2021.e00117).
