# ======================================
# backend/compliance_extractor.py   ← NEW
# ======================================
import re
from typing import List, Dict

def extract_compliance_obligations(full_text: str) -> List[Dict]:
    obligations = []
    
    # Simple but better sentence splitter
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
        
        found = []
        for pat in obligation_patterns:
            if re.search(pat, sent, re.IGNORECASE):
                found.append(pat)
        
        if found:
            section_match = re.search(r'(Regulation|Section|Clause|Para)\s*(\d+[.\d]*)', sent, re.I)
            section = section_match.group(0) if section_match else "N/A"
            
            obligations.append({
                "obligation": sent[:300] + ("..." if len(sent) > 300 else ""),
                "section": section,
                "keywords": [w.lower() for w in ["shall", "must", "required", "should"] if w.lower() in sent.lower()],
                "confidence": "high" if "shall" in sent.lower() or "must" in sent.lower() else "medium",
                "source_text_length": len(sent)
            })
    
    return obligations[:20]  # limit per doc for prototype