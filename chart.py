import matplotlib
matplotlib.use('Agg')  # <-- This disables GUI backend
import matplotlib.pyplot as plt

import openai
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, request, jsonify

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/generate_chart", methods=["POST"])
def generate_chart():
    text = request.json["summary"]

    prompt = f"""Extract data for a chart from this text and output Python lists:
    TEXT: {text}
    Output format:
    labels = [...]
    values = [...]
    chart_type = "pie"
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    exec_locals = {}
    exec(response.choices[0].message.content, {}, exec_locals)

    labels = exec_locals["labels"]
    values = exec_locals["values"]
    chart_type = exec_locals.get("chart_type", "bar")

    # Generate chart
    fig, ax = plt.subplots()
    if chart_type == "pie":
        ax.pie(values, labels=labels, autopct='%1.1f%%')
    else:
        ax.bar(labels, values)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    base64_image = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify({
    "image_url": f"data:image/png;base64,{base64_image}"
    })
    
