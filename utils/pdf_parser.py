import pdfplumber
import os
import json
from groq import Groq

def extract_income(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        return {"error": f"Failed to read PDF file: {str(e)}"}

    if not text.strip():
        return {"error": "PDF uploaded is empty or couldn't be read."}

    # Retrieve Groq Key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "YOUR_API_KEY":
        # Realistic simulated extraction for demo when no API Key is available
        simulated = {
            "income": 1250000.0,
            "hra": 96000.0,
            "pf": 64000.0,
            "tax_deducted": 45000.0,
            "deductions_80c": 120000.0,
            "employer_name": "Acme Innovations Ltd",
            "financial_year": "2024-25",
            "is_simulated": True,
            "raw_snippet": text[:300] + "..." if len(text) > 300 else text
        }
        return simulated

    try:
        client = Groq(api_key=groq_api_key)
        
        system_prompt = (
            "You are a highly precise document extraction AI. Your task is to analyze financial text extracted from "
            "Form 16 or a Salary Slip and extract critical metrics. Return ONLY a valid, minified JSON object with the "
            "following keys: 'income' (float, annual gross salary if stated, or monthly multiplied by 12), "
            "'hra' (float, HRA/Rent Allowances, annual), 'pf' (float, PF/Provident Fund), 'tax_deducted' (float, TDS/Tax deducted), "
            "'deductions_80c' (float, other 80C investments like ELSS, LIC, PPF, excluding PF if already counted), "
            "'employer_name' (string), 'financial_year' (string). "
            "Do not include any formatting, markdown wrappers, backticks, or conversational text. Return only the JSON."
        )
        
        user_prompt = f"Extracted Text:\n\n{text[:5000]}" # Truncate to save token window
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )
        
        raw_reply = res.choices[0].message.content.strip()
        
        # Clean any accidental markdown codeblock formatting if Llama outputted them
        if raw_reply.startswith("```json"):
            raw_reply = raw_reply[7:]
        if raw_reply.startswith("```"):
            raw_reply = raw_reply[3:]
        if raw_reply.endswith("```"):
            raw_reply = raw_reply[:-3]
            
        parsed_data = json.loads(raw_reply.strip())
        parsed_data["is_simulated"] = False
        parsed_data["raw_snippet"] = text[:300] + "..." if len(text) > 300 else text
        
        return parsed_data
        
    except Exception as e:
        print("PDF GROQ PARSER ERROR:", e)
        # Safe fallback in case of JSON parse or connection failure
        return {
            "income": 1250000.0,
            "hra": 96000.0,
            "pf": 64000.0,
            "tax_deducted": 45000.0,
            "deductions_80c": 120000.0,
            "employer_name": "Acme Innovations Ltd",
            "financial_year": "2024-25",
            "is_simulated": True,
            "error_fallback": str(e),
            "raw_snippet": text[:300] + "..." if len(text) > 300 else text
        }