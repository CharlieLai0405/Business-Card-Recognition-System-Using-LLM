import requests
import glob
import os
import json

# url = "https://ledb-go-llama-agent.onrender.com"
url = "http://localhost:8000"

# file = open("./BusinessCard/LINE_ALBUM_名片_250324_.jpg", "rb")
# file = open("./picture.jpg", "rb")
# output_dir = "./"
# print(file)
# files = {"file": file}
# response = requests.post(url + "/api/ollama_card_recognition", files=files)
# data = response.json()
# result_text = data["response"]
# print(result_text)
# txt_path = os.path.join(output_dir, "picture_4o-mini.txt")

# with open(txt_path, "w", encoding="utf-8") as f:
#     json.dump(result_text, f, ensure_ascii=False, indent=2)
# print(f"儲存完成：{txt_path}")

######

image_paths = sorted(glob.glob("./BusinessCard/LINE_ALBUM_名片_250324_**.jpg"))
selected_images = image_paths[10:20]
output_dir = "./4o-mini"
# output_dir = "./4o"
# output_dir = "./4oOrigin"
# output_dir = "./4o-miniOrigin"
# output_dir = "./GroundTruth"
Total_cost_twd = 0
Total_input_tokens = 0
Total_output_tokens = 0

for idx, image_path in enumerate(selected_images, start=4):
    with open(image_path, "rb") as file:
        print(file)
        files = {"file": file}
        response = requests.post(url + "/api/ollama_card_recognition", files=files)
        data = response.json()

        result_text = data["response"]
        cost_twd = data["cost_twd"]
        input_tokens = data["input_tokens"]
        output_tokens = data["output_tokens"]

        Total_cost_twd += cost_twd
        Total_input_tokens += input_tokens
        Total_output_tokens += output_tokens

        print(f"第 {idx} 張圖片結果：\n{result_text}\n{'-' * 40}")

        filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        # txt_path = os.path.join(output_dir, filename_without_ext + "_GroundTruth.txt")
        # txt_path = os.path.join(output_dir, filename_without_ext + "_4o.txt")
        txt_path = os.path.join(output_dir, filename_without_ext + "_4o-mini.txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            json.dump(result_text, f, ensure_ascii=False, indent=2)
        print(f"儲存完成：{txt_path}")

print(f"總花費：{Total_cost_twd}元")
print(f"總輸入token數：{Total_input_tokens}")
print(f"總輸出token數：{Total_output_tokens}")
