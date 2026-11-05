import json, sys
P = sys.argv[1]; d = json.load(open(P, encoding='utf-8'))
d['admin_target'] = {'adp': -370.0, 'adn': -291.0, 'source': "Finance BU review Act Sep'26 (9+3), slide 25: Target incl. cassava flour line, TDC 2.0 pre-op reclass and cost savings"}
json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
a = d['admin']['AP26']
print('AP26 admin P', {k: round(x, 1) for k, x in a['adp'].items()}, 'NonP', {k: round(x, 1) for k, x in a['adn'].items()})
for s in ['2025', 'LE26', 'AP27']:
    r = d['bupl'][s]; print(s, [(x['label'], None if x['vals'][0] is None else round(x['vals'][0], 3), None if x['vals'][-1] is None else round(x['vals'][-1], 3)) for x in r if x['label'] in ('% Vol growth', 'Total admin')])
