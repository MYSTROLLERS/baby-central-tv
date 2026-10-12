#!/usr/bin/env python3
"""
Generate the Baby Central TV display index.html for GitHub Pages.
Auto-cycling JavaScript slideshow, no sign-in required.
Writes: ~/workspace/baby-central-babies/tv-site/index.html
"""
import json, os

WORKSPACE = os.path.expanduser("~/workspace/baby-central-babies")
HIDDEN = os.path.join(WORKSPACE, "hidden_files")
TV_SITE = os.path.join(WORKSPACE, "tv-site")
COUNT = 50  # births shown in the rotation

CRIB_URL = "https://cdn.shoplightspeed.com/shops/608968/files/77911785/img-7206.jpg"
BOTTLE_URL = "https://cdn.shoplightspeed.com/shops/608968/files/77911789/img-7207.jpg"

def main():
    with open(os.path.join(HIDDEN, "all_births.json")) as f:
        all_births = json.load(f)

    recent = all_births[:COUNT]
    boys = sum(1 for b in all_births if b['gender'] == 'Boy')
    girls = sum(1 for b in all_births if b['gender'] in ('Girl', 'Twin Girls'))

    # Build JS data array - use double quotes for JS strings, escape properly
    js_items = []
    for b in recent:
        names = b['names'].replace('\\', '\\\\').replace('"', '\\"').replace('&amp;', '&')
        date_str = ''
        if b['date']:
            y, m, d = b['date'].split('-')
            date_str = f"{int(m)}/{int(d)}/{y}"
        is_boy = b['gender'] == 'Boy'
        label = "It's a Boy!" if is_boy else ("Twin Girls!" if b['gender'] == 'Twin Girls' else "It's a Girl!")
        label = label.replace("'", "\\'")
        js_items.append(
            f'{{names:"{names}",label:"{label}",date:"{date_str}",boy:{str(is_boy).lower()}}}'
        )
    js_data = ",\n".join(js_items)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="86400">
<title>Baby Central Babies</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Arial,Helvetica,sans-serif;background:#fff;color:#333;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:25px 20px}}
.header{{display:flex;align-items:center;justify-content:center;gap:30px;margin-bottom:15px}}
.header img{{height:90px}}
.header h1{{color:#d63384;font-size:36px;text-align:center}}
.header p{{color:#666;font-size:16px;text-align:center;margin-top:6px}}
.counts{{font-size:22px;font-weight:bold;margin-bottom:20px}}
.counts .b{{color:#0d6efd}} .counts .g{{color:#d63384}}
#grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;width:min(1050px,95vw);transition:opacity .5s}}
.card{{border-radius:12px;padding:20px 12px;text-align:center;box-shadow:0 6px 20px rgba(0,0,0,.1);min-height:140px;display:flex;flex-direction:column;justify-content:center}}
.card.boy{{background:#e7f3ff;border:3px solid #0d6efd}}
.card.girl{{background:#fce4f0;border:3px solid #d63384}}
.card .names{{font-size:19px;font-weight:bold;margin-bottom:6px}}
.card .label{{font-size:16px;font-weight:bold}}
.card.boy .label{{color:#0d6efd}} .card.girl .label{{color:#d63384}}
.card .date{{color:#999;font-size:14px;margin-top:8px}}
#counter{{color:#aaa;font-size:14px;margin-top:20px}}
.footer{{color:#999;font-size:13px;margin-top:12px}}
</style>
</head>
<body>
<div class="header">
<img src="{CRIB_URL}" alt="Baby crib">
<div><h1>Baby Central Babies</h1><p>Celebrating the newest arrivals from our Baby Central family.<br>Mazel Tov to all the proud parents!</p></div>
<img src="{BOTTLE_URL}" alt="Baby bottle">
</div>
<div class="counts"><span class="b">&hearts; {boys} Boys</span> &nbsp;|&nbsp; <span class="g">&hearts; {girls} Girls</span></div>
<div id="grid"></div>
<div id="counter"></div>
<div class="footer">Showing the {len(recent)} most recent of {len(all_births)} total arrivals &bull; Updated daily</div>
<script>
var births=[{js_data}];
var PER_PAGE=9;
var page=0;
var pages=Math.ceil(births.length/PER_PAGE);
function show(){{
  var g=document.getElementById('grid');
  g.style.opacity=0;
  setTimeout(function(){{
    var html='';
    for(var k=0;k<PER_PAGE;k++){{
      var b=births[(page*PER_PAGE+k)%births.length];
      html+='<div class="card '+(b.boy?'boy':'girl')+'"><div class="names">'+b.names+'</div><div class="label">'+b.label+'</div><div class="date">'+b.date+'</div></div>';
    }}
    g.innerHTML=html;
    document.getElementById('counter').textContent='Page '+(page+1)+' of '+pages;
    g.style.opacity=1;
  }},400);
  page=(page+1)%pages;
}}
show();setInterval(show,10000);
</script>
</body>
</html>"""

    out = os.path.join(TV_SITE, "index.html")
    with open(out, 'w') as f:
        f.write(html)
    print(f"Generated TV index.html: {len(html)} chars, {len(recent)} births in rotation")

if __name__ == "__main__":
    main()
