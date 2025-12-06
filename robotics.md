---
title: Robotics Dashboard
description: Robotics research and industry news
category: tech
page_id: robotics
updated: '2025-12-06T10:28:32.543292+00:00'
url: https://peekdeck.ruidiao.dev/robotics.html
markdown_url: https://peekdeck.ruidiao.dev/robotics.md
widgets: 3
data_types:
- videos
- news
- social
---

# Robotics Dashboard

Robotics research and industry news

**Last Updated:** December 06, 2025 at 10:28 UTC  
**HTML Version:** [robotics.html](https://peekdeck.ruidiao.dev/robotics.html)

---

## Table of Contents

1. [Reddit: r/robotics](#reddit-rrobotics)
2. [Google News: "robotics"](#google-news-robotics)
3. [YouTube Videos: "robotics"](#youtube-videos-robotics)

---

## Reddit: r/robotics

**[Robot dance Arduino](https://www.reddit.com/r/robotics/comments/1pfijsr/robot_dance_arduino/)**

3h ago

---

**[Sunday Robotics: Collecting Data Through the Memory-Developer Glove Before Building the Humanoid](https://www.reddit.com/r/robotics/comments/1pf9wv3/sunday_robotics_collecting_data_through_the/)**

https://youtu.be/UAlm8Z4mfpU

11h ago

---

**[AGIBOT D1 Pro](https://www.reddit.com/r/robotics/comments/1peuynn/agibot_d1_pro/)**

AGIBOT on 𝕏: AGIBOT D1 Pro/Edu Quadruped Robot is not only a reliable helper for scientific research and education but also an eye-catcher for entertainment companionship and commercial demonstrations～ 3.5m/s fast running, 1-2 hours battery life, IP54 dustproof & waterproof, durable and easy to use!: https://x.com/AgiBot_zhiyuan/status/1996928040182464537

21h ago

---

**[Arduino Nano quadcopter build help](https://www.reddit.com/r/robotics/comments/1pfk3x2/arduino_nano_quadcopter_build_help/)**

Hella everyone! I've been building this drone as my own personal test on my engineering knowledge as I've just finished my mechatronic systems engineering degree. Sorry if the post is too long but here is a TLDR: TLDR: My motors won't spin, arduino logic and wiring should be correct as it worked with an older QBRAIN 4in1 ESC. Suspecting one of my cells in my 3S battery to be dead. Initialization tone is heard but no arming tone and writing esc.writeMicroseconds(1000); in the loop. Also tried 1500us and 2000us. Still doesn't work. ---------------------------------------------------------------------------------------------------- Here is a list of components: Arduion Nano: CH340 chip and ATmega328P ESC: Radiolink FlyColour 4 in 1 ESC (EFM8BB21 MCU, 8-bit C8051 core) Motors: 4x 900Kv BLDC motors (No idea what brand, I just found them) RX/TX: FlySky iA6B receiver and FS-i6X transmitter Gyro: MPU-6050 Buck converter: LM2596 ---------------------------------------------------------------------------------------------------- My setup: I've got the arduino outputting PWM signals into my ESC's motor signal pins which has been mapped to 1000-2000us before being sent into the ESC. (I dont have an oscilloscope to verify) The arduino is powered through the buck converter which sees the full Lipo battery voltage at the input (Stepped down to 5v for the arduino and grounded at arduino gnd) The ESC is powered directly from the Lipo battery and I've connected one of the two grounds leading OUT of the ESC's jst connector into the arduino ground. M1 signal wire is connected to D8 of my arduino and M1 is the only one that is plugged in and powered by the ESC At the moment I just want to be able to command the motor speed through the arduino, no PID control, no serial UART communications just yet. ---------------------------------------------------------------------------------------------------- My Problem: I can hear the motors play the initalization musical tone, but no subsequent beeps for self test or arming and it will not spin. When using the exact same setup on an older QBRAIN 4 in 1 ESC it all worked. Including my PID control and iBUS UART communication. Except the arduino needed to be powered through the ESC's regulator instead of the battery + buck converter combo. ---------------------------------------------------------------------------------------------------- My Theory: One of the 3 cells on my battery is dead, ESC is not getting enough voltage and I'm an idiot ESC boots faster than arduino can and goes into fail safe mode EMI between the logic and power grounds Arduino can't output a fast enough PWM signal If anyone could point me in the right direction to troubleshoot it would be greatly appreciated. I will go buy a new battery in the morning to see if that is the problem. However in the meantime if anyone could point out any wiring issues from what I've described or if you require any more specific information about my setup please let me know. Otherwise feel free to criticize, hate or provide constructive suggestions to my project. ---------------------------------------------------------------------------------------------------- Extra questions: Is the arduino nano even a suitable MCU for this application? From my research it seems like there is not enough of a safety margin in terms of cycles/second to do PID math, read gyro data and send fast PWM signals. If anything is bunged out of order it could lead to a positive feedback loop and crash my drone Since it is an engineering project and not a drone building project I'd like to use something that i can program. What other microcontrollers can work in place of the nano? (Preferrably not something I need to use assembly and design an MCU from scratch, thats a whole another project) https://preview.redd.it/qdwmnaiw9j5g1.jpg?width=3024&format=pjpg&auto=webp&s=f7871ed8a913dcf55e474cf7cdb7787240a3b9c3

2h ago

---

**[Knee assist exoskeleton motor](https://www.reddit.com/r/robotics/comments/1pfl5ee/knee_assist_exoskeleton_motor/)**

Im working on an electric knee assist exoskeleton and i have a 450 rpm 24V 15kg*cm³ motor and i was wondering if it would be sufficient to show a noticeable difference for an average sized person when using the exoskeleton or will I need to use two motors.

1h ago

---

**[Art installation draws attention for its robot dogs with famous faces](https://www.reddit.com/r/robotics/comments/1pe56c3/art_installation_draws_attention_for_its_robot/)**

1d ago

---

**[Are we witnessing the end of “real robot data” as the foundation of Embodied AI? Recent results from InternData-A1, GEN-0, and Tesla suggest a shift. (Original post by Felicia)](https://www.reddit.com/r/robotics/comments/1pessi4/are_we_witnessing_the_end_of_real_robot_data_as/)**

For a long time, many robotics teams believed that real robot interaction data was the only reliable foundation for training generalist manipulation models. But real-world data collection is extremely expensive, slow, and fundamentally limited by human labor. Recent results suggest the landscape is changing. Three industry signals stand out: 1. InternData-A1: Synthetic data beats the strongest real-world dataset Shanghai AI Lab’s new paper InternData-A1 (Nov 2025, arXiv) is the first to show that pure simulation data can match or outperform the best real-robot dataset used to train Pi0. The dataset is massive: 630k+ trajectories 7,434 hours 401M frames 4 robot embodiments, 18 skill types, 70 tasks $0.003 per trajectory generation cost One 8×RTX4090 workstation → 200+ hours of robot data per day Results: On RoboTwin2.0 (49 bimanual tasks): +5–6% success over Pi0 On 9 real-world tasks: +6.2% success Sim-to-Real: 1,600 synthetic samples ≈ 200 real samples (≈8:1 efficiency) The long-held “simulation quality discount” is shrinking fast. 2. GEN-0 exposes the economic impossibility of scaling real-world teleoperation Cross-validated numbers show: Human teleoperation cost per trajectory: $2–$10 Hardware systems: $30k–$40k 1 billion trajectories → $2–10 billion GEN-0’s own scaling law predicts that laundry alone would require 1B interactions for strong performance. https://preview.redd.it/qd8pkcdpfd5g1.png?width=556&format=png&auto=webp&s=1df2607476d3e63f5ca32edae1bf7319d97f1176 Even with Tesla-level resources, this is not feasible. That’s why GEN-0 relies on distributed UMI collection across thousands of sites instead of traditional teleoperation. 3. Tesla’s Optimus shifts dramatically: from mocap → human video imitation Timeline: 2022–2024: Tesla used full-body mocap suits + VR teleop; operators wore ~30 lb rigs, walked 7 hours/day, paid up to $48/hr. May 21, 2025: Tesla confirms:“Optimus is now learning new tasks directly from human videos.” June 2025: Tesla transitions to a vision-only approach, dropping mocap entirely. Their demo showed Optimus performing tasks like trash disposal, vacuuming, cabinet/microwave use, stirring, tearing paper towels, sorting industrial parts — all claimed to be controlled by a single end-to-end network. 4. So is real robot data obsolete? Not exactly. These developments indicate a shift, not a disappearance: Synthetic data (InternData-A1) is now strong enough to pre-train generalist policies Distributed real data (GEN-0) remains critical for grounding and calibration Pure video imitation (Tesla) offers unmatched scalability but still needs validation for fine manipulation All major approaches still rely on a small amount of real data for fine-tuning or evaluation Open Questions: Where do you think the field is heading? A synthetic-first paradigm? Video-only learning at scale? Hybrid pipelines mixing sim, video, and small real datasets? Or something entirely new? Curious to hear perspectives from researchers, roboticists, and anyone training embodied agents.

22h ago

---

**[Chat Interface for Isaac Sim](https://www.reddit.com/r/robotics/comments/1pfa7jb/chat_interface_for_isaac_sim/)**

10h ago

---

**[Behind-the-scenes footage from the EngineAI T800 shoot — a direct response to the CG accusations.](https://www.reddit.com/r/robotics/comments/1peipg7/behindthescenes_footage_from_the_engineai_t800/)**

Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.

🔗 [youtube.com](https://www.youtube.com/watch?v=VoytjBgpG28) • 1d ago

---

**[ROS News for the Week of December 2nd, 2025](https://www.reddit.com/r/robotics/comments/1pf5ccu/ros_news_for_the_week_of_december_2nd_2025/)**

ROS News for the Week of December 2nd, 2025     ROSCon 2025 videos are now available! If you want a quick summary of the event I put together ROSCon 2025 Recap for the OpenCV Weekly Webinar.       For Giving Tuesday we put together a new campaign for ROS users to become a become a Build Farm Backer. If you’ve every saved a few minutes by running sudo apt install ros-kilted-* instead of compiling from source we would love it if you helped cover our compute costs. Also, for the first time ever, we...

🔗 [Open Robotics Discourse](https://discourse.openrobotics.org/t/ros-news-for-the-week-of-december-2nd-2025/51298) • 14h ago

---

---

## Google News: "robotics"

**[Market-Crushing AI Momentum: Top Robotics Technology Stocks Leading the 2026 Growth Trend](https://seekingalpha.com/article/4850474-market-crushing-ai-momentum-top-robotics-technology-stocks)**

Robotics technologies could be 2026âs next big investment trend as Washington backs automation and next-gen manufacturing. Discover four Quant Strong Buys tied to robotics and AI.

Seeking Alpha • 1d ago

---

**[MIT’s AI Robotics Lab Director Is Building People-Centered Robots](https://spectrum.ieee.org/mits-ai-robotics-lab-director)**

From Romania to MIT, Daniela Rus is redefining robotics to enhance human capabilities. What's her secret to giving people 'superpowers'?

IEEE Spectrum • 2d ago

---

**[Fanuc (TSE:6954) Valuation After Nvidia Physical AI Robotics Deal and Recent Share Price Surge](https://finance.yahoo.com/news/fanuc-tse-6954-valuation-nvidia-070745387.html)**

Fanuc (TSE:6954) just jumped nearly 13% after unveiling a collaboration with Nvidia to build industrial robots powered by physical AI, a move that immediately sharpened investor focus on its long term growth story. See our latest analysis for Fanuc. That surge has come on top of already strong momentum, with a 7 day share price return of 18.0% and a 90 day share price return of 44.3%. The 1 year total shareholder return of 52.4% signals investors are steadily warming to Fanuc as physical AI...

Yahoo Finance • 3h ago

---

**[MIT researchers “speak objects into existence” using AI and robotics](https://news.mit.edu/2025/mit-researchers-speak-objects-existence-using-ai-robotics-1205)**

MIT researchers at the School of Architecture and Planning developed a speech-to-reality system that combines generative AI, natural language processing, and robotic assembly to fabricate physical objects from spoken prompts.

MIT News • 19h ago

---

**[25-year-old robotics company still growing in West Michigan](https://www.mlive.com/news/grand-rapids/2025/12/25-year-old-robotics-company-still-growing-in-west-michigan.html)**

Hyperion Automation on Wednesday, Dec. 4, revealed its second expansion in three years.

MLive.com • 1d ago

---

**[Walmart's AI Robotics Maker Is Sinking For This Reason After Big Run](https://www.investors.com/news/walmart-ai-robotics-maker-symbotic-tumbling-after-big-run/)**

Investor's Business Daily • 1d ago

---

**[3 Robotics Stocks to Buy Now Ahead of a White House Game-Changer](https://www.barchart.com/story/news/36461441/3-robotics-stocks-to-buy-now-ahead-of-a-white-house-game-changer)**

The Trump administration is pushing for robotics as a critical industry to bring back production to the United States.

Barchart.com • 1d ago

---

**[Massimo Group (NASDAQ: MAMO) forms AI robotics division to enter global automation and smart-systems markets](https://www.stocktitan.net/news/MAMO/massimo-group-announces-formation-of-ai-robotics-division-expanding-p08w84pho0qe.html)**

Massimo Group forms Massimo AI Technology to develop industrial automation and logistics robotics, aiming to diversify revenue and expand beyond powersports and EVs.

Stock Titan • 1d ago

---

**[Olympus-backed robotics startup Swan EndoSurgical taps Stryker vet for CEO](https://www.fiercebiotech.com/medtech/olympus-backed-swan-endosurgical-names-stryker-vet-erik-todd-ceo)**

Swan EndoSurgical, a gastrointestinal startup launched by Olympus and Revival Healthcare Capital earlier this year, has named former Stryker executive Erik Todd as its CEO. | Swan EndoSurgical, formed by Olympus and Revival Healthcare Capital this year, named former Stryker executive Erik Todd as CEO.

Fierce Biotech • 2d ago

---

**[Marine robotics firm will resume deep-sea search for MH370 plane that vanished a decade ago](https://www.cnn.com/2025/12/03/asia/malaysia-mh370-robotics-search-latam-intl)**

Malaysia’s transport ministry said Wednesday that a private firm will resume a deep-sea hunt for Malaysia Airlines Flight 370 later this month, more than a decade after the jet vanished without a trace.

CNN • 2d ago

---

---

## YouTube Videos: "robotics"

**[Tesla’s Running Robot: Optimus Just Took a Huge Step Forward](https://www.youtube.com/watch?v=xE_gPhwzQAc)**

Tesla just showed its Optimus humanoid robot running in the laboratory, and it looks a lot closer to a real life sci fi moment than a ...

📺 DPCcars

👁️ 62K • 👍 498 • 💬 248 • ⏱️ 2:30 • 2d ago

---

**[China Just Launched SLAUGHTERBOTS: A Fully AI-Controlled Robot Army](https://www.youtube.com/watch?v=Plp8-cJYuVE)**

Humanoid robots are leaving labs and moving into real deployment, with China pushing ahead fastest. Mass-produced ...

📺 AI Revolution

👁️ 35K • 👍 1K • 💬 191 • ⏱️ 12:07 • 9h ago

---

**[Trump administration looks to supercharge robotics industry, Politico reports](https://www.youtube.com/watch?v=XvXNEYbIBYw)**

Leaders in the robotics industry say that to strengthen AI, companies also need a plan for robots. The White House appears to be ...

📺 CBS News

👁️ 12K • 👍 258 • 💬 140 • ⏱️ 4:05 • 1d ago

---

**[Unitree 1.8m Humanoid Robot  Every Punch Comes Through！🥰](https://www.youtube.com/watch?v=kjJeQZECPcQ)**

Unitree 1.8m H2 Humanoid Robot, A Combat Sparring Test. H2's knee strike lifts G1 off the ground. This is to validate the overall ...

📺 Unitree Robotics

👁️ 761K • 👍 1K • 💬 290 • ⏱️ 1:06 • 2d ago

---

**[Purchased the newly released 2025 humanoid robot. #robotics #ai #humanoidrobot #airobot](https://www.youtube.com/watch?v=NJeenJ276ug)**

📺 AI . Robot

👁️ 1.1M • 👍 6K • 💬 43 • ⏱️ 0:17 • 1d ago

---

**[China&#39;s humanoid robotics leap: new T800 unveiled](https://www.youtube.com/watch?v=wbLl3aSOzoc)**

For more: https://news.cgtn.com/news/2025-12-03/China-s-humanoid-robotics-leap-new-T800-unveiled-1INHjYVbHGM/p.html ...

📺 CGTN

👁️ 97K • 💬 599 • ⏱️ 1:21 • 3d ago

---

**[Guy Tries Out the Newest Girlfriend Robot at the Expo.](https://www.youtube.com/watch?v=_MgTHoFYPDs)**

At Expo 2025, a man unveils his stunning robot girlfriend — blending cutting-edge design with lifelike AI reactions. From futuristic ...

📺 Humanoid Robot 🤖

👁️ 88K • 👍 442 • 💬 5 • ⏱️ 0:19 • 1d ago

---

**[AI Humanoid Robot Activated in 2025 — Reacts Like a Real Human in Silicon Valley Lab](https://www.youtube.com/watch?v=bjUcx-S0-ks)**

In a 2025 Silicon Valley Robotics lab, engineers finish a new AI humanoid robot and apply a breakthrough synthetic skin.

📺 AI Robot Lab

👁️ 105K • 👍 408 • 💬 10 • ⏱️ 0:19 • 21h ago

---

**[Viral Art Exhibit Shows Musk, Zuckerberg and Bezos as Creepy Robot Dogs](https://www.youtube.com/watch?v=tFfR0uQXl7w)**

Famed artist Beeple's newest spectacle, “Regular Animals,” has billionaire-tech-titan robot dogs pooping out NFTs, stopping ...

📺 New York Post

👁️ 5K • 👍 100 • 💬 65 • ⏱️ 2:06 • 20h ago

---

**[ChatGPT in a real robot does what experts warned.](https://www.youtube.com/watch?v=byQmJ9x0RWA)**

Chat GPT inside a robot. Can we trust AI? Use code insideai at https://incogni.com/insideai to get an exclusive 60% off Please ...

📺 InsideAI

👁️ 577K • 👍 23K • 💬 3K • ⏱️ 14:58 • 5d ago

---

---

*Generated by PeekDeck - A glance is all you need*
