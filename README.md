# 💰 AI Money Mentor

🚀 An AI-powered personal finance mentor that helps users manage money, build wealth, and make smarter financial decisions — all in one place.

---

## 📌 Problem Statement

95% of people lack a structured financial plan, while traditional financial advisors are expensive and mostly accessible only to high-net-worth individuals.

AI Money Mentor aims to democratize financial guidance by providing an intelligent, affordable, and always-available solution.

---

## 🎯 Solution

AI Money Mentor is a **24/7 AI-based financial assistant** that:
- Tracks income and expenses
- Provides smart budgeting strategies
- Suggests investment options
- Offers personalized financial advice
- Educates users about finance

---

## ✨ Features

### 🧠 AI Chat Assistant
- Ask finance-related queries
- Get intelligent and personalized responses

### 📊 Expense Tracker
- Track daily income & expenses
- Automatic categorization

### 💡 Smart Budgeting
- AI-generated monthly budget plans
- Spending insights and optimization tips

### 📈 Investment Suggestions
- SIP, stocks, and savings recommendations
- Risk-based financial planning

### 🧾 Financial Reports
- Weekly / Monthly reports
- Spending analysis and trends

### 🔔 Smart Alerts
- Bill reminders
- Overspending notifications

---

## 🏗️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python (Flask)

### AI Integration
- OpenAI API / Groq API (LLM-based chatbot)

### Database (Optional)
- MySQL / SQLite

---

## ⚙️ System Architecture

- User → Frontend UI → Flask Backend → AI Model API
↓
Database


---

## 🔄 Workflow

1. User enters financial data or query  
2. Frontend sends request to backend  
3. Backend processes input  
4. AI model analyzes the request  
5. Response is generated  
6. Output displayed to user  

---

## 📊 Impact

- 📉 Reduces financial illiteracy  
- 💰 Improves saving habits  
- 📈 Enhances investment decisions  
- 🧠 Makes financial planning accessible to everyone  

---

## 🚀 Future Enhancements

- 📱 Mobile App (Android & iOS)  
- 🎙️ Voice-based assistant  
- 🌐 Multi-language support  
- 🏦 Bank API integration  
- 📊 Advanced portfolio tracking  
- 🤖 Multi-agent AI system  

---


## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/omroy07/AI-Money-Mentor.git

# Navigate into the project folder
cd AI-Money-Mentor

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

```

---

## 🔑 API Configuration

This project requires an API key to run. Follow these steps to set up:

### 1. Get Your API Key
- Sign up at [OpenAI](https://platform.openai.com/) or [Groq](https://console.groq.com/)
- Navigate to the API keys section
- Create a new API key

### 2. Set Up Environment Variables
Create a `.env` file in the project root directory:

```bash
# .env
OPENAI_API_KEY=your_api_key_here
# OR
GROQ_API_KEY=your_api_key_here
```

### 3. Ensure the `.env` file is NOT committed to Git
The `.gitignore` file should include `.env` to protect your API keys.

### 4. Run the Application
Once the API key is configured, start the application:

```bash
python app.py
```

The application will load the API key from the environment variables and establish connection with the AI model.

**⚠️ Important:** Never share or commit your API key to version control.
