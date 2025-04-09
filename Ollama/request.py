import requests
import glob
import os

# url = "https://ledb-go-llama-agent.onrender.com"
url = "http://localhost:8000"
# file = open("./picture.jpg", "rb")
# print(file)
# files = {"file": file}
# response = requests.post(url + "/api/ollama_card_recognition", files=files)
# print(response.text)

image_paths = sorted(glob.glob("./BusinessCard/LINE_ALBUM_名片_250324_*.jpg"))

selected_images = image_paths[2:10]

output_dir = "./BusinessCard"

for image_path in selected_images:
    with open(image_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url + "/api/ollama_card_recognition", files=files)
        result_text = response.text

    filename_without_ext = os.path.splitext(os.path.basename(image_path))[0]

    txt_path = os.path.join(output_dir, filename_without_ext + ".txt")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    print(f"儲存完成：{txt_path}")
