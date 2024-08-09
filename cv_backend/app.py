import os
import pickle
import math
import json
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
from openai import OpenAI
from fetchers import predict_week
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

@app.route('/get_response', methods=['POST'])
def get_response():
    print("Received a POST request")
    try:
        body = request.get_json()
        print("Request body:", body)
        user_input = body['query']
        print("User input:", user_input)

        with open('cv_model.pkl', 'rb') as model_file:
            model = pickle.load(model_file)

        prediction = predict_week(model)
        prediction_str = ''
        for date, stats in prediction.items():
            prediction_str += f"{date}, the sales are predicted to be ${stats['sales']:.2f}, with {math.ceil(stats['orders'])} orders, and around {math.ceil(stats['guests'])} guests.\n"
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""
                            You are an assistant that helps communicate numerical predictions about sales, orders, and guests to the user. 
                            When making predictions for the week as a whole, exclude 'today'. Today is {datetime.now().date()} and it is a {datetime.now().weekday()}, with each integer corresponding to the day of the week, with Monday as 0 and Sunday as 6. 
                            When relaying prediction data to the user, please use the day of the week instead of the date.
                            """},
                {"role": "user", "content": prediction_str},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=400,
            top_p=1
        )
        content = response.choices[0].message.content

        return jsonify({'response': content}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
