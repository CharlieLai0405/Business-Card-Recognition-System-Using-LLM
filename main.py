# %%
import ollama
from flask import Flask, request
from os import remove
from ollama import Client

url = "https://ollama-api.seadeep.ai/"
# url = "http://localhost:11434/api/generate"
app = Flask(__name__)


def get_ollama_card_recognition(path, recommend):
    try:
        print("------------------------------------------------------------\n")
        print("get ollama recommand: \n" + recommend)
        client = Client(host=url)
        response = client.chat(
            model="llama3.2-vision:11b",
            # model="granite3.2-vision",
            # model="gemma3:27b",
            messages=[
                {
                    "role": "system",
                    "content": """
                    {recommend}/n
                    這是一張名片，幫我解讀並用json格式回傳以下這些資訊:
                    姓名、公司名稱、職位、部門、電子郵件、地址、電話號碼、行動電話、傳真，你只要回傳json的內容就好，絕對不要講任何其他的話，沒有的訊息回傳""，全部都用中文回答，如果有重複的資料，只要回傳其中一個就好，
                    最好是中文的那筆資料，務必確保你回傳的東西符合json的規定，欄位名稱一定要用用中文這很重要，如果沒有傳真(FAX)的話，傳真那個欄位回傳""
                    回傳之前先自己檢查三次確認資料是否正確，盡量回傳所有得到的正確資訊，一定要確保你回傳的所有東西符合json的規定，先自己檢查三次是否符合json的格式，如果不符合請重新生成json的格式後再給我，最後只需要回傳json的內容就好，絕對絕對不要講任何其他的話
                    """,
                    "images": [path],
                }
                # {"role": "user", "content": "Hi"}
            ],
        )

        res = response.message.content
        # print("------------------------------------------------------------\n")
        # print("res:\n")
        # print(res)
        # print("------------------------------------------------------------\n")

        res = res[res.find("{") : res.rfind("}") + 1]

        while res.find("\n") != -1:
            res = res.replace("\n", "")

        res = eval(res)
        if "姓名" not in res:
            return "Failed"
        res = f"{res}"

        return res

    except Exception as e:
        print(e)
        return "Failed"


def ask_llama3Vision_check(path, input_text):
    try:
        # print("run llama3.2-vision:11b")
        # print("run gemma")
        client = Client(host=url)
        response = client.chat(
            # model="llama3.2-vision:11b",
            model="gemma3:27b",
            messages=[
                {
                    "role": "system",
                    "content": f"{input_text}\n以上資料有符合json格式嗎，而且資料的欄位名稱必須是中文，如果你覺得有請回答'yes'，如果你覺得沒有請回答'no ',回答的前三個字你只能回答'yes'或'no'，絕對不要講任何其他的話，這很重要請再三確認你回覆的前三個字是否只有yes或no，如果你回答‘no '，請先換行，並根據jason格式分析，告訴我為什麼回答no，然後給出改進的建議，並告訴我你覺得哪幾欄辨識結果與你自己得辨識結果不同，需要重新辨識",
                    # content": f"{input_text}\n以上資料有符合json格式嗎，而且資料的欄位名稱必須是中文，如果你覺得有，請回答yes，如果你覺得沒有，請回答no,你只能回答yes或no，絕對不要講任何其他的話",
                    "images": [path],
                }
            ],
        )

        res = response.message.content

    except Exception as e:
        print(e)
        return "Failed"

    return res


def ask_gemma_check(path, input_text):
    try:
        # print("run llama3.2-vision:11b")
        # print("run gemma")
        client = Client(host=url)
        response = client.chat(
            model="llama3.2-vision:11b",
            # model="gemma3:27b",
            messages=[
                {
                    "role": "system",
                    "content": f"{input_text}\n以上資料有符合json格式嗎，而且資料的欄位名稱必須是中文，如果你覺得有，請回答'答案是：yes'，如果你覺得沒有，請回答'答案是：no ',回答的前七個字只能出現'答案是：yes'或'答案是：no'，如果你回答'答案是：yes'就不要再回答任何其他的話，但是如果你回答‘答案是：no '，請先換行，並根據jason格式分析，告訴我為什麼回答no，然後根據生成的條件‘全部都用中文回答，如果有重複的資料，只要回傳其中一個就好，最好是中文的那筆資料，務必確保你回傳的東西符合json的規定，欄位名稱一定要用用中文這很重要，如果沒有傳真(FAX)的話，傳真那個欄位回傳"
                    "’給出改進的建議，並告訴我你覺得哪幾欄辨識結果與你自己得辨識結果不同，辨識結果的正確性非常重要，所以你自己也要辨識過並與我提供的進行比對，並用列點方式告訴我哪幾欄需要重新辨識，哪些不需要重新辨識",
                    # content": f"{input_text}\n以上資料有符合json格式嗎，而且資料的欄位名稱必須是中文，如果你覺得有，請回答yes，如果你覺得沒有，請回答no,你只能回答yes或no，絕對不要講任何其他的話",
                    "images": [path],
                }
            ],
        )

        res = response.message.content

    except Exception as e:
        print(e)
        return "Failed"

    return res


def try_ollama_card_recognition(path):
    recommend = ""
    for i in range(10):
        ret = get_ollama_card_recognition(path, recommend)
        print("------------------------------------------------------------\n")
        print("output: " + ret)
        print("------------------------------------------------------------\n")
        if ret == "Failed":
            print("Failed: " + str(i))
            continue
        if len(ret) < 10:
            print("len(ret) < 10 Failed: " + str(i))
            continue
        print("output: " + ret + " \n" + "ask ollama check again")

        # print("run gemma \n" + ask_llama3Vision_check(path, ret))
        if ask_llama3Vision_check(path, ret)[:3] != "yes":
            recommend = ask_llama3Vision_check(path, ret)
            print("gemma Failed: " + str(i))
            continue

        print("Y or N llama3.2_Vision \n" + ask_gemma_check(path, ret)[4:7])
        print("------------------------------------------------------------\n")
        # print("run llama3.2_Vision \n" + ask_gemma_check(path, ret))
        if ask_gemma_check(path, ret)[4:7] != "yes":
            recommend = ask_gemma_check(path, ret)
            print("llama3.2_Vision Failed: " + str(i))
            print("------------------------------------------------------------\n")
            continue

        return ret

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

    ret = try_ollama_card_recognition(path)
    remove(path)
    return ret


@app.route("/")
def index():
    return "Hello World"


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")


# %%

# %%
