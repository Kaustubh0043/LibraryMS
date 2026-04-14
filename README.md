# ALeX - Modern Library Management System (Django 5)

ALeX is a premium, high-performance Library Management System designed with a focus on aesthetics and user experience. It features a fully responsive design, fluid animations, and a rich feature set for both students and administrators.

![ALeX Logo](static/img/alex_logo_v2.png)

## ✨ Features

### 🎨 Premium UI & Experience
- **Fluid Dark/Light Mode**: Seamless manual theme switching with bulletproof contrast and visibility.
- **Glassmorphic Design**: Modern transparent card layouts and high-end typography.
- **Micro-Animations**: Scroll-reveal effects and interactive transitions (AOS-style).
- **Dynamic Logos**: Auto-switching logo video-to-image transitions for a premium brand feel.

### 📚 Core Library Logic
- **Smart Catalog**: Advanced search by book title, author, department, and semester.
- **Smart Thumbnails**: Intelligent cover loading system using uploaded files, URL fallbacks, or dynamic placeholders.
- **Transaction Workflow**: Issue and return requests with clear status tracking (Pending, Issued, Overdue, etc.).
- **UPI Fine Management**: Integrated Razorpay UPI payment gateway for real-time fine clearance.

### 🛠️ Advanced Modules
- **Dynamic Syllabus Notification**: Configurable alert popups for university-level updates.
- **Interactive Feedback**: Emoji-based rating system for continuous library improvement.
- **Contact & Support**: Secure contact forms saved directly to the database and accessible via admin panel.
- **Portfolio About Page**: Integrated certifications gallery and technical skills portfolio.
- **Admin Intelligence Suite**: Dedicated user tracking, global transaction logs, and deep-dive history views.
- **High-Contrast Reader**: Specialized Cyber-Amber & Cyan color palette for superior readability in dark mode.

## 🚀 Quick Setup

### 1. Environment Configuration
```bash
# Clone the repository
git clone https://github.com/YourUsername/LibraryMS.git
cd LibraryMS

# Setup Virtual Environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Install Dependencies
pip install -r requirements.txt
```

### 2. Database & Assets
```bash
# Apply Migrations
python manage.py migrate

# Preload Academic Catalog (Optional)
python manage.py load_engineering_books

# Create Admin Account
python manage.py createsuperuser

# Start Server
python manage.py runserver
```

### 3. Secretary Configuration (.env)
Create a `.env` file in the root directory based on `.env.example`:
```ini
DEBUG=True
SECRET_KEY=your_secret_key
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
DAILY_FINE_INR=10
LOAN_DAYS=14
```

## 🔐 Security & Privacy
This repository is pre-configured with a robust `.gitignore` to prevent leakage of:
- SQLite Database (`db.sqlite3`)
- Environment variables (`.env`)
- Local media assets and certificates
- Python cached files and IDE settings

---
Built with ❤️ by **Kaustubh Jadhav**  
*CSE Student at Alard University, Pune*
