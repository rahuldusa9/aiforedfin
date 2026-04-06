import asyncio, edge_tts, json 
async def main(): 
    voices = await edge_tts.list_voices() 
    d={} 
    names={} 
    for v in voices: 
        locale = v['Locale'].split('-')[0] 
        lang_name = v['FriendlyName'].split('- ')[-1].split(' (')[0].strip() 
        names[locale] = lang_name 
        if locale not in d: d[locale] = {'default': v['ShortName'], 'voices': []} 
        gender = 'VoiceGender.MALE' if v['Gender'] == 'Male' else 'VoiceGender.FEMALE' 
        style = 'VoiceStyle.NARRATOR' 
        d[locale]['voices'].append(f'VoiceProfile("{v["ShortName"]}", "{v["Locale"]}", "{lang_name}", {gender}, {style}, "{v["ShortName"]}")') 
    with open('voices_generated.py', 'w', encoding="utf8") as f: 
        f.write("MULTILINGUAL_VOICES = {\n") 
        for k,v in d.items(): 
            f.write(f'  "{k}": {{"default": "{v["default"]}", "voices": [\n') 
            for voice in v['voices']: f.write(f'    {voice},\n') 
            f.write("  ]},\n") 
        f.write("}\n\nLANGUAGE_NAMES = {\n") 
        for k,v in names.items(): 
            f.write(f'  "{k}": "{v}",\n') 
        f.write("}\n") 
asyncio.run(main()) 
