import re 
with open("c:/aifen/backend/services/multilingual_voices.py", "r", encoding="utf8") as f: text = f.read() 
with open("voices_generated.py", "r", encoding="utf8") as f: insert = f.read() 
text = re.sub(r'MULTILINGUAL_VOICES\s*=\s*{.*?}(?=\s*def get_voice_for_language)', insert + "\n", text, flags=re.DOTALL) 
with open("c:/aifen/backend/services/multilingual_voices.py", "w", encoding="utf8") as f: f.write(text) 
