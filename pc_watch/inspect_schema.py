import json,urllib.request,re
from html.parser import HTMLParser
class Parser(HTMLParser):
 def __init__(self): super().__init__();self.active=False;self.text=""
 def handle_starttag(self,tag,attr):
  if tag=="script" and dict(attr).get("id")=="__NEXT_DATA__":self.active=True
 def handle_data(self,d):
  if self.active:self.text=d
 def handle_endtag(self,tag):
  if tag=="script":self.active=False
def json_for(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0","Accept-Language":"ja,en;q=0.8"})
 with urllib.request.urlopen(req,timeout=18) as r: txt=r.read(4500000).decode("utf-8","replace")
 p=Parser();p.feed(txt);return json.loads(p.text)
for name,url in [("search","https://paypayfleamarket.yahoo.co.jp/search/%E3%83%9F%E3%83%8BPC?sort=-created"),("item","https://paypayfleamarket.yahoo.co.jp/item/z733999054")]:
 try:
  obj=json_for(url);state=obj["props"]["initialState"]
  if name=="search":
   search=state["searchState"]["search"]
   print("SEARCH_KEYS",list(search))
   print("SEARCH_PAGINATION",[(k,str(v)[:300]) for k,v in search.items() if k!='auctionItemsModule'])
   module=search["auctionItemsModule"]
   print("MODULE_KEYS",list(module))
   for i,x in enumerate(module.get("items",[])[:3]):print("SEARCH_ITEM",i,json.dumps(x,ensure_ascii=False)[:2500])
   print("QUERY",json.dumps(obj["query"],ensure_ascii=False))
  else:
   print("ITEM",json.dumps(state["itemsState"]["items"]["item"],ensure_ascii=False)[:13000])
 except Exception as e:print("ERR",name,repr(e))
