import random
import os
import json
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

# 欠款紀錄檔案
DEBTS_FILE = "debts.json"

# 載入欠款資料
def load_debts():
    if os.path.exists(DEBTS_FILE):
        with open(DEBTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

# 儲存欠款資料
def save_debts(debts):
    with open(DEBTS_FILE, "w", encoding="utf-8") as f:
        json.dump(debts, f, ensure_ascii=False, indent=4)

# 全域變數 debts
debts = load_debts()

# 設定文字回覆
responses = {
    "吃啥" : ["弘爺", "ㄐㄐ", "阿基", "大吉祥", "吉購吉", "傻師傅", "維克","小張","新鮮","老麥","麥味登","六扇門","啊搖","三媽","漢堡王","高嫁妝","勞碌命"],
    "龍潭路" : ["弘爺", "阿基", "大吉祥", "吉購吉", "傻師傅", "維克","麥味登","啊搖","越南"],
    "出去吃" : ["小張","新鮮","老麥","麥味登","六扇門","三媽","漢堡王","高嫁妝","勞碌命","越南河粉"],
    "外面吃" : ["小張","新鮮","老麥","麥味登","六扇門","三媽","漢堡王","高嫁妝","勞碌命","越南河粉"],
    "ㄐㄐ" : ["ㄔㄐㄐ!ㄔㄐㄐ!!","ㄐㄐ"],
    "閉嘴" : ["管好你自己","在那狗叫甚麼"],
    "加一點" : ["好事多胡椒鹽"],
    "好痠喔" : ["真香","真冰涼","不錯不錯"],
    "好酸喔" : ["真香","真冰涼","不錯不錯"],
    "真香" : ["好痠喔","真冰涼","不錯不錯"],
    "真冰涼" : ["真香","好痠喔","不錯不錯"],
    "還是這邊":["翹","翹課","問就是翹"],
    "還是等等":["翹","翹課","問就是翹"],
    "還是我們":["翹","翹課","問就是翹"],
    "英雄聯盟" : ["狗才玩"],
    "LOL" : ["狗才玩"],
    "lol" : ["狗才玩"],
}

# 設定圖片回覆
image_responses = {
    "吃我屌" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E5%90%83%E6%88%91%E5%B1%8C.jpg?raw=true"],
    "幫我吹" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%98%8E%E5%A4%A9%E5%B9%AB%E4%BD%A0%E7%B4%A0.jpg?raw=true"],
    "幫我素" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%98%8E%E5%A4%A9%E5%B9%AB%E4%BD%A0%E7%B4%A0.jpg?raw=true"],
    "幫我吃" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%98%8E%E5%A4%A9%E5%B9%AB%E4%BD%A0%E7%B4%A0.jpg?raw=true"],
    "騷" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E8%89%98.jpg?raw=true"],
    "真騷" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E8%89%98.jpg?raw=true"],
    "= =" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/=%20=.jpg?raw=true"],
    "==" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/=%20=.jpg?raw=true"],
    "下棋" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E4%B8%8B%E6%A3%8B.jpg?raw=true"],
    "我出來了" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E6%88%91%E5%87%BA%E4%BE%86%E4%BA%86.jpg?raw=true"],
    "抱歉": ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E5%B0%91%E8%8F%AF%E6%8A%B1%E6%AD%89.jpg?raw=true"],
    "破防了" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E7%A0%B4%E6%88%BF%E4%BA%86.jpg?raw=true"],
    "累累" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/%E7%B4%AF%E7%B4%AF.jpg?raw=true"],
    "蛤" : ["https://github.com/sloth0622/line-bot/blob/main/static/images/Mygo/%E8%9B%A4.jpg?raw=true"]
}

# 多關鍵字匹配回覆
multi_keyword_responses = {
    ("下棋", "嗎"): "雲科左為申請出戰"
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
    global debts  # 🔥 要存新的 debts
    user_message = event.message.text.strip()
    user_id = event.source.user_id

    print(f"收到的訊息: {user_message} (user_id: {user_id})")

    # 1. 欠款功能：新增
    if "我欠" in user_message and "元" in user_message:
        try:
            parts = user_message.split("欠")[1].split("元")[0]
            who = ''.join([c for c in parts if not c.isdigit()]).strip()
            amount = int(''.join([c for c in parts if c.isdigit()]))

            if user_id not in debts:
                debts[user_id] = {"debt_list": []}

            debts[user_id]["debt_list"].append({"who": who, "amount": amount})
            save_debts(debts)

            reply = f"已記錄：你欠 {who} {amount} 元"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )
        except Exception as e:
            print(f"記錄欠款失敗：{e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="格式錯誤，請用『我欠小明40元』這樣輸入！")
            )
        return

    # 2. 欠款功能：查詢
    if user_message in ["查欠款", "查詢欠款"]:
        if user_id not in debts or not debts[user_id]["debt_list"]:
            reply = "你沒有任何欠款紀錄喔！"
        else:
            reply = "你的欠款紀錄：\n"
            for debt in debts[user_id]["debt_list"]:
                reply += f"- 欠 {debt['who']} {debt['amount']}元\n"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
        return

    # 3. 欠款功能：清除
    if user_message.startswith("清除欠款"):
        target = user_message.replace("清除欠款", "").strip()

        if user_id in debts:
            if target == "":
                debts[user_id]["debt_list"] = []
                reply = "你的所有欠款紀錄都已清除！"
            else:
                before = len(debts[user_id]["debt_list"])
                debts[user_id]["debt_list"] = [
                    debt for debt in debts[user_id]["debt_list"] if debt["who"] != target
                ]
                after = len(debts[user_id]["debt_list"])

                if before == after:
                    reply = f"沒有找到欠 {target} 的紀錄。"
                else:
                    reply = f"已清除欠 {target} 的紀錄！"
            save_debts(debts)
        else:
            reply = "你沒有欠款紀錄可以清除喔～"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
        return

    # 正常文字回覆
    if user_message in responses:
        reply_text = random.choice(responses[user_message])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        return

    # 圖片回覆
    if user_message in image_responses:
        image_url = random.choice(image_responses[user_message])
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url=image_url,
                preview_image_url=image_url
            )
        )
        return

    # 多關鍵字匹配回覆
    for keywords, reply_text in multi_keyword_responses.items():
        if all(keyword in user_message for keyword in keywords):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            return

    print(f"未匹配的訊息: {user_message}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
