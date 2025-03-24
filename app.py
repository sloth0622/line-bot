import random
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

# 設定環境變數
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 設定關鍵字與隨機回覆
responses = {
    "你好": ["你好！", "哈囉！", "安安！"],
    "天氣": ["今天天氣不錯！", "看起來快下雨了！", "要記得帶傘喔！"],
    "笑話": ["為什麼雞過馬路？因為它想過去！", "今天我遇到一個笑話，結果他比我還會笑！"],
}

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot 正在運行！"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({"status": "error", "message": "Invalid signature"}), 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    matched_replies = []

    for keyword, reply_list in responses.items():
        if keyword in user_message:
            matched_replies.extend(reply_list)

    if matched_replies:
        reply_text = random.choice(matched_replies)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
