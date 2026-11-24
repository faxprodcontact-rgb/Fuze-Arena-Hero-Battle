# python3 avantapres.py <nom> <id>  → refonte-graphique/pixel/sortie/hd-<nom>-premier-jet.png
import sys; import os; R=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))+'/'
sys.path.insert(0,R+'refonte-graphique/pixel/hd')
import hd
from PIL import Image, ImageDraw
name,cid=sys.argv[1:3]
old=Image.open(R+f'public/art/px/{cid}.webp').convert('RGBA'); cw=old.width//8
o=old.crop((0,0,cw,old.height)).resize((cw//3,old.height//3),Image.NEAREST).resize((cw//3*6,old.height//3*6),Image.NEAREST)
n=hd.frames(name)[0]; n=n.resize((n.width*4,n.height*4),Image.NEAREST)
W=o.width+n.width; H=max(o.height,n.height)+30
im=Image.new('RGBA',(W,H),(232,236,242,255)); im.alpha_composite(o,(0,H-o.height)); im.alpha_composite(n,(o.width,H-n.height))
d=ImageDraw.Draw(im); d.text((10,8),'avant',fill=(30,20,36,255)); d.text((o.width+10,8),'premier jet HD',fill=(30,20,36,255))
p=R+f'refonte-graphique/pixel/sortie/hd-{name}-premier-jet.png'; im.convert('RGB').save(p); print(p)
