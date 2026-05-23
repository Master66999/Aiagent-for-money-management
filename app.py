from flask import Flask, request, jsonify, render_template
import yfinance as yf
import os
from groq import Groq

# ---------------- 🔐 SET API KEY ----------------
# ---------------- 🔐 SET API KEY ----------------
if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "YOUR_API_KEY":
    os.environ["GROQ_API_KEY"] = "YOUR_API_KEY"

# ---------------- IMPORT UTILS ----------------
from utils.sip import calculate_sip
from utils.tax import calculate_tax, calculate_old_vs_new_tax
from utils.pdf_parser import extract_income
from utils.money_score import calculate_money_score
from utils.multi_agent import run_multi_agent
from utils.goal_planner import generate_goal_strategy
from utils.fire_planner import simulate_fire

app = Flask(__name__)

# ---------------- INIT GROQ ----------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("landing.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


# ---------------- 🤖 AI CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        msg = request.json.get("message")

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a financial advisor for India."},
                {"role": "user", "content": msg}
            ]
        )

        return jsonify({"reply": res.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})


# ---------------- 💸 SIP ----------------
@app.route("/sip", methods=["POST"])
def sip():
    try:
        data = request.json
        result = calculate_sip(
            float(data["monthly"]),
            float(data["rate"]),
            int(data["years"])
        )
        return jsonify({"future_value": result})

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 📊 STOCK ----------------
@app.route("/portfolio", methods=["POST"])
def portfolio():
    try:
        stock = request.json["stock"].upper()

        # Add .NS for Indian stocks (important!)
        if not stock.endswith(".NS"):
            stock = stock + ".NS"

        data = yf.Ticker(stock)
        hist = data.history(period="5d")

        if hist.empty:
            return jsonify({"error": "Invalid stock symbol"})

        price = hist["Close"].iloc[-1]

        return jsonify({"price": round(price, 2)})

    except Exception as e:
        return jsonify({"error": str(e)})
    
# ---------------- 💸 TAX ----------------
@app.route("/tax", methods=["POST"])
def tax():
    try:
        income = float(request.json["income"])
        return jsonify({"tax": calculate_tax(income)})

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 💸 TAX COMPARISON ----------------
@app.route("/tax-compare", methods=["POST"])
def tax_compare():
    try:
        data = request.json
        result = calculate_old_vs_new_tax(
            float(data["income"]),
            float(data.get("deductions_80c", 0)),
            float(data.get("deductions_80d", 0)),
            float(data.get("hra", 0)),
            float(data.get("home_loan_interest", 0)),
            float(data.get("other_deductions", 0))
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 🎯 GOALS ----------------
@app.route("/goals", methods=["POST"])
def goals():
    try:
        data = request.json
        result = generate_goal_strategy(
            data["title"],
            float(data["target_amount"]),
            float(data["target_years"]),
            float(data.get("current_savings", 0)),
            data.get("risk_profile", "moderate")
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 🔥 FIRE PLANNER ----------------
@app.route("/fire-calc", methods=["POST"])
def fire_calc():
    try:
        data = request.json
        result = simulate_fire(
            int(data["current_age"]),
            int(data["target_retire_age"]),
            float(data["monthly_expenses"]),
            float(data.get("current_net_worth", 0)),
            float(data.get("annual_savings", 0)),
            float(data.get("expected_return_pre", 12)),
            float(data.get("expected_return_post", 8)),
            float(data.get("inflation_rate", 6))
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 📄 PDF ----------------
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        result = extract_income(file)
        return jsonify({"data": result})

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 🧠 MULTI AGENT ----------------
@app.route("/agent", methods=["POST"])
def run_agent_route():
    try:
        query = request.json["query"]
        response = run_multi_agent(query)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- 💰 MONEY SCORE ----------------
@app.route("/money-score", methods=["POST"])
def money_score():
    try:
        data = request.json

        score = calculate_money_score(
            float(data["income"]),
            float(data["expenses"]),
            float(data["savings"]),
            float(data["investments"]),
            float(data["debt"]),
            float(data["emergency"])
        )

        if score >= 80:
            status = "Excellent 💚"
        elif score >= 60:
            status = "Good 👍"
        elif score >= 40:
            status = "Average ⚠️"
        else:
            status = "Needs Improvement ❌"

        return jsonify({
            "score": score,
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
