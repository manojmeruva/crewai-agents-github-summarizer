import os, requests
r = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {os.getenv("GROQ_API_KEY")}'})
for m in r.json().get('data', []):
    print(m['id'])
