import multiprocessing
import time
import os
from datetime import datetime
import yaml
import argparse
import logging

# LangChain models
from langchain_community.chat_models import ChatLlamaCpp
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from translate.storage.tmx import tmxfile


# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    filename="reviewer.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# -------------------------
# Model Factory
# -------------------------
def load_llm(model_type: str, model_path: str = None, temperature: float = 0):
    """Return a LangChain-compatible LLM depending on model_type."""
    if model_type == "llama":
        return ChatLlamaCpp(
            temperature=temperature,
            model_path=model_path,
            n_ctx=2048,
            n_gpu_layers=8,
            n_batch=64,
            max_tokens=128,
            n_threads=max(1, multiprocessing.cpu_count()),
            repeat_penalty=1.1,
            top_p=1.0,
            verbose=False,
        )
    elif model_type == "gpt":
        return ChatOpenAI(
            temperature=temperature,
            model="gpt-4o-mini",  # parametrize if needed
            max_tokens=128,
        )
    elif model_type == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=temperature,
            max_output_tokens=128,
        )
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")


# -------------------------
# CLI Arguments
# -------------------------
def get_args():
    parser = argparse.ArgumentParser(description="Run translation reviewer.")
    parser.add_argument("--prompt_version", type=str, default="2_1")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument(
        "--model_type",
        type=str,
        choices=["llama", "gpt", "gemini"],
        default="llama",
        help="Which backend to use",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-27b-it-Q8_0.gguf",
        help="Path for local Llama models (ignored for GPT/Gemini)",
    )
    return parser.parse_args()


# -------------------------
# Prompt & Metadata
# -------------------------
def load_prompt(prompt_version: str):
    with open(f"config/prompt-v{prompt_version}.txt", "r") as file:
        return file.read()


def load_metadata(prompt_version: str):
    try:
        with open(f"config/metadata-v{prompt_version}.yml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(e)
        return {"goal": "Default prompt description"}


# -------------------------
# Translation Logic
# -------------------------
def translate(llm, prompt: str, english: str, catalan: str) -> str:
    english = english.replace("_", "")
    catalan = catalan.replace("_", "")
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"English: '''{english}'''\nCatalan: '''{catalan}'''"),
    ]
    ai_msg = llm.invoke(messages)
    answer = (ai_msg.content or "").strip()
    logging.info(f"s: {english}")
    logging.info(f"t: {catalan}")
    logging.info(f"a: {answer}\n")
    return answer


def _write(english: str, catalan: str, note: str, result: str, fh, status: str):
    lines = [
        f"English: {english}",
        f"Catalan: {catalan}",
    ]
    if note:
        lines.append(f"Note: {note}")
    lines.append(f"Result: {result}")
    lines.append(f"Status: {status}")
    lines.append("\n-----------------------\n")
    content = "\n".join(lines)
    fh.write(content + "\n")
    print(content)


def load_strings(dataset: str):
    with open(dataset, "rb") as file:
        tmx = tmxfile(file, "en", "ca")
    strings = []
    for tu in tmx.unit_iter():
        source = tu.source
        target = tu.target
        note = tu.getnotes()
        strings.append((source, target, note))
    return strings


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    args = get_args()

    llm = load_llm(args.model_type, args.model_path)
    prompt = load_prompt(args.prompt_version)
    metadata = load_metadata(args.prompt_version)

    dataset = "dataset/dataset.tmx"
    strings = load_strings(dataset)
    total_strings = min(len(strings), args.max)

    tp = fp = fn = tn = 0
    processed = 0
    start_time = time.time()

    with open(
        f"output/results-v{args.prompt_version}-{args.max}.txt",
        "w",
        encoding="utf-8",
    ) as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(llm, prompt, en, ca)
            processed += 1

            if idx % 10 == 0 or idx == args.max:
                percent_done = (idx / total_strings) * 100
                total_time = time.time() - start_time
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                set_sec = processed / total_time * 60 if total_time > 0 else 0
                print(
                    f"Progress: {percent_done:.2f}% - {idx}/{total_strings} | set/min: {set_sec:.2f}| "
                    f"Time: {total_time:.2f}s | "
                    f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn} | "
                    f"Precision: {precision:.2f}, Recall: {recall:.2f}"
                )

            if idx > 0 and idx == args.max:
                break

            if res.upper().startswith("NO"):
                if note:
                    fn += 1
                    _write(en, ca, note, res, file, "fn")
                    continue
                else:
                    tn += 1
                continue

            if note:
                tp += 1
                _write(en, ca, note, res, file, "tp")
            else:
                fp += 1
                _write(en, ca, note, res, file, "fp")

    total_time = time.time() - start_time
    print(f"Total time used: {total_time:.2f} seconds")

    # Save stats
    csv = f"output/stats_{args.max}.csv"
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    if os.path.exists(csv):
        mode = "a"
        write_header = False
    else:
        mode = "w"
        write_header = True

    goal = metadata["goal"]
    with open(csv, mode, encoding="utf-8") as fh:
        if write_header:
            header = "date_time\tprompt_version\tgoal\ttp\tfp\tfn\ttn\tprecision\trecall\ttotal_time\tstrings"
            fh.write(header + "\n")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"{now}\t{args.prompt_version}\t{goal}\t{tp}\t{fp}\t{fn}\t{tn}\t{precision:.2f}\t{recall:.2f}\t{total_time:.2f}\t{processed}"
        fh.write(context + "\n")

