---
title: Robotics Dashboard
description: Robotics research and industry news
category: tech
page_id: robotics
updated: '2025-12-05T12:52:17.677056+00:00'
url: https://peekdeck.ruidiao.dev/robotics.html
markdown_url: https://peekdeck.ruidiao.dev/robotics.md
widgets: 3
data_types:
- social
- videos
- news
---

# Robotics Dashboard

Robotics research and industry news

**Last Updated:** December 05, 2025 at 12:52 UTC  
**HTML Version:** [robotics.html](https://peekdeck.ruidiao.dev/robotics.html)

---

## Table of Contents

1. [Reddit: r/robotics](#reddit-rrobotics)
2. [Google News: "robotics"](#google-news-robotics)
3. [YouTube Videos: "robotics"](#youtube-videos-robotics)

---

## Reddit: r/robotics

**["Volonaut" Airbike: Jet-powered hoverbike landing with advanced stabilization (Prototype Demo)](https://www.reddit.com/r/robotics/comments/1pequkz/volonaut_airbike_jetpowered_hoverbike_landing/)**

This is the Volonaut Airbike, a prototype by Polish inventor Tomasz Patan. Mechanism: Jet-powered vertical take-off and landing (VTOL). Control: Uses an advanced stabilization system to assist the rider's balance during precision maneuvers. Specs: Carbon fiber frame (30kg), top speed ~100km/h (capped) and flight time ~10 mins. Source: Volonaut 🔗 : https://youtu.be/4b0Laxsj_z0?si=8loRPWJWr4v622ii

3h ago

---

**[Art installation draws attention for its robot dogs with famous faces](https://www.reddit.com/r/robotics/comments/1pe56c3/art_installation_draws_attention_for_its_robot/)**

19h ago

---

**[Behind-the-scenes footage from the EngineAI T800 shoot — a direct response to the CG accusations.](https://www.reddit.com/r/robotics/comments/1peipg7/behindthescenes_footage_from_the_engineai_t800/)**

Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.

🔗 [youtube.com](https://www.youtube.com/watch?v=VoytjBgpG28) • 10h ago

---

**[Beeple just put Musk, Zuck and Bezos heads on robot dogs that literally shit NFTs at Art Basel. We are so cooked.](https://www.reddit.com/r/robotics/comments/1peofci/beeple_just_put_musk_zuck_and_bezos_heads_on/)**

5h ago

---

**[PLA logistics brigade member delivering supplies to frontline positions with the new standard passive exoskeleton during combat training.](https://www.reddit.com/r/robotics/comments/1pen0qf/pla_logistics_brigade_member_delivering_supplies/)**

7h ago

---

**[Marc Raibert on Why Robotics Needs More Transparency](https://www.reddit.com/r/robotics/comments/1pea59d/marc_raibert_on_why_robotics_needs_more/)**

Marc Raibert talks about how robotics demos usually show only the polished successes, even though most of the real progress comes from the failures. The awkward grasps, strange edge cases, and completely unexpected behaviors are where engineers learn the most. He points out that hiding all of that creates a distorted picture of what robotics development actually looks like. What makes his take interesting is that it comes from someone who helped define the modern era of legged robots. Raibert has been around long enough to see how public perception shifts when the shiny videos overshadow the grind behind them. His push for more openness feels less like criticism and more like a reminder of what drew so many people into robotics in the first place: the problem solving, the iteration, and the weird in-between moments where breakthroughs usually begin.

16h ago

---

**[Are we witnessing the end of “real robot data” as the foundation of Embodied AI? Recent results from InternData-A1, GEN-0, and Tesla suggest a shift. (Original post by Felicia)](https://www.reddit.com/r/robotics/comments/1pessi4/are_we_witnessing_the_end_of_real_robot_data_as/)**

For a long time, many robotics teams believed that real robot interaction data was the only reliable foundation for training generalist manipulation models. But real-world data collection is extremely expensive, slow, and fundamentally limited by human labor. Recent results suggest the landscape is changing. Three industry signals stand out: 1. InternData-A1: Synthetic data beats the strongest real-world dataset Shanghai AI Lab’s new paper InternData-A1 (Nov 2025, arXiv) is the first to show that pure simulation data can match or outperform the best real-robot dataset used to train Pi0. The dataset is massive: 630k+ trajectories 7,434 hours 401M frames 4 robot embodiments, 18 skill types, 70 tasks $0.003 per trajectory generation cost One 8×RTX4090 workstation → 200+ hours of robot data per day Results: On RoboTwin2.0 (49 bimanual tasks): +5–6% success over Pi0 On 9 real-world tasks: +6.2% success Sim-to-Real: 1,600 synthetic samples ≈ 200 real samples (≈8:1 efficiency) The long-held “simulation quality discount” is shrinking fast. 2. GEN-0 exposes the economic impossibility of scaling real-world teleoperation Cross-validated numbers show: Human teleoperation cost per trajectory: $2–$10 Hardware systems: $30k–$40k 1 billion trajectories → $2–10 billion GEN-0’s own scaling law predicts that laundry alone would require 1B interactions for strong performance. https://preview.redd.it/qd8pkcdpfd5g1.png?width=556&format=png&auto=webp&s=1df2607476d3e63f5ca32edae1bf7319d97f1176 Even with Tesla-level resources, this is not feasible. That’s why GEN-0 relies on distributed UMI collection across thousands of sites instead of traditional teleoperation. 3. Tesla’s Optimus shifts dramatically: from mocap → human video imitation Timeline: 2022–2024: Tesla used full-body mocap suits + VR teleop; operators wore ~30 lb rigs, walked 7 hours/day, paid up to $48/hr. May 21, 2025: Tesla confirms:“Optimus is now learning new tasks directly from human videos.” June 2025: Tesla transitions to a vision-only approach, dropping mocap entirely. Their demo showed Optimus performing tasks like trash disposal, vacuuming, cabinet/microwave use, stirring, tearing paper towels, sorting industrial parts — all claimed to be controlled by a single end-to-end network. 4. So is real robot data obsolete? Not exactly. These developments indicate a shift, not a disappearance: Synthetic data (InternData-A1) is now strong enough to pre-train generalist policies Distributed real data (GEN-0) remains critical for grounding and calibration Pure video imitation (Tesla) offers unmatched scalability but still needs validation for fine manipulation All major approaches still rely on a small amount of real data for fine-tuning or evaluation Open Questions: Where do you think the field is heading? A synthetic-first paradigm? Video-only learning at scale? Hybrid pipelines mixing sim, video, and small real datasets? Or something entirely new? Curious to hear perspectives from researchers, roboticists, and anyone training embodied agents.

1h ago

---

**[A potentially highly efficient image and video tokenizer for LLMs/VLAs.](https://www.reddit.com/r/robotics/comments/1peo0w3/a_potentially_highly_efficient_image_and_video/)**

Since 10 years ago, I have been thinking about the following question in my spare time, mostly as an intellectual challenge just for fun: if you are an engineer tasked to design the visual system of an organism, what would you do? This question is too big, so I worked one small step at a time and see how far I can get. I have summarized my decade journey in the following note: https://arxiv.org/abs/2210.13004 Probably the most interesting part is the last part of the note where I proposed a loss function to learn image patches representation using unsupervised learning. The learned representation is a natural binary vector, rather than typical real vectors or binary vectors from quantization of real vectors. Very preliminary experiments show that it is much more efficient than the representation learned by CNN using supervised learning. Practically, I’m thinking this could be used as an image/video tokenizer for LLMs or related models. However, due to growing family responsibilities, I now have less time to pursue this line of research as a hobby. So I’m posting it here in case anyone finds it interesting or useful.

6h ago

---

**[UBTECH Walker S2 - World’s First Mass Delivery of Humanoid Robots](https://www.reddit.com/r/robotics/comments/1peqau3/ubtech_walker_s2_worlds_first_mass_delivery_of/)**

Enjoy the videos and music you love, upload original content, and share it all with friends, family, and the world on YouTube.

🔗 [youtu.be](https://youtu.be/nzflxCHT4vw?si=-5HRhvsVT8sEiVIO) • 3h ago

---

**[Any genuinely promising robotics applications in construction?](https://www.reddit.com/r/robotics/comments/1peq7b7/any_genuinely_promising_robotics_applications_in/)**

Humanoid robotics is getting cheaper, smarter, and a lot more capable at moving through the world. But construction sites are a different beast with uneven terrain, unpredictable workflows, and tasks that vary wildly from day to day. I’m curious whether robotics aimed specifically at construction has kept up. Not the glossy demo videos, but actual sector-focused systems that show real progress on tasks like material handling, layout, inspections, drilling, or repetitive onsite work. It actually feels like construction is one of the few fields where purpose-built robots should make far more sense than humanoids. Most site tasks don’t need a human-shaped form factor at all. Are there ad hoc or specialized robots that feel like a real breakthrough, or is the field still stuck in research prototypes?

4h ago

---

---

## Google News: "robotics"

**[After AI push, Trump administration is now looking to robots](https://www.politico.com/news/2025/12/03/trump-administration-ai-robotics-00674204)**

Politico • 1d ago

---

**[MIT’s AI Robotics Lab Director Is Building People-Centered Robots](https://spectrum.ieee.org/mits-ai-robotics-lab-director)**

From Romania to MIT, Daniela Rus is redefining robotics to enhance human capabilities. What's her secret to giving people 'superpowers'?

IEEE Spectrum • 1d ago

---

**[Robotic Vehicle Sensor Market - Forecasts from 2025 to 2030: Opportunities Driven by Government Initiatives Like NIST's AV Programme, Significant Robotics Investments, China's Manufacturing Leadership](https://finance.yahoo.com/news/robotic-vehicle-sensor-market-forecasts-114500165.html)**

The robotic vehicle sensor market is expanding rapidly due to increased autonomous vehicle adoption and EV sector growth. Key opportunities are driven by government initiatives like NIST's AV Programme, significant robotics investments, and China's manufacturing leadership in Asia-Pacific. Robotic Vehicle Sensor Market Robotic Vehicle Sensor Market Dublin, Dec. 05, 2025 (GLOBE NEWSWIRE) -- The "Robotic Vehicle Sensor Market - Forecasts from 2025 to 2030" report has been added to ResearchAndMarke

Yahoo Finance • 1h ago

---

**[Trump administration looks to supercharge robotics industry, Politico reports](https://www.cbsnews.com/video/trump-administration-looks-supercharge-robotics-industry-politico/)**

Leaders in the robotics industry say that to strengthen AI, companies also need a plan for robots. The White House appears to be listening. Yasmin Khorram, economic policy reporter for Politico, joins CBS News to discuss her article on the topic.

CBS News • 15h ago

---

**[Market-Crushing AI Momentum: Top Robotics Technology Stocks Leading the 2026 Growth Trend](https://seekingalpha.com/article/4850474-market-crushing-ai-momentum-top-robotics-technology-stocks)**

Robotics technologies could be 2026âs next big investment trend as Washington backs automation and next-gen manufacturing. Discover four Quant Strong Buys tied to robotics and AI.

Seeking Alpha • 2h ago

---

**[Robotics Stocks Surged on Wednesday. Here's Why.](https://www.nasdaq.com/articles/robotics-stocks-surged-wednesday-heres-why)**

Key PointsPresident Trump is reportedly considering signing an executive order in the new year to accelerate the development of robots in the U.S.

Nasdaq • 1d ago

---

**[Walmart's AI Robotics Maker Is Sinking For This Reason After Big Run](https://www.investors.com/news/walmart-ai-robotics-maker-symbotic-tumbling-after-big-run/)**

Investor's Business Daily • 15h ago

---

**[Former Stryker robotics leader named CEO at Olympus’ Swan EndoSurgical robotics play](https://www.massdevice.com/former-stryker-leader-ceo-swan-endosurgical-olympus/)**

Swan EndoSurgical announced today that it has appointed longtime Stryker robotics leader Erik Todd as its CEO.

MassDevice • 2d ago

---

**[3 Robotics Stocks to Buy Now Ahead of a White House Game-Changer](https://www.barchart.com/story/news/36461441/3-robotics-stocks-to-buy-now-ahead-of-a-white-house-game-changer)**

The Trump administration is pushing for robotics as a critical industry to bring back production to the United States.

Barchart.com • 18h ago

---

**[Vision-native AI opportunities: a precursor to intelligent robotics](https://www.bvp.com/atlas/vision-native-ai-opportunities-a-precursor-to-intelligent-robotics)**

As AI advances into the real world of robotics and automation, we’re seeing a turning point for physical AI — 1X’s NEO Home Robot can now adapt to new environments in real-time, Physical Intelligence’s Pi0 became the first robot to fold laundry with human-level dexterity straight from a hamper, and Tesla’s Optimus is performing complex […]

Bessemer Venture Partners • 2d ago

---

---

## YouTube Videos: "robotics"

**[ChatGPT in a real robot does what experts warned.](https://www.youtube.com/watch?v=byQmJ9x0RWA)**

Chat GPT inside a robot. Can we trust AI? Use code insideai at https://incogni.com/insideai to get an exclusive 60% off Please ...

📺 InsideAI

👁️ 506K • 👍 20K • 💬 3K • ⏱️ 14:58 • 4d ago

---

**[Unitree 1.8m Humanoid Robot  Every Punch Comes Through！🥰](https://www.youtube.com/watch?v=kjJeQZECPcQ)**

Unitree 1.8m H2 Humanoid Robot, A Combat Sparring Test. H2's knee strike lifts G1 off the ground. This is to validate the overall ...

📺 Unitree Robotics

👁️ 110K • 👍 1K • 💬 257 • ⏱️ 1:06 • 2d ago

---

**[Live Unboxing of the AI Humanoid Robot. #robotics #humanoidrobot #robot #ai](https://www.youtube.com/watch?v=k0cHshXI6dc)**

📺 AI . Robot

👁️ 487K • 👍 6K • 💬 229 • ⏱️ 0:27 • 6d ago

---

**[China&#39;s humanoid robotics leap: new T800 unveiled](https://www.youtube.com/watch?v=wbLl3aSOzoc)**

For more: https://news.cgtn.com/news/2025-12-03/China-s-humanoid-robotics-leap-new-T800-unveiled-1INHjYVbHGM/p.html ...

📺 CGTN

👁️ 82K • 💬 527 • ⏱️ 1:21 • 2d ago

---

**[AI Robot Girl Calibration Reveals Her New Emotional Upgrade #AIrobot #Robotgirl](https://www.youtube.com/watch?v=F3bsD3rrodE)**

In a high-end robotics lab in Silicon Valley, engineers activate and calibrate a next-gen AI Humanoid Robot Girl. As her synthetic ...

📺 AI Robot Lab

👁️ 47K • 👍 579 • 💬 6 • ⏱️ 0:29 • 1d ago

---

**[Humanoid robot Vol.149: Robotics Lab](https://www.youtube.com/watch?v=mVAHi_eB8Mc)**

AI #stablediffusion #AIart #humanoid #scifi #robot #futuretech.

📺 ROBOT HUMANOID AI

👁️ 7K • 👍 94 • ⏱️ 0:25 • 20h ago

---

**[Humanoid robots attentively feed babies and care for them!](https://www.youtube.com/watch?v=qLHweaRvF84)**

Humanoid robots attentively feed babies and care for them! #ai #robot #humanoidrobot #futuristic #robotics #technology ...

📺 NUROBIQ

👁️ 39K • 👍 335 • 💬 3 • ⏱️ 0:10 • 4d ago

---

**[Symbotic (SYM) Analysis: Robotics Pure Play or Just a Walmart Vendor?](https://www.youtube.com/watch?v=XLkQ6o-dz30)**

Pure-play robotics stock Symbotic (SYM) has had a wild ride in 2025, soaring to new highs before taking a significant ...

📺 Chip Stock Investor

👁️ 3K • 👍 144 • 💬 9 • ⏱️ 14:23 • 21h ago

---

**[New Humanoid ‘Jena’ Unveiled at the 2025 Robot Expo. #robotics #humanoidrobot #robot #ai](https://www.youtube.com/watch?v=XVHKg1DNMg4)**

📺 AI . Robot

👁️ 387K • 👍 4K • 💬 42 • ⏱️ 0:19 • 4d ago

---

**[Guy Tries Out the Newest Girlfriend Robot at the Expo](https://www.youtube.com/watch?v=JfOMxe8zbxo)**

robots #irc #humanoid At the latest tech expo, a man shows off his brand new robot girlfriend. From futuristic design to human-like ...

📺 She Shorts AI

👁️ 1.8M • 👍 10K • 💬 19 • ⏱️ 0:11 • 4d ago

---

---

*Generated by PeekDeck - A glance is all you need*
