# 🚀 Deployment Guide

This guide will help you deploy the **Shanghai Metals Cost Analysis** app to the web using **Streamlit Community Cloud** (free).

## Prerequisites
1.  **GitHub Account**: You need a GitHub account to host the code.
2.  **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/) using your GitHub account.

## Step 1: Upload Code to GitHub
1.  Create a **new repository** on GitHub (e.g., `metal-cost-app`).
2.  Upload all project files to this repository:
    - `app.py`
    - `requirements.txt`
    - `assets/` folder
    - `views/` folder
    - `utils/` folder
    - `run_app.bat` (optional)

## Step 2: Deploy on Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io/).
2.  Click **"New app"**.
3.  Select your repository (`metal-cost-app`), branch (`main`), and main file (`app.py`).
4.  Click **"Deploy!"**.

## Step 3: Configure Secrets (Passwords)
Your app checks `st.secrets["password"]`. By default it uses "admin123" if no secret is set, but for security you should set it online.

1.  On your deployed app dashboard in Streamlit Cloud, go to **Settings** -> **Secrets**.
2.  Add the following content:
    ```toml
    password = "YOUR_SECURE_PASSWORD"
    ```
3.  Save. The app will restart and use this new password.

## Troubleshooting
- **"ModuleNotFoundError"**: Ensure `requirements.txt` lists all libraries (`streamlit`, `pandas`).
- **"KeyError: password"**: If you removed the default fallback in `utils/auth.py`, you MUST set the secret. Currently, it defaults to `admin123`.

---
**Your app is now online!** 🌍
