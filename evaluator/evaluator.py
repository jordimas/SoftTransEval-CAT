import multiprocessing
import time
import yaml
import argparse
import logging
import save_json
import re

# LangChain models
from langchain_community.chat_models import ChatLlamaCpp
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
from translate.storage.tmx import tmxfile


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
    if model_type == "gemma3":
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
    if model_type == "gpt-oss":
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

    if model_type == "mistral":
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

    if model_type == "qwen3":
        return ChatLlamaCpp(
            temperature=0.7,
            model_path=model_path,
            n_ctx=2048,
            n_gpu_layers=8,
            n_batch=64,
            max_tokens=8192,
            n_threads=max(1, multiprocessing.cpu_count()),
            repeat_penalty=1.2,
            top_p=1.0,
            verbose=False,
        )

    elif model_type == "gpt":
        return ChatOpenAI(
            temperature=temperature,
            model="gpt-5-2025-08-07",
            max_tokens=4096,
        )
    elif model_type == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=temperature,
            max_output_tokens=128,
        )
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")


def get_args():
    parser = argparse.ArgumentParser(description="Run translation reviewer.")
    parser.add_argument("--prompt_version", type=str, default="1")
    parser.add_argument("--max", type=int, default=400)
    parser.add_argument(
        "--model_type",
        type=str,
        choices=["gemma3", "gpt", "gemini", "gpt-oss", "mistral", "qwen3"],
        default="gemma3",
        help="Which backend to use",
    )
    return parser.parse_args()


# -------------------------
# Prompt & Metadata
# -------------------------
def load_prompt(model: str, prompt_version: str):
    with open(f"config/{model}/prompt-v{prompt_version}.txt", "r") as file:
        return file.read()


def load_metadata(model: str, prompt_version: str):
    try:
        prompt_version = int(prompt_version.replace("_", ""))
        with open(f"config/{model}/metadata.yml", "r") as fh:
            data = yaml.safe_load(fh)
            data = data["versions"]
            return data[prompt_version]["goal"]
    except Exception as e:
        print(f"load_metadata. Error: {e}")
        return "Default prompt description"


# -------------------------
# Translation Logic
# -------------------------
def translate(llm, prompt: str, english: str, catalan: str) -> str:
    english = english.replace("_", "")
    catalan = catalan.replace("_", "")
    text_to_review = f"English: '''{english}'''\nCatalan: '''{catalan}'''"
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=text_to_review),
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


def load_strings(dataset: str, max_entries=-1):
    with open(dataset, "rb") as file:
        tmx = tmxfile(file, "en", "ca")
    strings = []
    notes = 0
    for tu in tmx.unit_iter():
        source = tu.source
        target = tu.target
        note = tu.getnotes()
        if note:
            notes += 1
        strings.append((source, target, note))
        if len(strings) == max_entries:
            break

    total = len(strings)
    errors = notes
    correct = total - errors

    error_pct = (errors / total) * 100 if total > 0 else 0
    correct_pct = (correct / total) * 100 if total > 0 else 0

    print(
        f"DATASET. Loaded {total} strings with {errors} translation errors. Errors {error_pct:.2f}%, correct: {correct_pct:.2f}%"
    )
    return strings


def calc_metrics(tp, fp, fn, elapsed, processed):
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    sets_per_min = (processed / elapsed * 60) if elapsed else 0

    if (precision + recall) > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0
    return precision, recall, sets_per_min, f1


if __name__ == "__main__":
    args = get_args()

    if args.model_type == "gemma3":
        path = "/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-12b-it-Q8_0.gguf"
    elif args.model_type == "gpt-oss":
        path = "/home/jordi/sc/llama/llama.cpp/download/gpt-oss-20b-UD-Q8_K_XL.gguf"
    elif args.model_type == "mistral":
        path = "/home/jordi/sc/llama/llama.cpp/download/Mistral-Small-24B-Instruct-2501.Q8_0.gguf"
    elif args.model_type == "qwen3":
        path = "/home/jordi/sc/llama/llama.cpp/download/Qwen3-30B-A3B-Q8_0.gguf"
    else:
        if args.model_type not in ["gpt", "gemini"]:
            raise "Unknown model"
        else:
            path = None

    llm = load_llm(args.model_type, path)
    prompt, metadata = load_prompt(args.model_type, args.prompt_version), load_metadata(
        args.model_type, args.prompt_version
    )

    dataset = "dataset/dataset.tmx"
    strings = load_strings(dataset, args.max)
    total_strings = min(len(strings), args.max)

    tp = fp = fn = tn = processed = 0
    start_time = time.time()

    with open(
        f"output/results-{args.max}-{args.model_type}-v{args.prompt_version}.txt",
        "w",
        encoding="utf-8",
    ) as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(llm, prompt, en, ca)
            processed += 1

            if idx % 10 == 0 or idx == args.max:
                elapsed = time.time() - start_time
                precision, recall, spm, f1 = calc_metrics(
                    tp, fp, fn, elapsed, processed
                )
                print(
                    f"Progress: {(idx/total_strings)*100:.2f}% - {idx}/{total_strings} | "
                    f"set/min: {spm:.2f} | Time: {elapsed:.2f}s | "
                    f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn} | "
                    f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1 {f1:.2f}"
                )

            remove_thinking = re.sub(r"<think>.*?</think>", "", res, flags=re.DOTALL)
            full_answer = res
            if res != remove_thinking:
                print(f"Removed thinking: ### {res} ###")
                res = remove_thinking.strip()

            if res.upper().startswith("NO"):
                if note:
                    fn += 1
                    _write(en, ca, note, full_answer, file, "fn")
                else:
                    tn += 1
                continue

            if not res.upper().startswith("YES"):
                full_answer = f"Answer is not 'YES' or 'NO'\n" + full_answer

            if note:
                tp += 1
                _write(en, ca, note, full_answer, file, "tp")
            else:
                fp += 1
                _write(en, ca, note, full_answer, file, "fp")

    total_time = time.time() - start_time
    prompt_version = args.prompt_version
    prompt_comment = metadata
    save_json.save_json(
        args.model_type,
        prompt_version,
        prompt_comment,
        tp,
        fp,
        fn,
        tn,
        precision,
        recall,
        f1,
        total_time,
        processed,
    )
    print(f"Total time used: {total_time:.2f} seconds")
