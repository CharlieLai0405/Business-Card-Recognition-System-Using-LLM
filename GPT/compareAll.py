import os
import ast


def load_txt_as_dict(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1].encode("utf-8").decode("unicode_escape")
        return ast.literal_eval(content)


def compare_accuracy(ground_truth, predicted):
    total = 0
    correct = 0
    for key in ground_truth:
        if key == "":
            continue
        total += 1
        gt_val = ground_truth.get(key, "").strip()
        pred_val = predicted.get(key, "").strip()
        if gt_val == pred_val:
            correct += 1
    return correct, total, correct / total if total > 0 else 0.0


# === 資料夾與檔名處理 ===
ground_truth_folder = "GroundTruth"
while True:
    choose = input("select model: \n1. 4o-miniOrigin\n2. 4o-mini\n3. 4oOrigin\n4. 4o\n")
    if choose == "1":
        predict_folder = "4o-miniOrigin"
    elif choose == "2":
        predict_folder = "4o-mini"
    elif choose == "3":
        predict_folder = "4oOrigin"
    elif choose == "4":
        predict_folder = "4o"
    else:
        break

    # 取得所有 GroundTruth 檔案
    gt_files = [
        f for f in os.listdir(ground_truth_folder) if f.endswith("_GroundTruth.txt")
    ]

    # 統計變數
    total_files = 0
    total_fields = 0
    total_correct = 0

    # print("🔍 開始比對每筆資料...\n")

    for gt_file in sorted(gt_files):
        base_name = gt_file.replace("_GroundTruth.txt", "")
        if choose == "1" or choose == "2":
            pred_file = f"{base_name}_4o-mini.txt"
        elif choose == "3" or choose == "4":
            pred_file = f"{base_name}_4o.txt"

        gt_path = os.path.join(ground_truth_folder, gt_file)
        pred_path = os.path.join(predict_folder, pred_file)

        # 檢查預測檔是否存在
        if not os.path.exists(pred_path):
            print(f"❌ 缺少對應預測檔：{pred_file}")
            continue

        gt_dict = load_txt_as_dict(gt_path)
        pred_dict = load_txt_as_dict(pred_path)

        correct, total, acc = compare_accuracy(gt_dict, pred_dict)

        # print(f"{pred_file}")
        # print(f"✅ 正確欄位數: {correct} / {total}")
        # print(f"✅ 準確率: {acc:.2%}")
        # print("-" * 50)

        total_files += 1
        total_fields += total
        total_correct += correct

    # === 平均統計 ===
    if total_files > 0:
        avg_accuracy = total_correct / total_fields if total_fields > 0 else 0.0
        print("📊 總結")
        print(f"比對筆數：{total_files}")
        print(f"總正確欄位數：{total_correct} / {total_fields}")
        print(f"平均準確率：{avg_accuracy:.2%}")
    else:
        print("⚠️ 沒有成功比對的檔案。")
