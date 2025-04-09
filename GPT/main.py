# %%
import ollama
from flask import Flask, request
from flask import Response
import json
from os import remove
from ollama import Client
from openai import OpenAI
import base64
import re

# url = "https://ollama-api.seadeep.ai/"
# url = "http://localhost:11434/api/generate"
app = Flask(__name__)

client = OpenAI(api_key="OpenAI_api_key")

# 台幣匯率
TWD_PER_USD = 30  # 1 美元 = 30 台幣

# 模型費率設定（每百萬 token）
MODEL_PRICING = {
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
        "cached_input": 1.25,
    },
    "gpt-4o-mini": {
        "input": 0.075,
        "output": 0.3,
        "cached_input": 0.075,  # 假設沒有區分 cached 價格
    },
}


def calculate_cost_by_model(model, input_tokens, cached_input_tokens, output_tokens):
    """根據模型計算 token 成本並換算成台幣"""
    if model not in MODEL_PRICING:
        raise ValueError(f"未知模型定價：{model}")
    pricing = MODEL_PRICING[model]
    usd_cost = (
        (input_tokens / 1_000_000) * pricing["input"]
        + (cached_input_tokens / 1_000_000) * pricing["cached_input"]
        + (output_tokens / 1_000_000) * pricing["output"]
    )
    return round(usd_cost * TWD_PER_USD, 5)


def get_ollama_card_recognition(path, recommend):
    try:
        print("------------------------------------------------------------\n")
        print("get ChatGPT recommand: \n" + recommend)

        with open(path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            # model="gpt-4o-mini",  # for 5 threshold 8
            model="gpt-4o",  # for 3 threshold 7
            messages=[
                {
                    "role": "system",
                    "content": f"""{recommend}/n
                    這是一張名片，幫我解讀並用json格式回傳以下這些資訊:
                    姓名、公司名稱、職位、部門、電子郵件、地址、電話號碼、行動電話、傳真，你只要回傳json的內容就好，絕對不要講任何其他的話，沒有的訊息回傳""，全部都用中文回答，如果有重複的資料，只要回傳其中一個就好，
                    最好是中文的那筆資料，務必確保你回傳的東西符合json的規定，欄位名稱一定要用用中文這很重要，如果沒有傳真(FAX)的話，傳真那個欄位回傳""
                    回傳之前先自己檢查三次確認資料是否正確，盡量回傳所有得到的正確資訊，一定要確保你回傳的所有東西符合json的規定，先自己檢查三次是否符合json的格式，如果不符合請重新生成json的格式後再給我，最後只需要回傳json的內容就好，絕對絕對不要講任何其他的話
                    """,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    ],
                },
            ],
            max_tokens=1000,
        )

        # Use_model = "gpt-4o-mini"
        Use_model = "gpt-4o"
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        cached_input_tokens = 0  # 預設無 cached

        cost_twd = calculate_cost_by_model(
            Use_model, input_tokens, cached_input_tokens, output_tokens
        )

        res = response.choices[0].message.content
        res = res[res.find("{") : res.rfind("}") + 1]

        while "\n" in res:
            res = res.replace("\n", "")

        res = eval(res)
        if "姓名" not in res:
            return "Failed"
        res = f"{res}"

        return res, cost_twd, input_tokens, output_tokens

    except Exception as e:
        print(e)
        return "Failed"


def ask_GPTVision_check(path, input_text):
    try:
        with open(path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")

        response = client.chat.completions.create(
            # model="gpt-4o-mini",  # for 5 threshold 8
            model="gpt-4o",  # for 3 threshold 7
            messages=[
                {"role": "system", "content": "你是一位幫助我驗證名片辨識結果的助手"},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""以下是我根據圖片辨識出的 JSON 結果：{input_text}
                            請你檢查：以上資料是否符合 JSON 格式，並且所有欄位名稱是否都是「中文」？
                            只允許你對這個輸出評分，1到9分你覺得這個答案幾分，給分的時候嚴格一點，你不能說明任何其他的話，其他什麼都不要講，
                            接著換行，如果你剛骯的評分小於8分，請告訴我原因和需要改進的地方，
                            並告訴我你覺得哪幾欄辨識結果與你自己得辨識結果不同，辨識結果的正確性非常重要，所以你自己也要辨識過並與我提供的進行比對，並用列點方式告訴我哪幾欄需要重新辨識，哪些不需要重新辨識。
                            """,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=1000,
        )

        # Use_model = "gpt-4o-mini"
        Use_model = "gpt-4o"
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        cached_input_tokens = 0  # 預設無 cached

        cost_twd = calculate_cost_by_model(
            Use_model, input_tokens, cached_input_tokens, output_tokens
        )

        res = response.choices[0].message.content

        return res, cost_twd, input_tokens, output_tokens

    except Exception as e:
        print(e)
        return "Failed"


def try_ollama_card_recognition(path):
    recommend = ""
    Temp_cost_twd = 0
    Temp_input_tokens = 0
    Temp_output_tokens = 0
    for i in range(5):
        ret, GTemp_cost_twd, GTemp_input_tokens, GTemp_output_tokens = (
            get_ollama_card_recognition(path, recommend)
        )
        print("------------------------------------------------------------\n")
        if ret == "Failed":
            print("Failed: " + str(i))
            continue
        if len(ret) < 10:
            print("len(ret) < 10 Failed: " + str(i))
            continue
        print("output: " + ret + " \n" + "ask ChatGPT check again")

        recommend, ATemp_cost_twd, ATemp_input_tokens, ATemp_output_tokens = (
            ask_GPTVision_check(path, ret)
        )
        Temp_cost_twd = Temp_cost_twd + GTemp_cost_twd + ATemp_cost_twd
        Temp_input_tokens = Temp_input_tokens + GTemp_input_tokens + ATemp_input_tokens
        Temp_output_tokens = (
            Temp_output_tokens + GTemp_output_tokens + ATemp_output_tokens
        )
        match = re.search(r"\d+", recommend)  # 找第一組數字
        if match:
            result_num = int(match.group())
            print(f"Y or N ChatGPT \n {result_num}")
            if result_num < 7:
                print("ChatGPT Failed: " + str(i))
                continue
        else:
            print("找不到數字")
            continue

        print(f"""
        picture_count: {picture_count},\n
        model: gpt-4o-mini,\n
        cost_twd: {Temp_cost_twd},\n
        input_tokens: {Temp_input_tokens},\n
        output_tokens: {Temp_output_tokens}\n""")

        return ret, Temp_cost_twd, Temp_input_tokens, Temp_output_tokens

    return "{}"


picture_count = 0


@app.route("/api/ollama_card_recognition", methods=["POST"])
def ollama_card_recognition():
    print("request received")
    global picture_count
    picture_count += 1
    path = f"picture{picture_count}.jpg"
    with open(path, "wb") as f:
        f.write(request.files["file"].read())

    ret, cost_twd, input_tokens, output_tokens = try_ollama_card_recognition(path)
    remove(path)
    return Response(
        json.dumps(
            {
                "response": ret,
                "cost_twd": cost_twd,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
            ensure_ascii=False,
        ),
        content_type="application/json",
    )


@app.route("/")
def index():
    return "Hello World"


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")


# %%

# %%
