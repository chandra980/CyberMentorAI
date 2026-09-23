#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"
OUT.mkdir(exist_ok=True)

size=512
im=Image.new("RGBA",(size,size),(5,11,18,255))
d=ImageDraw.Draw(im)
# subtle terminal frame
d.rounded_rectangle((28,28,size-28,size-28),radius=92,fill=(8,24,38,255),outline=(44,228,180,255),width=10)
# shield
shield=[(256,82),(390,132),(374,302),(350,365),(302,414),(256,442),(210,414),(162,365),(138,302),(122,132)]
d.polygon(shield,fill=(12,54,67,255),outline=(44,228,180,255))
# inner circuit / cross
d.rounded_rectangle((232,164,280,356),radius=14,fill=(238,250,255,255))
d.rounded_rectangle((166,230,346,278),radius=14,fill=(238,250,255,255))
# center terminal dot
d.ellipse((242,242,270,270),fill=(5,11,18,255))
png=OUT/"CyberMentorAI.png"
ico=OUT/"CyberMentorAI.ico"
im.save(png)
im.save(ico,format="ICO",sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print(png)
print(ico)
