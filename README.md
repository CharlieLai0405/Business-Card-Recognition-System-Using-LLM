# Business-Card-Recognition-System-Using-Ollama
– Implemented a business card recognition system centered on Ollama, integrating LLMs for image text parsing and structured JSON output, along with response optimization to improve accuracy.

---

## System Architecture

![1-1](https://github.com/user-attachments/assets/7d7e3fa7-dc12-4eb4-8a52-a1ce0fa29401)

**Modules Overview:**

| Module              | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| Flask API Endpoint  | Receives uploaded business card image requests                     |
| Controller          | Manages recognition + validation process                           |
| JSON Generator      | Uses GPT-4o to parse the image and output structured JSON          |
| Result Validator    | Uses GPT-4o to score the result (1–9), retry if below threshold    |
| API Response Module | Combines valid result + token usage + cost into the final response |

> If the quality score is below a configurable threshold (e.g. 7), the system will automatically retry (max 5 times) using adjusted prompts.

---

## How to Use

### 1. Start Backend (Flask API)

```bash
python3 main.py       # GPT-4o-mini
python3 main4o.py     # GPT-4o
```

### 2. Run Recognition Client

```bash
python3 request.py
```

* Automatically scans `./BusinessCard/`
* Stores output in designated model folder (e.g. `4o-mini/`)
* Tracks token usage and cost

### 3. Compare with Ground Truth

```bash
python3 compareAll.py
```

* Select model version (1–4)
* Evaluates field-level accuracy by comparing with files in `GroundTruth/`

---

## Sample API Response

```json
{
  "response": {
    "姓名": "顏漢杜",
    "公司名稱": "永豐能源科技股份有限公司",
    "職位": "總經理",
    "部門": "工程技術部",
    "電子郵件": "s0671@fy.com",
    "地址": "327桃園市新屋區中山西路三段240號",
    "電話號碼": "03-486-3636 分機 220",
    "行動電話": "0921-981-826",
    "傳真": ""
  },
  "cost_twd": 0.1391,
  "input_tokens": 202,
  "output_tokens": 145
}
```

---

## Token Cost Calculation

| Model       | Input (USD / 1K) | Output (USD / 1K) |
| ----------- | ---------------- | ----------------- |
| GPT-4o      | \$0.0025         | \$0.01            |
| GPT-4o-mini | \$0.000075       | \$0.0003          |

* Exchange rate: 1 USD = 30 TWD
* Cost is auto-calculated and returned by API

---

## Model Comparison Results

| Model                | Correct Fields | Accuracy   | Cost (TWD) |
| -------------------- | -------------- | ---------- | ---------- |
| 4o-mini              | 61 / 90        | 67.78%     | 0.0845     |
| 4o-mini + model      | 70 / 90        | 77.78%     | 1.6935     |
| 4o                   | 75 / 90        | 83.33%     | 0.1391     |
| 4o + model           | **79 / 90**    | **87.78%** | 4.8242     |

---

## Features

* Image-to-JSON extraction using GPT Vision
* Auto-format validation with GPT scoring (1–9)
* Retry mechanism (up to 5 rounds)
* Field-level accuracy comparison tool
* Real-time cost/token tracking
* Clean file organization by model/version

