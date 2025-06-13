import streamlit as st
import pandas as pd
import openai
from datetime import datetime

# ========== USER INPUT FOR API KEY ========== #
st.sidebar.title("🔐 إعدادات API")
user_api_key = st.sidebar.text_input("أدخل مفتاح OpenAI API الخاص بك", type="password")
if not user_api_key:
    st.warning("يرجى إدخال مفتاح OpenAI API في الشريط الجانبي")
    st.stop()
openai.api_key = user_api_key

# ========== FUNCTIONS ========== #
def calculate_end_of_service(start_date, end_date, base_salary):
    years = (end_date - start_date).days / 365.25
    if years <= 5:
        gratuity = 0.5 * base_salary * years
    else:
        gratuity = 0.5 * base_salary * 5 + (years - 5) * base_salary
    return round(gratuity, 2), round(years, 2)

def calculate_total_salary(base_salary, allowances=0, deductions=0):
    total = base_salary + allowances - deductions
    return round(total, 2)

def ask_gpt(question, context="سياسات الموارد البشرية لحساب الرواتب ونهاية الخدمة:"):
    prompt = f"{context}\n\nالسؤال: {question}\nالجواب:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بـ GPT: {str(e)}"

# ========== UI ========== #
st.title("📊 Chatbot لحساب الرواتب ومكافأة نهاية الخدمة")
st.write("أدخل بيانات الموظف ليتم حساب المستحقات تلقائيًا")

uploaded_file = st.file_uploader("تحميل ملف Excel يحتوي على بيانات الموظفين", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("## بيانات الموظفين:")
    st.dataframe(df)

    st.write("---")
    selected_index = st.selectbox("اختر موظفًا لحسابه:", df.index)
    employee = df.loc[selected_index]

    try:
        start_date = pd.to_datetime(employee['StartDate'])
        end_date = pd.to_datetime(employee['EndDate'])
        base_salary = float(employee['BaseSalary'])
        allowances = float(employee.get('Allowances', 0))
        deductions = float(employee.get('Deductions', 0))

        gratuity, years_worked = calculate_end_of_service(start_date, end_date, base_salary)
        total_salary = calculate_total_salary(base_salary, allowances, deductions)

        st.success(f"مدة الخدمة: {years_worked:.2f} سنة")
        st.success(f"مكافأة نهاية الخدمة: {gratuity:.2f} جنيه")
        st.success(f"إجمالي الراتب الشهري: {total_salary:.2f} جنيه")

    except Exception as e:
        st.error(f"خطأ في البيانات: {str(e)}")

st.write("---")
st.write("## 🤖 مساعد الذكاء الاصطناعي للأسئلة")
user_question = st.text_input("اسأل سؤالاً متعلقًا بالموارد البشرية أو السياسات:")
if user_question:
    answer = ask_gpt(user_question)
    st.info(answer)

st.write("---")
st.caption("تم التطوير بواسطة عمر فتحي - مشروع تجريبي")
