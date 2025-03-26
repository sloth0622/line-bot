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
    "吃啥": ["弘爺", "ㄐㄐ", "阿基", "大吉祥", "吉購吉", "傻師傅", "維克","小張","新鮮","老麥","麥味登","六扇門","啊搖","三媽","漢堡王","高嫁妝","勞碌命"],
    "ㄐㄐ": ["ㄔㄐㄐ!ㄔㄐㄐ!!"],
    "閉嘴": ["管好你自己","在那狗叫甚麼"],

    #好事多胡椒鹽
    "加一點":["好事多胡椒鹽"],
    "好痠喔":["真香","真冰涼","不錯不錯"],
    "好酸喔" : ["真香","真冰涼","不錯不錯"],
    "真香":["好痠喔","真冰涼","不錯不錯"],
    "真冰涼":["真香","好痠喔","不錯不錯"],

    #還是...
    "還是這邊":["翹","翹課","問就是翹"],
    "還是等等":["翹","翹課","問就是翹"],
    "還是我們":["翹","翹課","問就是翹"]
}

# 設定圖片回覆
image_responses = {
    "吃我屌": "https://github.com/sloth0622/line-bot/blob/main/static/images/%E5%90%83%E6%88%91%E5%B1%8C.jpg?raw=true",
    ("= =","==") : "https://github.com/sloth0622/line-bot/blob/main/static/images/=%20=.jpg?raw=true",
    "下棋":"https://github.com/sloth0622/line-bot/blob/main/static/images/%E4%B8%8B%E6%A3%8B.jpg?raw=true,",
    "我出來了" : "https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%88%91%E5%87%BA%E4%BE%86%E4%BA%86.jpg?raw=true",
    "抱歉": "https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%8A%B1%E6%AD%89.jpg?raw=true",
    ("幫我吹","幫我素") :"https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%98%8E%E5%A4%A9%E5%B9%AB%E4%BD%A0%E7%B4%A0.jpg?raw=true",
    "為甚麼":"https://github.com/sloth0622/line-bot/blob/main/static/images/%E7%82%BA%E7%94%9A%E9%BA%BC.jpg?raw=true",
    "破防了":"https://github.com/sloth0622/line-bot/blob/main/static/images/%E7%A0%B4%E6%88%BF%E4%BA%86.jpg?raw=true",
    "累累":"https://github.com/sloth0622/line-bot/blob/main/static/images/%E7%B4%AF%E7%B4%AF.jpg?raw=true",
    ("騷","真騷") : "https://github.com/sloth0622/line-bot/blob/main/static/images/%E8%89%98.jpg?raw=true",
    "蛤" : "https://github.com/sloth0622/line-bot/blob/main/static/images/%E8%9B%A4.jpg?raw=true"
}

# 多關鍵字匹配回覆
multi_keyword_responses = {
    ("下棋"):["雲科左為申請出戰"]
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

    print(f"收到的訊息: {user_message}")  # 輸出收到的消息，幫助除錯

    # 文字回應：僅當完全匹配時才回覆
    if user_message in responses:
        reply_text = random.choice(responses[user_message])
        print(f"回覆文字: {reply_text}")  # 輸出回覆的文字
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    
    # 圖片回應：僅當完全匹配時才回覆
    elif user_message in image_responses:
        image_url = image_responses[user_message]  # 使用 GitHub 上的圖片 URL
        print(f"回覆圖片: {image_url}")  # 輸出回覆的圖片 URL
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        )
    
    # 多關鍵字匹配：檢查訊息是否包含多個關鍵字
    else:
        for keywords, reply_text in multi_keyword_responses.items():
            if all(keyword in user_message for keyword in keywords):  # 檢查是否包含所有關鍵字
                print(f"回覆文字: {reply_text}")  # 輸出回覆的文字
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
                return  # 停止繼續檢查其他條件

    print(f"未匹配的訊息: {user_message}")  # 輸出未匹配的消息

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
