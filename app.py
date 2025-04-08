"""
Created by Andre McLean
ID: 20211523
Date: April 8th, 2025

Smart Money GPT - Flask backend using LangChain, Chroma DB, and FLAN-T5 for financial Q&A and budgeting assistant.
"""

# ==== Flask + LangChain + Transformers Imports ====
from flask import Flask, render_template, request, jsonify, session
from langchain.chains import ConversationalRetrievalChain
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.memory import ConversationBufferWindowMemory
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import re

# ==== Flask App Setup ====
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session persistence

# ==== Vectorstore Setup ====
# Load Chroma vector DB with HuggingFace embeddings
vectorstore = Chroma(
    persist_directory="db",
    embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)
retriever = vectorstore.as_retriever()

# ==== Load Language Model (FLAN-T5) ====
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=150,
    truncation=True
)
llm = HuggingFacePipeline(pipeline=pipe)

# ==== Session Memory Setup ====
chat_memory = {}

# Manage per-user memory using a buffer of recent messages (k = 10 exchanges)
def get_memory_for_user(user_id):
    if user_id not in chat_memory:
        chat_memory[user_id] = ConversationBufferWindowMemory(
            memory_key="chat_history", return_messages=True, k=10
        )
    return chat_memory[user_id]

# ==== Home Page Route ====
@app.route("/")
def home():
    return render_template("index.html")

# ==== Salary Calculation ====
def calculate_salary_from_input(question, previous_data=None):
    # Extract hourly rate
    match = re.search(r"\$?(\d+(\.\d+)?)\s*(per hour|hourly)", question, re.IGNORECASE)
    hourly_rate = float(match.group(1)) if match else (previous_data.get("hourly") if previous_data else None)

    # Extract hours per week or fall back to 40
    try:
        hours_per_week = int(re.search(r"(\d+)\s*(hours|hrs).*?week", question, re.IGNORECASE).group(1))
    except:
        hours_per_week = previous_data.get("hours_per_week", 40) if previous_data else 40

    # Return salary breakdown
    if hourly_rate:
        weekly = hourly_rate * hours_per_week
        annual = weekly * 52
        monthly = annual / 12
        return {
            "hourly": round(hourly_rate, 2),
            "weekly": round(weekly, 2),
            "monthly": round(monthly, 2),
            "annual": round(annual, 2),
            "hours_per_week": hours_per_week
        }
    return None

# ==== Calculate After-Tax Monthly Salary ====
def calculate_after_tax(monthly, tax_rate=0.2):
    return round(monthly * (1 - tax_rate), 2)

# ==== Calculate Budget Breakdown ====
def calculate_budget(income, savings_percent=0.2):
    savings = round(income * savings_percent, 2)
    remaining = income - savings
    return {
        "savings": savings,
        "rent": round(remaining * 0.4, 2),
        "groceries": round(remaining * 0.3, 2),
        "other": round(remaining * 0.3, 2)
    }

# ==== Calculate Monthly Savings to Reach Goal ====
def calculate_monthly_savings(goal, months=12):
    try:
        return round(goal / months, 2)
    except ZeroDivisionError:
        return None

# ==== Extract Dollar Amount from Text ====
def extract_number_from_text(text):
    match = re.search(r"\$?(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None

# ==== Parse Questions About Saving Goals ====
def parse_savings_goal(question):
    match = re.search(r"save\s*\$?(\d+(?:\.\d+)?)\s*(in|within)?\s*(\d+)\s*(months|month)", question, re.IGNORECASE)
    if match:
        total_goal = float(match.group(1))
        months = int(match.group(3))
        monthly_savings = round(total_goal / months, 2)
        return total_goal, months, monthly_savings
    return None, None, None

# ==== Main Chat Endpoint ====
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").strip()
    if not user_question:
        return jsonify({"error": "No valid question received"}), 400

    # Manage session + memory
    user_id = session.get("user_id", str(id(session)))
    session["user_id"] = user_id
    memory = get_memory_for_user(user_id)

    previous_salary = session.get("salary_data", {})

    # Determine intent type
    is_salary_q = any(k in user_question.lower() for k in ["per hour", "hourly", "wage", "salary", "annual", "weekly", "monthly", "income"])
    is_budget_q = "budget" in user_question.lower() or "allocate" in user_question.lower()
    is_custom_hours_q = "hours per week" in user_question.lower() or "what if i work" in user_question.lower()
    is_partial_period_q = "6 months" in user_question.lower()

    # Savings goal query
    total_goal, months, monthly_savings = parse_savings_goal(user_question)
    if total_goal:
        response = (
            f"To save ${total_goal} in {months} months, you need to save about:\n"
            f"💰 ${monthly_savings} per month."
        )
        return jsonify({"answer": response})

    # Custom work hours query
    if is_custom_hours_q:
        try:
            hours_per_week = int(re.search(r"(\d+)\s*(hours|hrs).*?week", user_question, re.IGNORECASE).group(1))
            previous_salary["hours_per_week"] = hours_per_week
            new_salary = calculate_salary_from_input("", previous_salary)
            session["salary_data"] = new_salary
            response = (
                f"Based on ${new_salary['hourly']} per hour and {new_salary['hours_per_week']} hours/week:\n"
                f"🗓️ Weekly: ${new_salary['weekly']}\n"
                f"📅 Monthly: ${new_salary['monthly']}\n"
                f"📈 Annual: ${new_salary['annual']}\n"
                f"💸 Monthly After Tax (20%): ${calculate_after_tax(new_salary['monthly'])}"
            )
            return jsonify({"answer": response})
        except Exception as e:
            print(f"ERROR: {e}")
            return jsonify({"error": "Something went wrong while calculating custom hours per week."}), 500

    # Income over 6 months
    if is_partial_period_q:
        try:
            months = 6
            if previous_salary:
                total_earnings = round(previous_salary["monthly"] * months, 2)
                after_tax = round(calculate_after_tax(previous_salary["monthly"]) * months, 2)
                response = (
                    f"In {months} months, you'd earn:\n"
                    f"💰 Total Before Tax: ${total_earnings}\n"
                    f"💸 Total After Tax (20%): ${after_tax}"
                )
                return jsonify({"answer": response})
            else:
                return jsonify({"answer": "I need your salary details to calculate earnings for 6 months. Please share your hourly rate or salary information."})
        except Exception as e:
            print(f"ERROR: {e}")
            return jsonify({"error": "Something went wrong while calculating earnings for 6 months."}), 500

    # General salary query
    if is_salary_q:
        salary = calculate_salary_from_input(user_question, previous_salary)
        if salary:
            session["salary_data"] = salary
            response = (
                f"Based on ${salary['hourly']} per hour and {salary['hours_per_week']} hours/week:\n"
                f"🗓️ Weekly: ${salary['weekly']}\n"
                f"📅 Monthly: ${salary['monthly']}\n"
                f"📈 Annual: ${salary['annual']}\n"
                f"💸 Monthly After Tax (20%): ${calculate_after_tax(salary['monthly'])}"
            )
            return jsonify({"answer": response})

    # Monthly budget query
    if is_budget_q:
        monthly_income = previous_salary.get("monthly", 0)
        if monthly_income > 0:
            budget = calculate_budget(monthly_income)
            response = (
                f"💸 Monthly Budget (on ${monthly_income}):\n"
                f"💰 Savings: ${budget['savings']}\n"
                f"🏠 Rent: ${budget['rent']}\n"
                f"🛒 Groceries: ${budget['groceries']}\n"
                f"📦 Other: ${budget['other']}"
            )
            return jsonify({"answer": response})
        else:
            return jsonify({"answer": "I need your monthly income to create a budget. Please share it."})

    # General fallback: LangChain LLM
    try:
        qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)
        result = qa.invoke({"question": user_question})
        return jsonify({"answer": result["answer"]})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": "Something went wrong."}), 500

# Global error handler for debugging
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"ERROR: {e}")
    return jsonify({"error": "Something went wrong. Please try again or clarify your query."}), 500

# ==== needed to run flask app====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
