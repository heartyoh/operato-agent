# rag/chunker.py

import os
import yaml

def load_dsls(dsl_dir="generated_dsl"):
    chunks = []
    for filename in os.listdir(dsl_dir):
        if not filename.endswith(".yaml"):
            continue
        with open(os.path.join(dsl_dir, filename), "r", encoding="utf-8") as f:
            dsl = yaml.safe_load(f)
            text = f"DSL `{dsl['name']}` ({dsl['type']}): {dsl['description']}\nQuery:\n{dsl['query_template']}"
            chunks.append({
                "id": dsl["name"],
                "text": text,
                "metadata": {
                    "name": dsl["name"],
                    "type": dsl["type"],
                    "variables": ", ".join(dsl.get("variables", [])),
                    "related_types": ", ".join(dsl.get("related_types", []))
                }
            })
    return chunks
