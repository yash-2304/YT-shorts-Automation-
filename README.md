# 🚀 YouTube Shorts Automation Pipeline

An end-to-end automated system that converts long-form videos into high-retention YouTube Shorts using AI, video processing, and API integration.

---

## ⚡ Overview

This project automates the entire lifecycle of Shorts creation:

- Extracts high-impact moments from long videos
- Generates captions using speech-to-text
- Creates engaging AI-powered titles
- Enhances retention using gameplay overlays
- Uploads content directly to YouTube via API

Designed for scalable, faceless content creation workflows.

---

## 🎯 Features

### 🎬 Smart Clip Extraction
- Uses Whisper-based transcription to identify meaningful segments  
- Avoids naive slicing → focuses on high-signal moments  

### 🧠 AI Captions
- Generates subtitles automatically  
- Builds transcripts for downstream processing  

### ✍️ AI Title Generation
- Uses OpenAI to generate engaging, short-form optimized titles  
- Multiple styles: dramatic, informational, viral  

### 🎮 Retention Optimization
- Merges clips with gameplay (e.g., Minecraft parkour / Subway Surfers)  
- Boosts viewer retention for Shorts  

### 📤 Automated Upload
- Uses YouTube Data API (OAuth-based)  
- Handles metadata, titles, and publishing  

### 🧹 Clean Pipeline Execution
- Full lifecycle management:

Generate → Process → Upload → Cleanup
---

## 🧱 Pipeline Flow
YouTube URL
↓
Download Video
↓
Highlight Extraction (AI)
↓
Caption Generation (Whisper)
↓
Title Generation (OpenAI)
↓
Gameplay Merge (FFmpeg)
↓
Upload to YouTube
↓
Cleanup

---

## 🛠 Tech Stack

- Python
- OpenAI API
- Whisper (Speech-to-Text)
- FFmpeg
- YouTube Data API
- OAuth 2.0

---

## ⚙️ Setup

### 1. Clone the repo
git clone https://github.com/yash-2304/YT-shorts-Automation-.git
cd YT-shorts-Automation-

OPENAI_API_KEY=your_openai_api_key

### 3. Add YouTube credentials
- Place `client_secret.json` in root
- Authenticate on first run

---

## ▶️ Run Pipeline
python3 run_pipeline.py “<youtube_video_url>”

---

## ⚠️ Notes

- Secrets and media files are excluded from this repository  
- Requires FFmpeg installed locally  
- YouTube upload limits may apply  

---

## 💡 Use Cases

- Faceless YouTube automation channels  
- AI-driven content pipelines  
- Social media growth experiments  
- Video repurposing workflows  

---

## 📈 Future Improvements

- Smarter highlight scoring (semantic + audio peaks)  
- Multi-channel upload scaling  
- Upload scheduling & rate limiting  
- Analytics-driven clip selection  

---

## 🧠 Author

Built by **Yash Prajapati**  
📎 [LinkedIn](https://www.linkedin.com/in/yash-prajapati-29a423187)  
💻 [GitHub](https://github.com/yash-2304)

---

## ⭐ If you like this project

Give it a star ⭐ — it helps a lot!
