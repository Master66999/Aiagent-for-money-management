def calculate_tax(income):
    # Backward compatibility wrapper for old single tax calculator (New Regime estimate)
    res = calculate_old_vs_new_tax(income, 0, 0, 0, 0, 0)
    return res["new_tax"]

def calculate_old_vs_new_tax(income, deductions_80c=0, deductions_80d=0, hra=0, home_loan_interest=0, other_deductions=0):
    income = float(income)
    
    # ---------------------------------------------
    # 1. NEW REGIME TAX COMPUTATION (FY 2024-25 / FY 2025-26)
    # ---------------------------------------------
    std_deduction_new = 75000.0 # Standard deduction in New Regime
    taxable_new = max(0.0, income - std_deduction_new)
    
    new_slabs = [
        {"limit": 300000, "rate": 0.0},
        {"limit": 600000, "rate": 0.05},
        {"limit": 900000, "rate": 0.10},
        {"limit": 1200000, "rate": 0.15},
        {"limit": 1500000, "rate": 0.20},
        {"limit": float('inf'), "rate": 0.30}
    ]
    
    new_tax = 0.0
    temp_taxable = taxable_new
    prev_limit = 0
    slab_breakdown_new = []
    
    for slab in new_slabs:
        limit = slab["limit"]
        rate = slab["rate"]
        
        if temp_taxable > 0:
            taxable_in_slab = min(temp_taxable, limit - prev_limit)
            tax_in_slab = taxable_in_slab * rate
            new_tax += tax_in_slab
            temp_taxable -= taxable_in_slab
            
            slab_breakdown_new.append({
                "slab": f"₹{prev_limit//1000}K - " + (f"₹{limit//1000}K" if limit != float('inf') else "Above"),
                "rate": f"{int(rate*100)}%",
                "tax": round(tax_in_slab, 2)
            })
            prev_limit = limit
        else:
            break
            
    # Rebate under section 87A for New Regime (Taxable Income <= 7,00,000 -> Tax rebate up to 25k)
    if taxable_new <= 700000.0:
        new_tax = 0.0
        for sb in slab_breakdown_new:
            sb["tax"] = 0.0
            
    cess_new = new_tax * 0.04
    total_new_tax = round(new_tax + cess_new, 2)

    # ---------------------------------------------
    # 2. OLD REGIME TAX COMPUTATION
    # ---------------------------------------------
    std_deduction_old = 50000.0
    cap_80c = min(float(deductions_80c), 150000.0)
    cap_80d = min(float(deductions_80d), 50000.0)
    cap_home_loan = min(float(home_loan_interest), 200000.0)
    cap_other = min(float(other_deductions), 50000.0) # NPS 80CCD(1B)
    
    total_deductions_old = std_deduction_old + cap_80c + cap_80d + float(hra) + cap_home_loan + cap_other
    taxable_old = max(0.0, income - total_deductions_old)
    
    old_slabs = [
        {"limit": 250000, "rate": 0.0},
        {"limit": 500000, "rate": 0.05},
        {"limit": 1000000, "rate": 0.20},
        {"limit": float('inf'), "rate": 0.30}
    ]
    
    old_tax = 0.0
    temp_taxable = taxable_old
    prev_limit = 0
    slab_breakdown_old = []
    
    for slab in old_slabs:
        limit = slab["limit"]
        rate = slab["rate"]
        
        if temp_taxable > 0:
            taxable_in_slab = min(temp_taxable, limit - prev_limit)
            tax_in_slab = taxable_in_slab * rate
            old_tax += tax_in_slab
            temp_taxable -= taxable_in_slab
            
            slab_breakdown_old.append({
                "slab": f"₹{prev_limit//1000}K - " + (f"₹{limit//1000}K" if limit != float('inf') else "Above"),
                "rate": f"{int(rate*100)}%",
                "tax": round(tax_in_slab, 2)
            })
            prev_limit = limit
        else:
            break
            
    # Rebate under section 87A for Old Regime (Taxable Income <= 5,00,000 -> Tax rebate up to 12.5k)
    if taxable_old <= 500000.0:
        old_tax = 0.0
        for sb in slab_breakdown_old:
            sb["tax"] = 0.0
            
    cess_old = old_tax * 0.04
    total_old_tax = round(old_tax + cess_old, 2)
    
    # ---------------------------------------------
    # 3. OPTIMIZATION DECISION & COMPARISON
    # ---------------------------------------------
    savings = round(abs(total_old_tax - total_new_tax), 2)
    recommended = "New Regime" if total_new_tax < total_old_tax else "Old Regime"
    if total_new_tax == total_old_tax:
        recommended = "Both Regimes are identical"
        
    return {
        "gross_income": income,
        "standard_deduction_old": std_deduction_old,
        "total_deductions_old": total_deductions_old,
        "taxable_income_old": taxable_old,
        "old_tax_without_cess": round(old_tax, 2),
        "cess_old": round(cess_old, 2),
        "old_tax": total_old_tax,
        "slab_breakdown_old": slab_breakdown_old,
        
        "standard_deduction_new": std_deduction_new,
        "taxable_income_new": taxable_new,
        "new_tax_without_cess": round(new_tax, 2),
        "cess_new": round(cess_new, 2),
        "new_tax": total_new_tax,
        "slab_breakdown_new": slab_breakdown_new,
        
        "recommended": recommended,
        "savings": savings
    }