import re, urllib.request, html
from html.parser import HTMLParser

UA="MiniPCWatch/0.1 (personal price research; public HTML)"
urls={
"yahoo_item":"https://paypayfleamarket.yahoo.co.jp/item/z732559062",
"yahoo_search":"https://paypayfleamarket.yahoo.co.jp/search/%E3%83%9F%E3%83%8BPC?sort=-created",
"mercari_search":"https://jp.mercari.com/search?keyword=%E3%83%9F%E3%83%8BPC&status=on_sale&sort=created_time&order=desc"
}
class Meta(HTMLParser):
 def __init__(self):
  super().__init__();self.m=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('meta','script','a'):
   a=dict(attrs)
   if tag=='meta' and ('og:' in a.get('property','') or a.get('name','') in ('description','robots')):
    self.m.append((a.get('property') or a.get('name'),a.get('content','')[:240]))
   if tag=='script' and a.get('type')=='application/ld+json':self.m.append(('ld+json','present'))
   if tag=='script' and a.get('id')=='__NEXT_DATA__':self.m.append(('next-data','present'))
for name,u in urls.items():
 try:
  req=urllib.request.Request(u,headers={'User-Agent':UA,'Accept-Language':'ja,en;q=0.8'})
  with urllib.request.urlopen(req,timeout=20) as res:
   body=res.read(3_000_000).decode('utf-8','replace')
   meta=Meta();meta.feed(body)
   print('PAGE',name,res.status,'len',len(body),'meta',repr(meta.m[:18]),flush=True)
   for pattern in ('item/m[0-9]+','m[0-9]{11}','__NEXT_DATA__','soldOut','sold_out','price','掲載終了','SOLD','在庫なし','円'):
    matches=list(re.finditer(pattern,body,flags=re.I))
    print('PATTERN',name,pattern,'count',len(matches),'sample',html.unescape(re.sub(r'\\s+',' ',body[max(0,matches[0].start()-110):matches[0].end()+110]))[:260] if matches else '',flush=True)
 except Exception as e: print('ERROR',name,type(e).__name__,str(e),flush=True)
