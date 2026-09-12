"""Evidence-driven Pillow reconstructions, following campaign visual convention."""
import json,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
FONT=Path('/System/Library/Fonts/Supplemental');W=1120
COLORS=[('#1a73e8','#e8f0fe'),('#137333','#e6f4ea'),('#b3261e','#fce8e6')]
def font(size=32,bold=False,code=False):
 return ImageFont.truetype(str(FONT/('Courier New.ttf' if code else 'Arial Bold.ttf' if bold else 'Arial.ttf')),size)
def panel(label,kind,data,color,diagnostic=None):
 lines=textwrap.wrap(diagnostic,78) if diagnostic else []
 if kind=='source': data=[line for s in data.splitlines() for line in (textwrap.wrap(s,62,replace_whitespace=False,drop_whitespace=False) or [''])];h=80+38*len(data)
 elif kind=='table':h=80+65*len(data)
 else:h=80+48*len(data)
 h+=22+32*len(lines)
 im=Image.new('RGB',(W,h),'white');d=ImageDraw.Draw(im)
 d.rounded_rectangle((12,8,W-12,49),radius=7,fill=color[1]);d.text((26,13),label,fill=color[0],font=font(26,True));y=76
 if kind=='source':
  d.rectangle((28,65,W-28,h-20-32*len(lines)),fill='#f1f3f4')
  for t in data:d.text((42,y),t,fill='#202124',font=font(28,code=True));y+=38
 elif kind=='table':
  for i,row in enumerate(data):
   for j,t in enumerate(row):
    x=42+j*480;d.rectangle((x,y,x+480,y+65),outline='#5f6368',width=2);d.text((x+18,y+13),t,fill='#202124',font=font(32,i==0))
   y+=65
 else:
  for row in data:
   x=42
   for seg in row:
    f=font(32,seg.get('bold',False),seg.get('code',False));t=seg['text'];width=d.textlength(t,font=f)
    d.text((x,y),t,fill='#1155cc' if seg.get('link') else '#202124',font=f)
    if seg.get('link'):d.line((x,y+35,x+width,y+35),fill='#1155cc',width=1)
    x+=width
   assert x<W-20,(label,x,row)
   y+=48
 if lines:
  y=h-32*len(lines)-10
  for line in lines:d.text((42,y),line,fill='#5f6368',font=font(23));y+=32
 return im
def main():
 out=ROOT/'figures';out.mkdir(exist_ok=True)
 for c in json.loads((ROOT/'confirmed.json').read_text()):
  panels=[panel('BEFORE — MARKDOWN SOURCE','source',c['markdown'],COLORS[0])]
  for label,key,col in [('EXPECTED','expected',COLORS[1]),('OBSERVED — LIVE GOOGLE DOC','observed',COLORS[2])]:
   p=c[key];panels.append(panel(label,p['kind'],p['data'],col,p.get('diagnostic')))
  im=Image.new('RGB',(W,sum(p.height for p in panels)+34),'white');y=0
  for p in panels:im.paste(p,(0,y));y+=p.height
  ImageDraw.Draw(im).text((25,y+4),'Reconstructed from synthetic inputs and native Google Docs readback; not a screenshot.',font=font(19),fill='#5f6368')
  im.save(out/(c['id']+'.png'));print(c['id'],im.size)
if __name__=='__main__':main()
