import os
from groq import Groq

def simulate_fire(current_age, target_retire_age, monthly_expenses, current_net_worth, annual_savings, expected_return_pre, expected_return_post, inflation_rate):
    age = current_age
    net_worth = current_net_worth
    savings = annual_savings
    annual_exp = monthly_expenses * 12
    
    pre_rate = expected_return_pre / 100
    post_rate = expected_return_post / 100
    inf_rate = inflation_rate / 100
    
    years_to_retire = max(0, target_retire_age - current_age)
    
    # 1. Calculate FIRE Milestones (in today's values)
    # Standard FIRE Number is 25x annual expenses (4% rule)
    std_fire_today = annual_exp * 25
    lean_fire_today = annual_exp * 20 # 20x expenses (5% withdrawal)
    fat_fire_today = annual_exp * 30 # 30x expenses (3.3% withdrawal)
    
    # Target FIRE number adjusted for inflation at retirement year
    std_fire_retirement = std_fire_today * ((1 + inf_rate) ** years_to_retire)
    
    # Real rate of return pre-retirement (Fisher equation approximation: r_real = r_nom - inflation)
    real_rate_pre = pre_rate - inf_rate
    coast_fire_today = std_fire_today / ((1 + real_rate_pre) ** years_to_retire) if years_to_retire > 0 else std_fire_today
    
    # 2. Year by year simulation from current age to age 85
    timeline = []
    ran_out_age = None
    net_worth_at_retirement = 0.0
    
    for year in range(current_age, 86):
        # Record current state
        timeline.append({
            "age": year,
            "net_worth": round(net_worth, 2),
            "annual_expenses": round(annual_exp, 2),
            "annual_savings": round(savings if year < target_retire_age else 0.0, 2)
        })
        
        if year == target_retire_age:
            net_worth_at_retirement = net_worth
        
        # Calculate next year's values
        if year < target_retire_age:
            # Active working phase
            net_worth = net_worth * (1 + pre_rate) + savings
            savings = savings * (1 + inf_rate) # savings grow with inflation
        else:
            # Retired phase
            net_worth = (net_worth - annual_exp) * (1 + post_rate)
            if net_worth < 0 and ran_out_age is None:
                ran_out_age = year
                
        # Expenses inflate every year
        annual_exp = annual_exp * (1 + inf_rate)
        
    def format_rupee(val):
        if val >= 10000000:
            return f"₹{val/10000000:.2f} Cr"
        elif val >= 100000:
            return f"₹{val/10000:.2f} L"
        else:
            return f"₹{val:,.2f}"

    # 3. AI Advisor Review
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    plan_status = "Solid"
    if ran_out_age and ran_out_age < 80:
        plan_status = "High Risk ⚠️"
    elif net_worth_at_retirement >= std_fire_retirement:
        plan_status = "Excellent 💚"
    else:
        plan_status = "Undersaved ⚠️"
        
    if not groq_api_key or groq_api_key == "YOUR_API_KEY":
        if plan_status == "Excellent 💚":
            ai_advice = f"""### 🚀 FIRE Evaluation: **EXCELLENT PLAN**
            
Your current retirement strategy is incredibly robust. By age **{target_retire_age}**, your expected net worth of **{format_rupee(net_worth_at_retirement)}** comfortably beats your inflation-adjusted FIRE Target of **{format_rupee(std_fire_retirement)}**.

- **CoastFIRE Status:** Verified. Your current net worth of {format_rupee(current_net_worth)} exceeds the CoastFIRE threshold of {format_rupee(coast_fire_today)}.
- **Withdrawal Safety:** Your post-retirement asset compounding is sufficient to support your lifestyle without running out of money before age 85!
- **Action Item:** Keep compounding. Consider tax-efficient debt sweep accounts to shield gains as you approach retirement.
"""
        elif plan_status == "High Risk ⚠️":
            ai_advice = f"""### ⚠️ FIRE Evaluation: **HIGH RISK DETECTED**
            
Our simulations indicate your corpus will run dry at **age {ran_out_age}**. 

- **The Problem:** Expected retirement expenses (adjusted for inflation) outpace your post-retirement compounding returns.
- **Differentiator:** Your target retirement net worth **{format_rupee(net_worth_at_retirement)}** is below the required **{format_rupee(std_fire_retirement)}**.
- **Recommendations:**
  1. Increase your current annual savings of {format_rupee(annual_savings)} by 15-20%.
  2. Shift retirement age to **{target_retire_age + 3}** to let your investments compound longer.
  3. Explore secondary passive income streams in retirement to reduce capital drawdowns.
"""
        else:
            ai_advice = f"""### 📊 FIRE Evaluation: **AVERAGE / UNDERSAVED**
            
You are on the right track, but there is a marginal gap between your projected corpus (**{format_rupee(net_worth_at_retirement)}**) and your actual FIRE target (**{format_rupee(std_fire_retirement)}**).

- **Current Gap:** Approx. {format_rupee(std_fire_retirement - net_worth_at_retirement)}.
- **Optimization Strategy:** 
  1. Increase your annual standard savings increment to 10% or more.
  2. Reallocate 10% of debt investments into index equities to raise pre-retirement returns slightly.
  3. Leverage standard Indian tax breaks (like Section 80C, NPS) to reduce tax leakage and direct all tax savings back into your compounding portfolio.
"""
    else:
        try:
            client = Groq(api_key=groq_api_key)
            prompt = f"""
            Current Age: {current_age}
            Target Retirement Age: {target_retire_age}
            Monthly Expenses in Retirement (today's value): INR {monthly_expenses}
            Current Net Worth: INR {current_net_worth}
            Annual Savings: INR {annual_savings}
            Expected ROI Pre-Retirement: {expected_return_pre}%
            Expected ROI Post-Retirement: {expected_return_post}%
            Inflation Rate: {inflation_rate}%
            
            Simulated Results:
            - Net Worth at Retirement (nominal): INR {net_worth_at_retirement}
            - Inflation-Adjusted FIRE Number Needed at Retirement: INR {std_fire_retirement}
            - CoastFIRE Required Today: INR {coast_fire_today}
            - Age of depletion (if any): {ran_out_age if ran_out_age else 'Never runs out before 85'}
            
            Provide a deep financial review of this FIRE plan. 
            - Calculate and discuss if the user is CoastFIRE.
            - Address the inflation-adjusted expenses vs return post-retirement.
            - Offer 3 tailored, highly effective financial optimization adjustments (asset allocation, tax optimization like NPS/EPF, side income) for India.
            Keep output formatted in professional and highly readable markdown.
            """
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert financial researcher specializing in FIRE (Financial Independence Retire Early) movements in India."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_advice = res.choices[0].message.content
        except Exception as e:
            ai_advice = f"*(Groq Advisor Error: {str(e)})*\n\n**Calculated Summary:** Net worth at retirement will be **{format_rupee(net_worth_at_retirement)}** (Target needed: **{format_rupee(std_fire_retirement)}**). "
            if ran_out_age:
                ai_advice += f"Warning: Portfolio is projected to deplete at age {ran_out_age}."
            else:
                ai_advice += "Portfolio remains positive up to age 85."

    return {
        "years_to_retire": years_to_retire,
        "std_fire_today": std_fire_today,
        "lean_fire_today": lean_fire_today,
        "fat_fire_today": fat_fire_today,
        "std_fire_retirement": std_fire_retirement,
        "coast_fire_today": coast_fire_today,
        "net_worth_at_retirement": net_worth_at_retirement,
        "ran_out_age": ran_out_age,
        "timeline": timeline,
        "ai_advice": ai_advice
    }
