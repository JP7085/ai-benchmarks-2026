import os
import json
import requests
from datetime import datetime

# Configuration
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
DATA_FILE = 'data.json'

def query_perplexity(prompt):
    """Interroge l'API Perplexity pour récupérer les derniers benchmarks"""
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert en benchmarks d'IA. Réponds uniquement avec des données structurées en JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4000
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()['choices'][0]['message']['content']

def extract_benchmarks():
    """Récupère les derniers benchmarks depuis Perplexity"""
    prompt = """
Récupère les derniers scores de benchmarks pour ces modèles d'IA (février 2026) :

Modèles propriétaires :
- GPT-5.2 (OpenAI)
- Claude Opus 4.6 (Anthropic)
- Gemini 3.1 Pro (Google)
- Grok 4.1 (xAI)
- Perplexity Sonar-Reasoning-Pro

Modèles open source S-tier :
- Kimi K2.5 (Moonshot)
- DeepSeek V3.2
- GLM-4.7 (Zhipu AI)

Pour chaque modèle, fournis :
1. Score Intelligence Index / composite (0-100)
2. MMLU / GPQA (0-100)
3. Code : SWE-bench / HumanEval (0-100)
4. Search / Deep research (0-100)
5. Taille contexte (en milliers de tokens)
6. Prix relatif (1-100, 1=très bon marché, 100=cher)

Sources : LM Council, Artificial Analysis, Search Arena, DRACO, leaderboards open source.

Réponds au format JSON suivant (sans texte additionnel) :
{
  "update_date": "2026-02-26",
  "models": [
    {
      "name": "GPT-5.2 (xhigh)",
      "vendor": "OpenAI",
      "type": "proprietary",
      "mainUsage": ["text", "code"],
      "intelligence": 92,
      "mmlu": 87,
      "coding": 88,
      "search": 70,
      "context": 200,
      "price": 100,
      "notes": "Description courte"
    }
  ]
}
"""
    
    print("🔍 Interrogation de l'API Perplexity...")
    response = query_perplexity(prompt)
    
    # Extraction du JSON depuis la réponse
    import re
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
        return data
    else:
        raise ValueError("Impossible d'extraire le JSON de la réponse")

def update_data_file(new_data):
    """Met à jour le fichier data.json"""
    # Ajoute la date du jour
    new_data['update_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Écriture du fichier
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Fichier {DATA_FILE} mis à jour avec succès !")
    print(f"📊 {len(new_data['models'])} modèles référencés")
    print(f"📅 Date de mise à jour : {new_data['update_date']}")

def main():
    """Fonction principale"""
    if not PERPLEXITY_API_KEY:
        print("❌ Erreur : PERPLEXITY_API_KEY non définie")
        print("Définis cette variable d'environnement avec ta clé API")
        exit(1)
    
    try:
        # Récupération des benchmarks
        data = extract_benchmarks()
        
        # Mise à jour du fichier
        update_data_file(data)
        
        print("\n🎉 Mise à jour terminée avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
        exit(1)

if __name__ == "__main__":
    main()
