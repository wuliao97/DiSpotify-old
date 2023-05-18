import config as c
import json

with open(c.SR_CH, encoding="utf-8") as f:
    data = json.load(f)
    
data = data["characters"][0]

print(data["lang"]["ja"]["name"])