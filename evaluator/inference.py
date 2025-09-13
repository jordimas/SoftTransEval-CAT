import multiprocessing
import time
import yaml
import argparse
import logging
import re
import polib

# LangChain Gemma model
from langchain_community.chat_models import ChatLlamaCpp
from langchain.schema import SystemMessage, HumanMessage

logging.basicConfig(
    filename="inference.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# -------------------------
# Load Gemma 3
# -------------------------
def load_llm(model_path: str, temperature: float = 0):
    """Return Gemma 3 model (via llama.cpp)."""
    return ChatLlamaCpp(
        temperature=temperature,
        model_path=model_path,
        n_ctx=2048,
        n_gpu_layers=8,
        n_batch=64,
        max_tokens=512,
        n_threads=max(1, multiprocessing.cpu_count()),
        repeat_penalty=1.1,
        top_p=1.0,
        verbose=False,
    )


# -------------------------
# Args
# -------------------------
def get_args():
    parser = argparse.ArgumentParser(
        description="Run translation inference with Gemma 3."
    )
    parser.add_argument("--prompt_version", type=str, default="2_1")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument(
        "--model_path",
        default="/home/jordi/sc/llama/llama.cpp/download/google_gemma-3-12b-it-Q8_0.gguf",
        type=str,
        help="Path to Gemma 3 model file (.gguf)",
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="PO input file",
    )
    return parser.parse_args()


# -------------------------
# Prompt & Metadata
# -------------------------
def load_prompt(prompt_version: str):
    with open(f"config/gemma3/prompt-v{prompt_version}.txt", "r") as file:
        return file.read()


def load_metadata(prompt_version: str):
    try:
        prompt_version = int(prompt_version.replace("_", ""))
        with open(f"config/gemma3/metadata.yml", "r") as fh:
            data = yaml.safe_load(fh)
            return data["versions"][prompt_version]["goal"]
    except Exception as e:
        print(f"load_metadata. Error: {e}")
        return "Default prompt description"


# -------------------------
# Translation Inference
# -------------------------
def translate(llm, prompt: str, english: str, catalan: str) -> str:
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


def load_strings(dataset: str, max_entries=-1):
    po = polib.pofile(dataset)
    strings = []
    for idx, entry in enumerate(po, start=1):
        source = entry.msgid
        target = entry.msgstr
        note = entry.comment or ""
        strings.append((source, target, note))
        if max_entries > 0 and idx >= max_entries:
            break

    print(f"Loaded {len(strings)} strings from {dataset}")
    return strings


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    args = get_args()

    llm = load_llm(args.model_path)
    prompt, metadata = load_prompt(args.prompt_version), load_metadata(
        args.prompt_version
    )

    strings = load_strings(args.dataset, args.max)

    start_time = time.time()
    output = strings.replace(".po", ".txt")
    with open(
        strings,
        "w",
        encoding="utf-8",
    ) as file:
        for idx, (en, ca, note) in enumerate(strings, start=1):
            res = translate(llm, prompt, en, ca)

            lines = [
                f"English: {en}",
                f"Catalan: {ca}",
            ]
            if note:
                lines.append(f"Note: {note}")
            lines.append(f"Result: {res}")
            lines.append("\n-----------------------\n")

            content = "\n".join(lines)
            file.write(content + "\n")
            print(content)

    total_time = time.time() - start_time
    print(f"Total time used: {total_time:.2f} seconds")
