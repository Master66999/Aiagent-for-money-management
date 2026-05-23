import os
import re
from groq import Groq

def calculate_monthly_investment(target, years, current, rate):
    # Monthly rate and total months
    r = rate / 100 / 12
    n = years * 12
    
    # Future value of current savings
    fv_current = current * ((1 + (rate / 100)) ** years)
    
    if fv_current >= target:
        return 0.0, round(fv_current, 2), 0.0
    
    gap = target - fv_current
    
    # SIP annuity formula: FV = P * [((1 + r)^n - 1) / r] * (1 + r)
    # P = FV / ([((1 + r)^n - 1) / r] * (1 + r))
    if r == 0:
        monthly = gap / n
    else:
        multiplier = (((1 + r) ** n - 1) / r) * (1 + r)
        monthly = gap / multiplier
        
    return round(monthly, 2), round(fv_current, 2), round(gap, 2)

def generate_goal_strategy(goal_title, target_amount, target_years, current_savings, risk_profile):
    # Determine expected rate and portfolio allocation based on risk
    risk_profile = risk_profile.lower()
    if risk_profile == "conservative":
        rate = 7.0
        allocation = "80% Debt, 20% Equity"
        details = "Mainly focused on safety, capital preservation, and low-volatility returns through Debt Mutual Funds, FDs, and Gold."
    elif risk_profile == "aggressive":
        rate = 15.0
        allocation = "80% Equity, 15% Debt, 5% Alternate/Crypto"
        details = "High-growth approach using Mid/Small-cap equity mutual funds, direct stocks, and high-yield instruments to maximize compounding."
    else:  # moderate
        rate = 12.0
        allocation = "60% Equity, 30% Debt, 10% Gold"
        details = "Balanced wealth generation with a healthy mix of Large-cap index funds, Flexi-cap mutual funds, Corporate bonds, and Gold ETFs."

    monthly, fv_current, gap = calculate_monthly_investment(target_amount, target_years, current_savings, rate)

    # Let's format raw numbers for standard Indian display
    def format_rupee(val):
        return f"₹{val:,.2f}"

    # Query Groq to get a professional, highly detailed, personalized plan
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "YOUR_API_KEY":
        # Graceful fallback response
        ai_roadmap = f"""### 🎯 Personal Finance Goal Roadmap: **{goal_title.upper()}**

Based on your profile, we have structured a high-fidelity **{risk_profile.capitalize()}** investment plan.

#### 📊 Allocation Details ({allocation})
- **Equity (Growth Basket):** Focus on Large-Cap and Flexi-Cap Index Mutual Funds for long-term inflation-beating returns.
- **Debt (Stability Basket):** Allocate to High-Quality Corporate Bond Funds or Arbitrage Funds for safety and immediate liquidity.
- **Gold & Alternates:** Use Sovereign Gold Bonds (SGBs) or Gold ETFs to hedge against equity market downturns.

#### 📝 Action Plan
1. **Current Savings Growth:** Your current savings of {format_rupee(current_savings)} will compound at **{rate}% p.a.** to reach **{format_rupee(fv_current)}** in {target_years} years.
2. **Monthly SIP Commitment:** To bridge the remaining gap of **{format_rupee(gap)}**, you need to start a monthly investment of **{format_rupee(monthly)}**.
3. **Emergency Fund Guard:** Ensure you have 6 months of expenses parked in liquid funds before committing to this long-term SIP.
4. **Annual Step-up:** We recommend stepping up your monthly savings by **10% annually** as your income grows to achieve this goal even faster!
"""
    else:
        try:
            client = Groq(api_key=groq_api_key)
            prompt = f"""
            Goal Name: {goal_title}
            Target Amount: INR {target_amount}
            Investment Horizon: {target_years} years
            Current Savings: INR {current_savings}
            Expected Annual Growth: {rate}% (Risk Profile: {risk_profile})
            Calculated Monthly Contribution Required: INR {monthly}
            Current Savings Future Value: INR {fv_current}
            Remaining Gap to Fund: INR {gap}
            Portfolio Allocation Target: {allocation} ({details})

            As an expert Indian financial planner, write a highly actionable, beautiful markdown investment roadmap. Include:
            1. Recommended fund categories (e.g. Large Cap, Mid Cap, Debt Mutual Funds, Gold ETFs).
            2. Concrete steps to deploy the monthly SIP.
            3. Tax optimization suggestions (e.g. ELSS for 80C, capital gains harvesting rules in India).
            4. Emergency fund and insurance safeguards.
            Keep the tone professional, encouraging, and clear. Format output in gorgeous markdown.
            """
            
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a senior Wealth Manager and Personal Finance Advisor in India."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_roadmap = res.choices[0].message.content
        except Exception as e:
            ai_roadmap = f"*(Groq API Error: {str(e)})*\n\n**Fallback Strategy:**\nTo achieve your goal of **{goal_title}**, allocate your **{format_rupee(monthly)}** monthly investment into: **{allocation}** ({details}). This will comfortably cover your deficit of **{format_rupee(gap)}** over the next **{target_years} years**."

    return {
        "monthly_required": monthly,
        "current_fv": fv_current,
        "gap": gap,
        "expected_rate": rate,
        "allocation": allocation,
        "roadmap": ai_roadmap
    }
