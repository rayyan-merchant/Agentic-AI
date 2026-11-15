from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from calculations import *

FONT = Path("C:/Windows/Fonts")
FALLBACK_FONT = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

def plot_font(size):
    for path in (FONT / "segoeui.ttf", FALLBACK_FONT):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()
def make_plot(name, title, xmax, ymax, curves, log=False):
    width, height = 1240, 650
    im = Image.new("RGB",(width,height),"white")
    draw = ImageDraw.Draw(im)
    font = plot_font
    x0,y0,x1,y1=130,520,1165,100
    X=lambda x: x0+(x1-x0)*x/xmax
    Y=lambda y: y0-(y0-y1)*(math.log10(max(y,10)/10)/math.log10(ymax/10) if log else y/ymax)
    draw.text((35,23),title,fill="#123446",font=font(32))
    draw.text((35,63),"USD per month"+("  ·  logarithmic scale" if log else ""),fill="#496475",font=font(20))
    ticks=[10,100,1000,10000] if log else [i*ymax/5 for i in range(6)]
    for value in ticks:
        draw.line((x0,Y(value),x1,Y(value)), fill="#d6e0e6")
        draw.text((x0-20,Y(value)),f"${value:,.0f}",anchor="rm",fill="#304b5a",font=font(17))
    if log:
        for i,m in enumerate(MODELS):
            x=X(i+.5)
            values=[monthly_cost(m),monthly_cost(m,.5,caching=True)]
            for j,color in enumerate(("#376681","#1e927e")):
                start=x-24+25*j
                draw.rectangle((start,Y(values[j]),start+23,y0),fill=color)
            draw.text((x,y0+12),str(i+1),anchor="mt",font=font(17),fill="#304b5a")
    else:
        for i in range(6):
            x=xmax*i/5
            draw.text((X(x),y0+12),f"{x:,.0f}",anchor="mt",font=font(17),fill="#304b5a")
        for _,color,points in curves:
            draw.line([(X(x),Y(y)) for x,y in points],fill=color,width=4)
        draw.line((X(Q),y0,X(Q),y1),fill="#596c79",width=2)
        draw.text((X(Q)+8,y0-30),f"Assigned Q = {Q:,}",fill="#304b5a",font=font(17))
    draw.text(((x0+x1)/2,y0+48),"Model row number" if log else "Normal-day queries",anchor="mt",font=font(19),fill="#304b5a")
    for i,(label,color,_) in enumerate(curves):
        x=130+i*330
        draw.rectangle((x,605,x+19,623),fill=color)
        draw.text((x+26,600),label,font=font(18),fill="#304b5a")
    im.save(ROOT/name)

def plots():
    make_plot("api_cost.png","Monthly API cost by model",12,13000,
              [("No cache","#376681",None),("50% read scenario","#1e927e",None)],True)
    xmax=15000
    def steps(price):
        levels = [(0,price)]
        for k in range(1,math.ceil(xmax/BREAK_CAP)):
            levels.extend([(k*BREAK_CAP,k*price),(k*BREAK_CAP,(k+1)*price)])
        return levels+[(xmax,gpu_cost(xmax,price))]
    make_plot("break_even.png","Continuous API cost and GPU capacity steps",xmax,4000,
              [("RTX 4090 Secure","#376681",steps(GPU_MONTH)),
               ("RTX 4090 Community","#8c6548",steps(COMMUNITY_GPU_MONTH)),
               ("GPT-6 Luna optimized","#1e927e",[(0,0),(xmax,xmax*SLOPE)])])

if __name__ == "__main__":
    plots()
