import re
import json
from typing import List, Dict

from backend.utils import logger

import requests
import json
import requests
import json
import re

from backend.utils import logger

import requests
import json
import re

from backend.utils import logger

import requests
import json
import re

from backend.utils import logger

def enhance_with_llm(obligation_text: str) -> Dict:
    """
    Call LM Studio API with strict prompt and heavy post-processing to fix
    common model mistakes (extra braces, stray quotes, trailing junk).
    """
    try:
        url = "http://localhost:1234/v1/chat/completions"

        payload = {
            "model": "lmstudio-community/Phi-3.1-mini-4k-instruct-GGUF",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You MUST output **ONLY** a single valid JSON object. "
                        "Nothing before it, nothing after it. "
                        "No explanations, no markdown, no ```json, no extra braces, no trailing commas, "
                        "no stray quotes, no comments, no extra lines. "
                        "Use double quotes for all strings. "
                        "End exactly with the closing } and nothing else.\n\n"
                        "Strict structure:\n"
                        "{\n"
                        '  "compliance_type": "short category",\n'
                        '  "due_date": "YYYY-MM-DD or within X days/months or N/A",\n'
                        '  "affected_entity": "entity name",\n'
                        '  "risk_level": "High or Medium or Low",\n'
                        '  "short_summary": "one concise sentence"\n'
                        "}\n"
                        "Do not add any text after the final }."
                    )
                },
                {"role": "user", "content": obligation_text}
            ],
            "temperature": 0.1,
            "max_tokens": 450,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"].strip()

        # ── Heavy cleaning pipeline ─────────────────────────────────────────────

        # 1. Strip leading/trailing junk
        raw = raw.strip('` \n\r\t')

        # 2. Remove code fences if any
        raw = re.sub(r'^```json?\s*|\s*```?$', '', raw, flags=re.IGNORECASE | re.MULTILINE).strip()

        # 3. Cut everything after the last }
        last_brace_pos = raw.rfind('}')
        if last_brace_pos != -1:
            raw = raw[:last_brace_pos + 1]

        # 4. Remove extra closing braces or stray quotes at end
        raw = re.sub(r'"\s*"\s*\}\s*$', '"}', raw)           # double quote before }
        raw = re.sub(r'\}\s*"\s*$', '}', raw)               # stray " after }
        raw = re.sub(r'\}\s*\}\s*$', '}', raw)              # double }

        # 5. Fix trailing comma before last }
        raw = re.sub(r',\s*([}\]])', r'\1', raw)

        # 6. If last value is unclosed string → force close it
        if re.search(r':\s*"[^"]+\s*$', raw):
            raw = raw.rstrip() + '" }'

        # 7. Final parse attempt
        try:
            enhanced = json.loads(raw)
        except json.JSONDecodeError as inner_e:
            # Last rescue: remove everything after first complete object
            first_complete = re.search(r'\{[^}]+\}', raw)
            if first_complete:
                raw = first_complete.group(0)
                enhanced = json.loads(raw)
            else:
                raise inner_e

        # Validate keys
        required = {"compliance_type", "due_date", "affected_entity", "risk_level", "short_summary"}
        if not required.issubset(enhanced):
            raise ValueError(f"Missing keys: {required - set(enhanced.keys())}")

        return enhanced

    except Exception as e:
        logger.warning(f"LLM call failed. Raw output:\n{raw}\nError: {e}")
        return {
            "compliance_type": "Unknown",
            "due_date": "N/A",
            "affected_entity": "General",
            "risk_level": "Medium",
            "short_summary": "LLM output invalid or connection failed"
        }

def extract_compliance_obligations(full_text: str) -> List[Dict]:
    obligations = []
    llm_call_count = 0                    # track how many times we called LLM
    MAX_LLM_CALLS_PER_DOC = 6             # ← change this number if needed (6 is good balance)

    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s+', full_text)
    
    obligation_patterns = [
        r'(shall|must|required to|should|shall ensure|shall comply|shall submit|obligation of)',
        r'(within \d+ (days|months)|by \d{1,2}[/-]\d{1,2}[/-]\d{2,4}|latest by|deadline)',
        r'(Regulation \d+|Section \d+|Clause \d+|Para \d+)'
    ]
    
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 60:
            continue
        
        found = any(re.search(pat, sent, re.IGNORECASE) for pat in obligation_patterns)
        
        if found:
            section_match = re.search(r'(Regulation|Section|Clause|Para)\s*(\d+[.\d]*)', sent, re.I)
            section = section_match.group(0) if section_match else "N/A"
            
            # Basic risk (improved)
            risk_level = "High" if any(kw in sent.lower() for kw in ["penalty", "fine", "immediate", "urgent", "shall pay", "within 7", "within 5"]) else "Medium"

            base = {
                "obligation": sent[:300] + ("..." if len(sent) > 300 else ""),
                "section": section,
                "keywords": [w.lower() for w in ["shall", "must", "required", "should"] if w.lower() in sent.lower()],
                "confidence": "high" if "shall" in sent.lower() or "must" in sent.lower() else "medium",
                "risk_level": risk_level,
                "source_text_length": len(sent)
            }

            # LLM enhancement – only on high-confidence + limited count
            if base["confidence"] == "high" and llm_call_count < MAX_LLM_CALLS_PER_DOC:
                enhanced = enhance_with_llm(sent)
                base.update(enhanced)
                llm_call_count += 1
            else:
                # Fast fallback – no LLM cost/delay
                base.update({
                    "compliance_type": "Unknown",
                    "due_date": "N/A",
                    "affected_entity": "General",
                    "risk_level": base["risk_level"],  # keep the basic risk we already calculated
                    "short_summary": "Basic rule-based detection (LLM skipped for speed)"
                })

            obligations.append(base)
    
    return obligations[:30]  # keep the document limit