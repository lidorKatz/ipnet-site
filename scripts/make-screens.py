"""Author neutral simulated device displays; these are not live camera feeds."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont
root=Path(sys.argv[1]); root.mkdir(parents=True,exist_ok=True)
font="/usr/share/fonts/truetype/open-sans/OpenSans-Regular.ttf"
def f(size): return ImageFont.truetype(font,size)
for key,title,label,color in [
 ("calling","Visitor calling","CONNECTING…","#b7cbd9"),
 ("connected","You’re connected","CALL IN PROGRESS","#b7cbd9"),
 ("granted","Welcome inside","ACCESS GRANTED","#97cbb4")]:
 image=Image.new("RGB",(500,640),"#122126"); d=ImageDraw.Draw(image)
 d.text((28,27),"BUILDING ENTRY",font=f(20),fill="#d8e1e3")
 d.ellipse((447,30,456,39),fill="#8ab596")
 d.line((25,71,475,71),fill="#3a5158",width=2)
 d.rounded_rectangle((28,99,472,394),radius=5,fill="#293f46")
 d.polygon([(45,370),(205,168),(340,168),(455,370)],fill="#8e968c")
 d.rectangle((74,120,171,358),fill="#55685e")
 d.rectangle((205,168,340,340),fill="#1b2e32")
 d.line((225,180,225,325),fill="#7c9596",width=4)
 d.text((49,113),"ENTRANCE / LIVE",font=f(14),fill="#d5ddd8")
 d.text((28,433),title,font=f(31),fill="#edf0eb")
 d.text((28,485),"Reception · Main entrance",font=f(17),fill="#9eb2b6")
 d.rounded_rectangle((28,541,472,602),radius=7,fill=color)
 d.text((65,558),label,font=f(18),fill="#14262c")
 image.save(root/(key+".png"))
image=Image.new("RGB",(900,530),"#101c20"); d=ImageDraw.Draw(image)
d.text((30,22),"CONNECTED PROPERTY / SYSTEM VIEW",font=f(22),fill="#d3e0de")
for i,title in enumerate(["MAIN ENTRY","LOBBY","SIDE ENTRY","CORRIDOR"]):
 x=25+(i%2)*340; y=77+(i//2)*216
 d.rectangle((x,y,x+323,y+198),fill="#455951")
 d.polygon([(x,y+180),(x+145,y+55),(x+205,y+55),(x+320,y+180)],fill="#7e8878")
 for k in range(3): d.rectangle((x+25+k*100,y+20,x+80+k*100,y+125),fill="#253b35")
 d.rectangle((x,y+166,x+323,y+198),fill="#122326")
 d.text((x+12,y+173),title,font=f(14),fill="#d3dfd7")
for i,title in enumerate(["CAMERAS","ENTRY","NETWORK","WIRELESS"]):
 y=110+i*87
 d.ellipse((742,y,750,y+8),fill="#88bd99"); d.text((764,y-4),title,font=f(14),fill="#b7cbc2")
image.save(root/"monitor.png")
