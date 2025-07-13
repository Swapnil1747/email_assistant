# Intelligent Email Management System using AI

An intelligent assistant that reads your Gmail, auto-replies to emails, schedules meetings, and summarizes your inbox using AI.

---

## ✨ Project Description

This AI Email Assistant automates your email workflow:
- 📥 Fetches unread emails
- ✉️ Auto-replies using an AI model
- 🧠 Summarizes email content
- 📅 Detects meeting dates and schedules Google Calendar events
- ✅ Sends Slack notifications (optional)

Built using **Streamlit**, **Gmail API**, **Google Calendar API**, and **Gemini/GPT AI Models**.

---

## 🚀 Features

- 📥 Fetch unread emails automatically  
- ✉️ Auto-generate replies using AI  
- 🧠 Summarize long emails using LLMs  
- 📅 Extract dates/times and schedule meetings automatically  
- 📊 Dashboard to view emails, replies, and meetings  
- ⚙️ Settings to control AI creativity, timezone, auto-reply toggle  
- ✅ Optional Slack notification integration  

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Rajjuram/MyProject.git
cd ai-email-assistant

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

🔐 Environment Variables
Create a .env file in the root directory and add the following:

env
Copy
Edit
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OPENAI_API_KEY=your-openai-or-gemini-api-key
SLACK_WEBHOOK_URL=your-slack-webhook-url  # Optional

▶️ Usage
To run the Streamlit application:

bash
Copy
Edit
streamlit run app.py
Authenticate with your Gmail and Google Calendar accounts when prompted.

🔄 How It Works
🔐 Authenticate once with Gmail & Calendar API

📥 Fetch new unread emails into the local database

🧠 AI Model summarizes the emails

✉️ Auto-reply generated smartly

📅 If datetime found, event scheduled automatically on Calendar

📊 Dashboard tracks emails, replies, and scheduled meetings

Architecture:
![Architecture](https://github.com/user-attachments/assets/ed0cfbb1-b717-4b5e-bd41-7a5930ed77cf)

Entire Project Functionality:
![AI Email Assistant Workflow Diagram](https://github.com/user-attachments/assets/0c125853-63fb-406d-83e9-b14024bbac34)

🧰 Tech Stack
Python 3.10+

Streamlit

Gmail API

Google Calendar API

Gemini / GPT (LLM)

spaCy, dateparser (for NLP & datetime parsing)

Plotly (for visualizations)

SQLite (for local storage)

Slack API (for notifications)

DuckDuckGo Search API (for question answering)

Screenshots

Dashboard:
![2  Dashboard](https://github.com/user-attachments/assets/1a765c51-4042-4ae0-8954-edcd55bb3a50)

Inbox:
![3  Inbox](https://github.com/user-attachments/assets/8d00f1af-12ac-40bc-904b-3d8ca3ae2a8d)

🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

📜 License
This project is licensed under the MIT License.

🙏 Credits
Streamlit

Google APIs (Gmail + Calendar)

Gemini

DuckDuckGo Search API

spaCy, dateparser

Plotly

Slack SDK

---

Let me know if you'd like it saved as a `.md` file or want help creating a project logo or badge set for GitHub!
