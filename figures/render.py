"""Pillow Before / Expected / Observed illustrations from synthetic live evidence.
Follows campaign-private's visual convention; these are reconstructions, not screenshots.
Run: uv run --with pillow python figures/render.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).parent
FONT=Path('/System/Library/Fonts/Supplemental')
W=1120
COLORS=[('#1a73e8','#e8f0fe'),('#137333','#e6f4ea'),('#b3261e','#fce8e6')]
def font(size=32,bold=False):return ImageFont.truetype(str(FONT/('Arial Bold.ttf' if bold else 'Arial.ttf')),size)
def panel(label,rows,color,diagnostic=None):
 h=82+len(rows)*54+(64 if diagnostic else 0)
 im=Image.new('RGB',(W,h),'white');d=ImageDraw.Draw(im)
 d.rounded_rectangle((12,8,W-12,49),radius=7,fill=color[1]);d.text((26,13),label,fill=color[0],font=font(26,True))
 y=76
 for indent,segments in rows:
  x=42+indent
  for text,bold in segments:
   f=font(32,bold);d.text((x,y),text,fill='#202124',font=f);x+=d.textlength(text,font=f)
  assert x<W-20,(label,x)
  y+=54
 if diagnostic:
  d.rectangle((28,y+3,W-28,y+52),fill='#eef1f4')
  d.text((40,y+12),'Diagnostic: '+diagnostic,fill='#5f6368',font=font(23))
 return im
cases={
 'gdoc-bold-loss':{
  'rows':[
   [(0,[('Keep this bold.',True),(' Send the draft today.',False)])],
   [(0,[('Keep this bold.',True),(' Send the final today.',False)])],
   [(0,[('Keep this bold.',False),(' Send the final today.',False)])]],
  'diagnostic':[None,None,'gdoc reports success; native bold style is gone.']},
 'gdoc-unicode-search':{
  'rows':[
   [(0,[('İ cat',False)])],
   [(0,[('İ dog',False)])],
   [(0,[('İ cdog',False)])]],
  'diagnostic':[None,None,'gdoc reports success; replacement starts one position late.']},
 'shared-nested-list':{
  'rows':[
   [],
   [(0,[('•  Parent',False)]),(55,[('◦  Child',False)]),(0,[('•  Peer',False)])],
   [(0,[('•  Parent',False)]),(0,[('•  Child',False)]),(0,[('•  Peer',False)])]],
  'diagnostic':['Blank document tab.',None,'Both tools: Child has the same nesting level as Parent and Peer.']}
}
for name,c in cases.items():
 panels=[panel(label,c['rows'][i],COLORS[i],c['diagnostic'][i]) for i,label in enumerate(['BEFORE','EXPECTED','OBSERVED'])]
 final=Image.new('RGB',(W,sum(x.height for x in panels)+24),'white');y=0
 for im in panels:final.paste(im,(0,y));y+=im.height
 ImageDraw.Draw(final).text((25,y+2),'Reconstructed illustration from synthetic tests; not a Google Docs screenshot.',font=font(17),fill='#5f6368')
 final.save(ROOT/(name+'.png'))
 print(name,final.size)
