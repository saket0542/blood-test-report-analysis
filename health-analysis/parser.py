import re
from io import BytesIO
from pypdf import PdfReader

NUM = r"\d+(?:[.,]\d+)?"
ROW = re.compile(
    rf"^(?P<name>[A-Za-z][A-Za-z0-9 ,.()/%&'\-]{{1,60}}?)\s+(?P<value>{NUM})\s*(?P<unit>[A-Za-zµ%/^0-9.*]+(?:/[A-Za-z0-9µ.]+)?)?\s+"
    rf"(?P<range>(?:{NUM}\s*[-–]\s*{NUM})|(?:[<>≤≥]=?\s*{NUM}))\s*(?P<unit2>[A-Za-zµ%/^0-9.*]+)?\s*$"
)
RANGE = re.compile(rf"({NUM})\s*[-–]\s*({NUM})")
LIMIT = re.compile(rf"([<>≤≥])=?\s*({NUM})")


def extract_text(data: bytes) -> str:
    reader = PdfReader(BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _f(s: str) -> float:
    return float(s.replace(",", ""))


def _status(value: float, rng: str) -> str:
    if m := RANGE.fullmatch(rng.strip()):
        lo, hi = _f(m[1]), _f(m[2])
        return "Low" if value < lo else "High" if value > hi else "Normal"
    if m := LIMIT.fullmatch(rng.strip()):
        lim = _f(m[2])
        if m[1] in "<≤":
            return "High" if value > lim else "Normal"
        return "Low" if value < lim else "Normal"
    return "Normal"


def parse_results(text: str) -> list[dict]:
    rows, seen = [], set()
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        m = ROW.match(line)
        if not m:
            continue
        name = m["name"].strip()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        value = _f(m["value"])
        rows.append({
            "test": name,
            "value": m["value"],
            "unit": m["unit"] or m["unit2"] or "",
            "range": m["range"],
            "status": _status(value, m["range"]),
        })
    return rows


def fallback_text(text: str, limit: int = 6000) -> str:
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    lines = [l for l in lines if re.search(r"\d", l) and len(l) > 6]
    return "\n".join(lines)[:limit]
