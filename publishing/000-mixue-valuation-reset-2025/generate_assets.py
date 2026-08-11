from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'assets')
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1200, 675
BG = '#ffffff'
INK = '#172033'
MUTED = '#637089'
BLUE = '#4f46e5'
LIGHT = '#cdd9ff'
ORANGE = '#f59e0b'
GREEN = '#10b981'
RED = '#ef4444'
GRID = '#e8ecf4'

font_candidates = [
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
]
font_path = next((p for p in font_candidates if Path(p).exists()), font_candidates[-1])

def font(size):
    return ImageFont.truetype(font_path, size)

def canvas(title, subtitle=''):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((70, 45), title, fill=INK, font=font(44))
    if subtitle:
        d.text((72, 105), subtitle, fill=MUTED, font=font(24))
    d.line((70, 145, 1130, 145), fill=GRID, width=2)
    return im, d

def save(im, name):
    im.save(OUT / name, 'WEBP', quality=90, method=6)

def bars(d, labels, series, colors, top=210, bottom=560, left=120, right=1080):
    maxv = max(max(vals) for vals in series) * 1.1
    n = len(labels)
    group = (right-left)/n
    bw = group/(len(series)+1)
    for i, lab in enumerate(labels):
        x0 = left + i*group
        for j, vals in enumerate(series):
            v = vals[i]
            h = (bottom-top)*v/maxv
            x = x0 + (j+0.35)*bw
            d.rounded_rectangle((x, bottom-h, x+bw*0.75, bottom), radius=8, fill=colors[j])
            d.text((x, bottom-h-28), f'{v:.1f}', fill=INK, font=font(18))
        d.text((x0+group*0.32, bottom+14), str(lab), fill=MUTED, font=font(20))
    d.line((left,bottom,right,bottom), fill='#b8c2d8', width=2)

def line_chart(d, years, series, colors, top=210, bottom=550, left=120, right=1080):
    vals = [v for s in series for v in s]
    maxv = max(vals)*1.1
    minv = 0
    for gy in range(5):
        y=top+(bottom-top)*gy/4
        d.line((left,y,right,y), fill=GRID, width=2)
    xs=[left+(right-left)*i/(len(years)-1) for i in range(len(years))]
    for s,c in zip(series,colors):
        pts=[]
        for x,v in zip(xs,s):
            y=bottom-(bottom-top)*(v-minv)/(maxv-minv)
            pts.append((x,y))
        d.line(pts, fill=c, width=5)
        for x,y in pts:
            d.ellipse((x-7,y-7,x+7,y+7), fill=BG, outline=c, width=4)
    for x,yr in zip(xs,years):
        d.text((x-30,bottom+18),str(yr),fill=MUTED,font=font(19))

# Cover
im,d=canvas('蜜雪集团：利润没崩，高估值为什么消失？','2025 年核心财务与估值矛盾')
items=[('营收','335.6亿','+35.2%'),('归母净利润','59.3亿','+33.1%'),('经营现金流','60.39亿','同比约 +0.5%'),('现金+金融资产','接近200亿','资本配置待验证')]
for i,(a,b,c) in enumerate(items):
    y=195+i*95
    d.rounded_rectangle((80,y,640,y+70),radius=16,fill='#f7f8fc',outline=GRID,width=2)
    d.text((105,y+18),a,fill=MUTED,font=font(22)); d.text((280,y+13),b,fill=INK,font=font(30)); d.text((480,y+19),c,fill=BLUE,font=font(20))
d.text((710,215),'市场重新定价三件事',fill=INK,font=font(30))
for i,t in enumerate(['国内：从开店数量转向单店质量','海外：复制能力尚未证明','资本：留存现金能否创造高回报']):
    d.ellipse((715,285+i*85,735,305+i*85),fill=ORANGE)
    d.text((755,278+i*85),t,fill=INK,font=font(22))
d.text((80,620),'数据来源：蜜雪集团 2025 年报 / DupontMaster 研究整理',fill=MUTED,font=font(17))
save(im,'cover.webp')

# Revenue/profit
im,d=canvas('增长仍在：营收与利润继续高增','营业收入与归母净利润，亿元')
years=[2021,2022,2023,2024,2025]
rev=[103.5,136.0,203.0,248.3,335.6]; profit=[19.1,20.1,31.9,44.5,59.3]
bars(d,years,[rev,profit],[LIGHT,BLUE])
d.text((120,610),'2025：营收 +35.2%，归母净利润 +33.1%',fill=INK,font=font(22))
save(im,'revenue_profit.webp')

# Cashflow
im,d=canvas('现金流质量：利润与现金的节奏开始错位','经营现金流 OCF 与自由现金流 FCF，亿元')
ocf=[16.92,24.31,37.94,62.13,60.39]; fcf=[7.39,11.71,21.04,45.60,53.54]
line_chart(d,years,[ocf,fcf],[LIGHT,BLUE])
d.text((130,170),'OCF',fill=LIGHT,font=font(20)); d.text((210,170),'FCF',fill=BLUE,font=font(20))
d.text((120,610),'2025 OCF 60.39亿，同比仅约 +0.5%；FCF 约53.54亿',fill=INK,font=font(21))
save(im,'cashflow.webp')

# Inventory
im,d=canvas('库存增速明显快于收入','存货与原材料库存，亿元')
bars(d,['2024','2025'],[[22.15,36.73],[6.35,22.52]],[LIGHT,ORANGE],left=250,right=950)
d.text((120,610),'存货约 +65.8%；原材料库存约 +255% —— 这是验证信号，不是“压货”结论',fill=INK,font=font(20))
save(im,'inventory.webp')

# Assets
im,d=canvas('钱很多：资本配置成为估值核心问题','2025 年主要资产结构，亿元')
labels=['类现金资产','投资性资产','生产性资产','经营性资产','其他资产']; vals=[110.54,97.28,56.32,42.21,1.59]
maxv=max(vals)
for i,(lab,v) in enumerate(zip(labels,vals)):
    y=205+i*75
    d.text((100,y+8),lab,fill=INK,font=font(23))
    d.rounded_rectangle((330,y,330+650*v/maxv,y+42),radius=10,fill=[BLUE,'#8b5cf6',ORANGE,GREEN,'#9ca3af'][i])
    d.text((1010,y+8),f'{v:.2f}',fill=MUTED,font=font(21))
d.text((100,610),'总资产约307.94亿；类现金与投资性资产占比较高',fill=INK,font=font(21))
save(im,'asset_structure.webp')

# Valuation
im,d=canvas('三种未来，对应三种价值','情景估值仅用于研究框架，港元/股')
sc=['悲观','基准','乐观']; vals=[155,305,485]; cols=[RED,BLUE,GREEN]
for i,(lab,v,c) in enumerate(zip(sc,vals,cols)):
    x=220+i*320; h=330*v/520
    d.rounded_rectangle((x,540-h,x+150,540),radius=14,fill=c)
    d.text((x+35,560),lab,fill=INK,font=font(24)); d.text((x+42,500-h),str(v),fill=INK,font=font(28))
d.line((120,405,1080,405),fill=ORANGE,width=4)
d.text((850,370),'参考股价 212.6',fill=ORANGE,font=font(20))
d.text((120,625),'155 / 305 / 485 港元不是短期目标价，不构成投资建议',fill=MUTED,font=font(19))
save(im,'valuation_scenarios.webp')

print('generated:', ', '.join(sorted(p.name for p in OUT.glob('*.webp'))))
