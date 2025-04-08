# Smart Money GPT

**Created by Andre McLean**  
**ID: 20211523**  
**Date: April 8th, 2025**

---

## 💬 What is Smart Money GPT?

Smart Money GPT is a conversational financial assistant designed to help users make smarter financial decisions by:

- 💰 Calculating salary estimates (hourly, monthly, annual)
- 📊 Creating budgets (rent, savings, groceries, etc.)
- 🎯 Generating savings plans
- 🧠 Answering general finance-related questions using AI and embedded financial documents

It combines:
- **LangChain** for managing conversations and retrieval
- **FLAN-T5** (a Hugging Face model) for generating intelligent responses
- **Chroma Vector DB** for storing and retrieving embedded knowledge from PDF, Excel, and CSV files
- A sleek **Flask web app** interface

---

## 🚀 Features

- 🔄 Multi-turn conversations
- 🧾 PDF, CSV, and Excel-based knowledge retrieval
- 🔍 Semantic search with embeddings (MiniLM-L6-v2)
- 💸 Custom salary calculations with tax estimates
- 📅 Personalized budget and savings advice
- 📚 Integrated with financial literacy documents

---

## 📂 Project Structure

```
Smart-Money-GPT/
├── app.py                     # Flask backend and salary/budget logic
├── templates/
│   └── index.html            # Frontend interface
├── static/
│   └── bg.jpg                # Background image
├── db/                       # Chroma vector database
├── data/                     # Embedded PDF, Excel, and CSV files
├── load_docs.py              # Loads and indexes documents into Chroma
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
```

---

## 🛠️ How to Run Locally

### 1. Clone the Repo
```bash
git clone https://github.com/OfficialAndre/Smart-Money-GPT.git
cd Smart-Money-GPT
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Load the Vector Database
```bash
python load_docs.py
```

### 5. Start the App
```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser to chat with Smart Money GPT.

---

## 🌐 Hosting the App

You **cannot run Flask directly from GitHub**. To make this app live:

### Option 1: [Render.com](https://render.com)
- Supports Flask apps easily
- Free tier available

### Option 2: [Replit](https://replit.com)
- Paste your Flask app
- Add `.replit` and `replit.nix` config files

### Option 3: [Railway](https://railway.app) or [Glitch](https://glitch.com)

Let me know if you'd like help setting it up!

---

## 🔗 Try It Online

To run this project live from GitHub, you need to deploy it to a platform that supports Flask hosting.

You can use:
- **Render**: [Deploy Flask](https://render.com/docs/deploy-flask)
- **Replit**: [Create a new Replit](https://replit.com/~)
- **Glitch**: [Glitch Flask Template](https://glitch.com/edit/#!/remix/flask-starter)

---

## 📜 License

MIT License. Free to use and modify. Just give credit to Andre McLean 💼

---

## 👋 Stay Connected

For questions, collaborations, or support:  
**Email:** andrefmclean@gmail.com  
**GitHub:** [@OfficialAndre](https://github.com/OfficialAndre)

---

Built with 💙 for smarter money decisions!
