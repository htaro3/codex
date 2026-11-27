import json,re,urllib.request,html
from html.parser import HTMLParser
class S(HTMLParser):
 def __init__(self):super().__init__();self.next=None;self.active=False
 def handle_starttag(self,t,a):
  if t=='script' and dict(a).get('id')=='__NEXT_DATA__':self.active=True
 def handle_data(self,d):
  if self.active:self.next=d
 def handle_endtag(self,t):
  if t=='script':self.active=False
def load(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'ja,en;q=0.8'})
 with urllib.request.urlopen(req,timeout=20) as r:return r.read(4500000).decode('utf-8','replace')
def walk(d,p='',depth=0):
 if isinstance(d,dict):
  if any(k in d for k in ('price','itemId','item_id','sold','status','title')) and depth<15:
   print('FIELD',p,[(k,str(v)[:105]) for k,v in d.items() if k.lower() in ('price','status','title','itemid','item_id','sold','soldout','stockstatus','isavailable','name','is_sold')][:14],flush=True)
  for k,v in d.items():
   if depth<10 and (depth<=3 or any(i in k.lower() for i in ('item','product','detail','search','listing','status','price'))):walk(v,p+'/'+k,depth+1)
 elif isinstance(d,list):
  for i,v in enumerate(d[:2]):walk(v,p+'/'+str(i),depth+1)
for kind,url in [
 ('yahoo_item','https://paypayfleamarket.yahoo.co.jp/item/z732559062'),
 ('yahoo_search','https://paypayfleamarket.yahoo.co.jp/search/%E3%83%9F%E3%83%8BPC?sort=-created'),
 ('mercari_search','https://jp.mercari.com/search?keyword=%E3%83%9F%E3%83%8BPC&status=on_sale&sort=created_time&order=desc')]:
 try:
  src=load(url)
  print('KIND',kind,'len',len(src))
  if kind.startswith('yahoo'):
   parser=S();parser.feed(src);obj=json.loads(parser.next);walk(obj)
   print('TOP',list(obj.keys()),'initialState',list(obj.get('props',{}).keys()),'statekeys',list(obj.get('props',{}).get('initialState',{}).keys())[:30])
  else:
   for pat in ('m40984638124','status_SALE_STATUS_ON_SALE','itemId','searchItems','searchResult','created_time:desc'):
    matches=list(re.finditer(pat,src,flags=re.I))
    print('MERC',pat,'hits',len(matches),'ex',repr(src[max(0,matches[0].start()-260):matches[0].end()+350]) if matches else '')
 except Exception as e:print('ERR',kind,str(e))
