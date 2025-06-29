# 🚨 Profanity Detection in Filipino Social Media Comments Using Transformer-Based NLP Models

This project is part of my undergraduate thesis at **New Era University**, aiming to detect and classify profanity in Filipino (Tagalog) social media comments using transformer-based models like **BERT**, **XLNet**, and **ELECTRA**.

---

## 📘 Abstract

The rise of offensive and harmful language in online spaces, particularly on social media platforms, highlights the need for a robust profanity detection system tailored for the Filipino language. This study proposes a transformer-based NLP model that classifies the severity of profane comments into **non-profane**, **mild**, **moderate**, and **high** categories. The model was trained on annotated Tagalog datasets and integrated with APIs for real-time applications like Reddit bots and chat moderation.

---

## ⚙️ Technologies Used

- 🧠 **Transformers**: BERT, XLNet, ELECTRA (via Hugging Face Transformers)
- 💻 **Python**, **PyTorch**, **Scikit-learn**
- 📊 **Pandas**, **NumPy**, **Matplotlib**
- 🔤 **CalamanCy** (POS tagging for Tagalog)
- 🌐 **Flask** – for API and web integration
- 📡 **PRAW API** – Reddit comment integration

---

## 🧪 Features

- 🔍 Detects profane content in Tagalog/Filipino text
- 🚨 Classifies profanity into 4 severity levels:
  - Non-Profane
  - Mild
  - Moderate
  - High
- 🧼 Automatically censors or flags offensive content
- 🤖 Reddit Bot integration for live moderation
- 💬 Streamlit-based Tagalog chatbot with profanity filtering

