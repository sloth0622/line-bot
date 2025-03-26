import random
import os
from flask import Flask, request, jsonify, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 設定環境變數
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

app = Flask(__name__, static_folder="static")

# 初始化 LineBotApi 和 WebhookHandler
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 設定圖片回覆
image_responses = {
    "吃我屌": "/static/images/吃我屌.jpg",
    "風景": "/static/images/scenery.jpg"
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

# 讓 Flask 提供靜態圖片
@app.route("/static/images/<filename>")
def serve_image(filename):
    return send_from_directory("static/images", filename)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    # 回傳圖片
    if user_message in image_responses:
        image_url = request.url_root + image_responses[user_message]  # 產生完整 URL
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
