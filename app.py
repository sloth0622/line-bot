import random
import os
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 設定環境變數
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

app = Flask(__name__)

# 初始化 LineBotApi 和 WebhookHandler
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 設定文字回覆
responses = {
    "你好": ["你好！", "哈囉！", "安安！"],
    "天氣": ["今天天氣不錯！", "看起來快下雨了！", "要記得帶傘喔！"],
    "笑話": ["為什麼雞過馬路？因為它想過去！", "今天我遇到一個笑話，結果他比我還會笑！"],
    "吃啥": ["大頭", "ㄐㄐ", "阿基", "大吉祥", "吉購吉", "傻師傅", "維克"]
}

# 設定圖片回覆
image_responses = {
    "吃我屌": "https://github.com/sloth0622/line-bot/blob/main/static/images/%E5%90%83%E6%88%91%E5%B1%8C.jpg?raw=true"
}

@app.route("/", methods=["GET"])
def home():
    return "LINE Bot 正在運行！"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({"status": "error", "message": "Invalid signature"}), 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    # 文字回應：僅當完全匹配時才回覆
    if user_message in responses:
        reply_text = random.choice(responses[user_message])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    
    # 圖片回應：僅當完全匹配時才回覆
    elif user_message in image_responses:
        image_url = image_responses[user_message]  # 使用 GitHub 上的圖片 URL
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
