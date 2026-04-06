import asyncio, edge_tts, json 
async def main(): 
    v = await edge_tts.list_voices() 
    print(json.dumps([x for x in v][:2])) 
asyncio.run(main()) 
