# StreamTube — Scalable Video Streaming Platform

StreamTube is a full-stack video streaming platform inspired by YouTube, built using Django.
It supports video uploads, live streaming, subscriptions, notifications, and email alerts with a focus on scalability and clean architecture.

---

## ✨ Features

- 🎥 Video upload & playback system
- 🔴 Live streaming (WebSocket-based)
- 👥 Channel & subscription system
- 🔔 Real-time + email notifications
- 📝 Post creation (community tab style)
- 💬 Comments & likes system
- 📊 View tracking & engagement metrics
- 📧 Styled HTML email notifications
- 📂 Playlist management

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django, Django Channels |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | SQLite |
| **Real-time** | WebSockets (Channels) |
| **Email Service** | SMTP (Gmail) |

---

## ⚙️ Setup Instructions

Follow these steps to run the project locally.

### 1. Clone Repository

```bash
git clone https://github.com/Shiv-cyber79/streamtube.git
cd streamtube
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Linux / Mac**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

### 7. Open in Browser

- **Main App:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 📧 Email Setup

Update in `settings.py`:

```python
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

> ⚠️ Use Gmail App Password (not your normal password)

---

## 📂 Project Structure

```
streaming_platform/
│
├── users/          # User authentication & profiles
├── videos/         # Video upload, playback, live streaming
├── templates/      # HTML templates
├── media/          # Uploaded media files
├── static/         # Static assets (CSS, JS)
└── manage.py
```

---

## 🔔 Notifications

- Stored in database
- Email notifications sent on:
  - Video upload
  - Post creation
  - Live streaming

---

## 🔴 Live Streaming

- Implemented using Django Channels
- Real-time WebSocket communication

> **Note:** Production setup requires RTMP/CDN integration

---

## 📊 Limitations

- Media files stored locally
- WebSocket scaling limited
- No CDN integration

---

## 🚀 Future Improvements

- Recommendation system
- Analytics dashboard
- Monetization system (Ads, SuperChat)
- CDN + RTMP streaming
- Docker deployment

---

## 📌 Note

This project is designed with a modular structure and can be extended into a production-grade streaming platform.
