def dummy_llm_extract(text: str) -> dict:
    # In future: call Mistral / Phi-3 via Ollama or HuggingFace
    return {
        "compliance_type": "Regulatory Update",
        "summary": "Extracted via placeholder",
        "key_points": ["Due date pending", "Applies to DISCOMs/GENCOs"]
    }