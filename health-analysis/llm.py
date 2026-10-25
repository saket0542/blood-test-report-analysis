import json
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

here = Path(__file__).parent
load_dotenv(here / ".env")
load_dotenv(here.parent / "simple-llm-calling" / ".env")

MODEL = "openai/gpt-oss-120b"

SYSTEM = (
    "You are a nutrition-aware health assistant for Indian users. Given blood test findings, "
    "reply with ONLY JSON: {\"summary\":str(<=60 words),"
    "\"abnormal\":[{\"test\":str,\"status\":str,\"meaning\":str(<=15 words)}],"
    "\"eat\":[{\"food\":str,\"why\":str(<=10 words)}],"
    "\"avoid\":[{\"food\":str,\"why\":str(<=10 words)}],\"tips\":[str]}. "
    "Foods must be common Indian foods (dal, millets, methi, palak, curd, amla, etc.) honoring the diet preference. "
    "Max 8 eat, 8 avoid, 4 tips. Not a diagnosis; advise consulting a doctor for serious deviations."
)


def analyze(findings: str, diet: str = "Vegetarian") -> tuple[dict, dict]:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Diet: {diet}\n{findings}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=1500,
        reasoning_effort="low",
    )
    u = resp.usage
    return json.loads(resp.choices[0].message.content), {
        "prompt": u.prompt_tokens, "completion": u.completion_tokens, "total": u.total_tokens,
    }
