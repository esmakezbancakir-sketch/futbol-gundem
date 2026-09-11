import json
import re
import subprocess

from . import config

PROMPT_TEMPLATE = """Sen global futbol gündemini takip eden bir editörsün. Aşağıda RSS kaynaklarından
toplanmış ham futbol haberleri var (başlık + kısa açıklama + kaynak).

Görevin:
1. Bunlar arasından en önemli/popüler olan en fazla {max_topics} haberi seç
   (tekrar eden / aynı olayı anlatan haberleri birleştir, tek kayıt bırak).
2. Her biri için Türkçe, 2-3 cümlelik kısa bir özet yaz (haber diliyle, objektif).
3. Her biri için bir "competition" etiketi belirle (örn. "Premier League",
   "La Liga", "Champions League", "Serie A", "Bundesliga", "Diğer").
4. SADECE aşağıdaki formatta bir JSON array döndür, başka hiçbir metin yazma:

[
  {{
    "title": "Türkçe başlık",
    "summary": "Türkçe 2-3 cümlelik özet",
    "source_url": "orijinal link (girdideki link ile AYNI olmalı)",
    "source_name": "kaynak adı",
    "competition": "etiket"
  }}
]

Ham haberler:
{raw_entries}
"""


def _build_prompt(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        lines.append(
            f"- title: {e['title']}\n  link: {e['link']}\n  source: {e['source_name']}\n  desc: {e.get('summary_raw', '')[:400]}"
        )
    return PROMPT_TEMPLATE.format(
        max_topics=config.MAX_TOPICS_PER_RUN,
        raw_entries="\n".join(lines),
    )


def _extract_json_array(text: str):
    # Claude sometimes wraps output in a code fence even when told not to.
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    return json.loads(match.group(0))


def summarize_topics(entries: list[dict]) -> list[dict]:
    if not entries:
        return []

    prompt = _build_prompt(entries)
    result = subprocess.run(
        [config.CLAUDE_BIN, "-p", prompt, "--model", config.CLAUDE_MODEL],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr[:2000]}")

    return _extract_json_array(result.stdout)
