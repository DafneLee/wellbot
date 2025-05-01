from flask import Flask, request
import openai
import requests
import os

# ✅ 먼저 app 선언
app = Flask(__name__)

# ✅ 그 다음부터 라우터들
@app.route('/')
def home():
    return '✅ 서버 잘 켜졌어!'

@app.route('/slack/oauth/callback')
def oauth_callback():
    return 'OAuth callback received.'

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json

    if 'challenge' in data:
        return data['challenge']

    event = data.get('event', {})
    user_text = event.get('text', '')
    channel_id = event.get('channel')

    if user_text and 'bot_id' not in event:
        feedback = generate_feedback(user_text)
        send_to_slack(channel_id, feedback)

    return 'OK', 200

def generate_feedback(user_input):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 건강 피드백 코치야. 사용자 입력을 보고 운동/식단 피드백을 짧게 줘."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def send_to_slack(channel, text):
    headers = {
        "Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": text
    }
    requests.post("https://slack.com/api/chat.postMessage", json=payload, headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
