import json,urllib.request,urllib.parse
from html.parser import HTMLParser
class P(HTMLParser):
 def __init__(self): super().__init__();self.a=False;self.data=''
 def handle_starttag(self,t,attrs):
  if t=='script' and dict(attrs).get('id')=='__NEXT_DATA__':self.a=True
 def handle_data(self,d):
  if self.a:self.data=d
 def handle_endtag(self,t):
  if t=='script':self.a=False
for sort in ['-created','created','new','-new','-start','-opened','-openTime','date','newest','-startTime']:
 u='https://paypayfleamarket.yahoo.co.jp/search/'+urllib.parse.quote('ミニPC')+'?'+urllib.parse.urlencode({'sort':sort})
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'ja,en;q=.8'})
  with urllib.request.urlopen(req,timeout=18) as r:body=r.read(2000000).decode('utf-8','replace')
  p=P();p.feed(body);obj=json.loads(p.data)
  x=obj['props']['initialState']['searchState']['search']
  print('SORT',sort,'=>',x.get('searchParams',{}).get('sort'),x.get('searchParams',{}).get('order'),'newest',[(v.get('id'),v.get('openTime')) for v in x['result']['items'][:2]],flush=True)
 except Exception as e:print('ERR',sort,str(e)[:180],flush=True)
