#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import yaml
from chromadb import Client
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

def extract_text_from_url(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

def build_yaml_prompt(topic, source_text):
    return f"""
You are a clinical assistant tasked with reading raw medical source material and generating a decision-oriented emergency protocol.

YAML-making is a process where you **read** clinical data and then create an **original, structured synopsis** that would help a physician rapidly assess and manage a medical emergency.

Do NOT summarize or quote. Extract decision logic and treatment guidance.

Topic: {topic}

Source Text:
"""
{source_text[:4000]}
"""

Format your output as YAML with the following structure:
- title
- tags
- description
- trigger_conditions
- decision_logic
- interventions
- escalation_criteria
- complications
- references
"""

def query_llm(prompt):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "mythomax",
        "prompt": prompt,
        "stream": False
    })
    return res.json()["response"]

def extract_tags_from_yaml(yaml_text):
    try:
        data = yaml.safe_load(yaml_text)
        return data.get("tags", [])
    except:
        return []

def insert_into_chromadb(doc_id, topic, yaml_text, tags):
    chroma_client = Client(Settings(persist_directory="chromadb"))
    embedder = SentenceTransformerEmbeddingFunction()
    collection = chroma_client.get_or_create_collection(name="medical_protocols", embedding_function=embedder)
    collection.add(documents=[yaml_text], ids=[doc_id], metadatas={"topic": topic, "tags": tags})

def main():
    parser = argparse.ArgumentParser(description="Generate YAML medical protocol from a webpage or PDF.")
    parser.add_argument("--topic", required=True, help="Title of the clinical topic")
    parser.add_argument("--url", help="Webpage URL to read")
    parser.add_argument("--pdf", help="Path to PDF file to read")
    args = parser.parse_args()

    if args.url:
        source_text = extract_text_from_url(args.url)
    elif args.pdf:
        source_text = extract_text_from_pdf(args.pdf)
    else:
        print("❌ Must specify either --url or --pdf")
        return

    prompt = build_yaml_prompt(args.topic, source_text)
    yaml_output = query_llm(prompt)

    filename = args.topic.lower().replace(" ", "_") + ".yaml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(yaml_output)
    print(f"✅ Saved YAML to {filename}")

    tags = extract_tags_from_yaml(yaml_output)
    insert_into_chromadb(doc_id=args.topic.lower().replace(" ", "_"), topic=args.topic, yaml_text=yaml_output, tags=tags)
    print(f"📦 Inserted into ChromaDB with tags: {tags}")

if __name__ == "__main__":
    main()