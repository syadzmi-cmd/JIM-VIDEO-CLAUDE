import asyncio, edge_tts, sys, ssl, os, json
import edge_tts.communicate as ec
ec._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE, RATE = "ms-MY-OsmanNeural", "+14%"
lines = json.load(open(sys.argv[1])); out = sys.argv[2]
async def one(L):
    c = edge_tts.Communicate(L["say"], VOICE, rate=RATE, boundary="WordBoundary", proxy=os.environ["HTTPS_PROXY"])
    words = []
    with open(f"{out}/{L['id']}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "s": ch["offset"]/1e7, "e": (ch["offset"]+ch["duration"])/1e7})
    L["words"] = words
async def main():
    for L in lines: await one(L)
asyncio.run(main())
json.dump(lines, open(f"{out}/words.json", "w"), ensure_ascii=False, indent=1)
for L in lines: print(L["id"], len(L["words"]), L["words"][0]["s"], L["words"][-1]["e"])
