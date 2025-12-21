from gtts import gTTS

import requests
from pathlib import Path
from libs.logger import LogLevel, get_logger
from helpers.file_utils import slugify

logger = get_logger()

def gen_voice_for_free_tts(text: str, output_path: str = "./outputs/", lang: str = "en"):
    Path(output_path).mkdir(parents=True, exist_ok=True)
    tts = gTTS(text, lang=lang)
    safe_filename = slugify(text)
    out_file = f"{output_path}/{safe_filename}.mp3"
    tts.save(out_file)
    logger.log(LogLevel.INFO, f"已生成語音檔: {out_file}")


class DictionaryAPI:
    def __init__(self):
        self.url = "https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}"
            
def fetch_pronunciation_audio(word: str, lang: str = "en") -> str | None:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    phonetics = data[0].get("phonetics", []) if data else []
    audios = [p.get("audio") for p in phonetics if p.get("audio")]
    return audios[0] if audios else None

def download_audio(audio_url: str, save_as: str = "voice.mp3") -> Path:
    r = requests.get(audio_url, timeout=30)
    r.raise_for_status()
    out = Path(save_as)
    out.write_bytes(r.content)
    return out

import re
def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\-]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")

if __name__ == "__main__":
    audio = fetch_pronunciation_audio("hello", "en")
    if audio:
        path = download_audio(audio, "hello.mp3")
        logger.log(LogLevel.SUCCESS, f"Saved: {path.resolve()}")
    else:
        logger.log(LogLevel.WARNING, "No audio found.")
