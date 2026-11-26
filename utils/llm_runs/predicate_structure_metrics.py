"""Số đo cấu trúc tên vị từ trên một thư mục processed (đọc predicates_named + rules). Dùng: python -X utf8 -I metrics.py <base>"""
import json,collections,sys,re
base=sys.argv[1]
P=[json.loads(l) for l in open(base+'/predicates/predicates_named_BLLD_45-2019.jsonl',encoding='utf-8')]
m=[p for p in P if p['loai']=='menh_de' and p.get('predicate')]
dieu=lambda u:u.split('.')[1]
by=collections.defaultdict(set)
for p in m: by[p['predicate']].add(dieu(p['unit']))
names=list(by)
ao=[n for n in names if re.search(r'(^|_)(and|or)(_|$)',n)]
lst=[p for p in m if re.search(r',|\s(và|hoặc)\s',p['span'])]
R=[json.loads(l) for l in open(base+'/rules/rules_BLLD_45-2019.jsonl',encoding='utf-8')]
iso=sum(1 for r in R if r.get('isolated'))
heads=collections.Counter(r['head']['pred'] for r in R)
bodyp=collections.Counter(b.get('pred') or b['atom'] for r in R for b in r['body'] if b.get('role')!='chu_the' and 'atom' in b)
dead=[p for p in bodyp if p not in heads]
print(f"dong menh_de co ten {len(m)} | ten khac nhau {len(names)} | ten dung o >=2 Dieu {sum(1 for v in by.values() if len(v)>=2)}")
print(f"ten co and/or {len(ao)} | span con dau phay/va/hoac {len(lst)}")
print(f"quy tac {len(R)} | isolated {iso} | vi tu than khong co quy tac nao sinh ra {len(dead)}/{len(bodyp)}")
