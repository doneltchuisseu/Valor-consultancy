import json,re,html,os,shutil,unicodedata,zipfile
from PIL import Image
D=json.load(open('all.json'))
OUT='dist2'
shutil.rmtree(OUT,ignore_errors=True)
for p in ('services','actualites','formations','assets'): os.makedirs(f'{OUT}/{p}',exist_ok=True)
U08='/tmp/claude-0/-home-user-valor-consultancy/6ee59e1b-c5f9-5ea7-a436-f1f0bf258619/scratchpad/u0822'
REPO='/home/user/valor-consultancy'
SPAM=re.compile(r'craps|tafel|inzet|casoola|kasyno|spielen|gewinn|\btest\d*\b|casino|slot|bonus|\bbet|poker|pokie|jackpot|spin|gambl|roulette|blackjack|wager|payout|crypto|lottery|mostbet|1win|aviator',re.I)
def slugify(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:70] or 'page'
def fix_urls(s): return re.sub(r'https?://(?:www\.)?valorconsultancyafrica\.(?:com|org)/wp-content','/wp-content',s)
def body(s):
    s=re.sub(r'<(script|style|noscript)[^>]*>.*?</\1>','',s,flags=re.S|re.I)
    s=re.sub(r'<!--.*?-->','',s,flags=re.S); s=re.sub(r'\[/?[a-zA-Z_][^\]]*\]','',s)
    s=re.sub(r'\son\w+="[^"]*"','',s); s=re.sub(r'javascript:','',s,flags=re.I); s=fix_pool(fix_urls(s))
    s=re.sub(r'<img\b[^>]*src=["\']/wp-content/uploads/(?!pool/)[^>]*>','',s)
    s=re.sub(r'(?:<[^>]+>\s*)*Vous voulez en savoir plus sur nous\s*\?.*?T[ée]l[ée]charger(?:\s*<[^>]+>)*','',s,flags=re.S)
    return re.sub(r'\n{2,}','</p><p>',s.strip()) if '<p' not in s else s
def text(s,n=0):
    s=re.sub(r'<(script|style)[^>]*>.*?</\1>','',s,flags=re.S); s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    s=re.sub(r'<[^>]+>',' ',s); s=re.sub(r'\[[^\]]*\]',' ',s); s=re.sub(r'\s+',' ',html.unescape(s)).strip()
    return s[:n].rsplit(' ',1)[0]+'…' if n and len(s)>n else s
def esc(s): return html.escape(s,quote=True)
MONTHS=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
def fdate(d): y,m,dd=d[:10].split('-'); return f'{int(dd)} {MONTHS[int(m)-1]} {y}'
def write(p,s): open(f'{OUT}/{p}','w',encoding='utf-8').write(s)

# ---------- images (pool)
U='/root/.claude/uploads/6ee59e1b-c5f9-5ea7-a436-f1f0bf258619'
import glob
POOLDIR=f'{OUT}/wp-content/uploads/pool'; os.makedirs(POOLDIR,exist_ok=True)
AVAIL={}
def addimg(name,data=None,src=None):
    if name in AVAIL or name.endswith('/'): return
    out=f'{POOLDIR}/{name}'
    if src is None:
        open(out,'wb').write(data); src=out
    else: shutil.copy(src,out)
    if name.lower().endswith(('.jpg','.jpeg')) and os.path.getsize(out)>350000:
        try:
            im=Image.open(out); im.thumbnail((1600,1600)); im.convert('RGB').save(out,quality=82,optimize=True)
        except Exception: pass
    AVAIL[name]=1
for f in sorted(os.listdir(U08)):
    if os.path.isfile(f'{U08}/{f}') and f.lower().endswith(('.jpg','.jpeg','.png','.webp','.gif')): addimg(f,src=f'{U08}/{f}')
for zp in [f'{REPO}/202309.zip']+sorted(glob.glob(f'{U}/*Fichier_v.zip')+glob.glob(f'{U}/*-20[0-9][0-9]_[0-9][0-9].zip')):
    z=zipfile.ZipFile(zp)
    for n in z.namelist():
        if n.lower().endswith(('.jpg','.jpeg','.png','.webp','.gif')) and not n.startswith('__'): addimg(os.path.basename(n),data=z.read(n))
addimg('Marie-Victoire-1-250x285.jpg.webp',src=f'{REPO}/Marie-Victoire-1-250x285.jpg.webp')
if os.path.exists(f'{REPO}/docs/CNAME'): shutil.copy(f'{REPO}/docs/CNAME',f'{OUT}/CNAME')
open(f'{OUT}/.nojekyll','w').close()
def P(*names):
    for n in names:
        if n in AVAIL: return f'/wp-content/uploads/pool/{n}'
    return None
def _key(b):
    b=re.sub(r'\.webp$','',b,flags=re.I)
    b=re.sub(r'-(?:\d+x\d+|scaled|\d+x0|\d+x\d+@\dx)(?=\.[A-Za-z0-9]+$)','',b)
    b=re.sub(r'-1(?=\.[A-Za-z0-9]+$)','',b)
    return b.lower()
KEYIDX={}
for _n in AVAIL:
    _m=re.search(r'-(\d+)x(\d+)',_n); _sz=int(_m.group(1))*int(_m.group(2)) if _m else 10**9
    _k=_key(_n)
    if _k not in KEYIDX or _sz>KEYIDX[_k][0]: KEYIDX[_k]=(_sz,_n)
def resolve(base):
    if base in AVAIL: return base
    k=_key(base)
    return KEYIDX[k][1] if k in KEYIDX else None
def fix_pool(s):
    def r(m):
        base=os.path.basename(m.group(1)); hit=resolve(base)
        return '/wp-content/uploads/pool/'+hit if hit else m.group(0)
    return re.sub(r'/wp-content/uploads/((?:[^"\'\s)<>]+/)*[^"\'\s)<>/]+)',r,s)
UP='/wp-content/uploads/'
LOGO=P('logo-design-colors-01-768x295.png')
MV=P('Marie-Victoire-1-250x285.jpg.webp')
SVCIMG={'LEADERSHIP':P('IMG-20220826-WA0053.jpg','IMG-20220826-WA0053.jpg.webp'),'AUDIT EXTERNE':P('diagramme-ishikawa.png.webp'),'CONSEIL  CARRIÈRE':P('istockphoto-1256446514-612x612-1.jpg.webp'),'CONDUITE DU CHANGEMENT':P('istockphoto-600418448-612x612-1.jpg.webp'),'DÉVELOPPEMENT LOCAL':P('Triangle-du-Dossier-Technique-Commun-CTD-Le-CTD-est-organise-en-5-modules-Le-module-600x352.jpg','Triangle-du-Dossier-Technique-Commun-CTD-Le-CTD-est-organise-en-5-modules-Le-module-600x348.jpg'),'COACHING':P('femme-noire-fatiguee-frustree-travaillant-ordinateur-portable-ligne-reflechissant-trop-au-bureau_183219-9039-768x512.jpg.webp'),'FORMATIONS':P('IMG-20220826-WA0056-1024x1024.jpg')}

# ---------- data
pages={p['slug']:p for p in D if p['type']=='page' and p['status']=='publish'}
services=sorted([p for p in D if p['type']=='service' and p['status']=='publish'],key=lambda x:x['id'])
posts=[p for p in D if p['type']=='post' and p['status']=='publish' and not SPAM.search(p['title']) and not SPAM.search(p['content'][:800])]
posts.sort(key=lambda x:x['date'],reverse=True)
courses=[c for c in D if c['type']=='courses' and c['status']=='publish']
def svc_title(s):
    t=text(s['title']).title()
    for w in (' Du ',' De ',' Des ',' La '): t=t.replace(w,w.lower())
    return t.replace('Ctd','CTD').replace('  ',' ')
for p in posts:
    if not text(p['title']): p['title']='Sans titre'
    p['url']=f"actualites/{p['id']}-{slugify(p['title'])}.html"
for s in services: s['url']=f"services/{slugify(s['title'])}.html"; s['img']=SVCIMG.get(s['title'])

# ---------- layout
ICO={'pin':'<svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.500a2.500 2.500 0 0 1 0 5z"/></svg>',
'tel':'<svg viewBox="0 0 24 24"><path d="M6.600 10.800a15 15 0 0 0 6.600 6.600l2.200-2.200a1 1 0 0 1 1-.25 11 11 0 0 0 3.400.55 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.500a1 1 0 0 1 1 1c0 1.200.2 2.300.55 3.400a1 1 0 0 1-.25 1z"/></svg>',
'mail':'<svg viewBox="0 0 24 24"><path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm9 7.500L4.500 7v1.500L12 14l7.500-5.500V7z"/></svg>',
'in':'<svg viewBox="0 0 24 24"><path d="M4.500 8.500h3v11h-3zM6 3.500a1.800 1.800 0 1 1 0 3.600 1.800 1.800 0 0 1 0-3.600zM10 8.500h2.900v1.500c.5-.9 1.700-1.800 3.400-1.800 3.400 0 4 2.200 4 5.100v6.200h-3v-5.500c0-1.300 0-3-1.800-3s-2.100 1.400-2.100 2.900v5.600h-3z"/></svg>',
'wa':'<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 0 0-8.600 15L2 22l5.200-1.400A10 10 0 1 0 12 2zm5.300 14.200c-.2.600-1.300 1.200-1.800 1.200-.5.100-1 .2-3.300-.7-2.800-1.100-4.500-4-4.700-4.200-.1-.2-1.100-1.500-1.100-2.800 0-1.300.7-2 .9-2.200.2-.3.5-.3.700-.3h.5c.2 0 .4 0 .6.500l.8 2c.1.200.1.400 0 .5l-.4.600c-.1.200-.3.300-.1.600.2.300.8 1.300 1.700 2.100 1.200 1 2.100 1.300 2.400 1.500.3.100.4.100.6-.1l.8-1c.2-.3.400-.2.600-.1l1.900.9c.3.100.4.200.5.300.1.200.1.800-.1 1.300z"/></svg>',
'arrow':'<svg viewBox="0 0 24 24"><path d="M12 5l7 7-1.400 1.400L13 8.800V20h-2V8.800l-4.600 4.600L5 12z"/></svg>'}
NAVL=[('index.html','Accueil'),('a-propos.html','À propos'),('services.html','Services'),('formations.html','Formations'),('actualites.html','Actualités'),('agenda.html','Agenda'),('nous-rejoindre.html','Nous rejoindre')]
def page(title,desc,content,active='',depth=0,head=None,extra=''):
    r='../'*depth
    sub=''.join(f'<a href="{r}{s["url"]}">{esc(svc_title(s))}</a>' for s in services)
    nav=''
    for h,l in NAVL:
        cls=' class="on"' if h==active else ''
        if h=='services.html': nav+=f'<div class="dd"><a href="{r}{h}"{cls}>{l} <i>▾</i></a><div class="ddm">{sub}</div></div>'
        else: nav+=f'<a href="{r}{h}"{cls}>{l}</a>'
    ph=f'<section class="pagehead"><div class="wrap"><h1>{esc(head)}</h1><p><a href="{r}index.html">Accueil</a> · {esc(head)}</p></div></section>' if head else ''
    svcl=''.join(f'<a href="{r}{s["url"]}">{esc(text(s["title"]).upper())}</a>' for s in services)
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} – Valor Consultancy Africa</title><meta name="description" content="{esc(desc)}">
<link rel="icon" href="{P('favicon_vca.png')}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/style.css"></head><body>
<div class="top"><div class="wrap topin"><a class="brand" href="{r}index.html"><img src="{LOGO}" alt="Cabinet VCA" onerror="this.replaceWith(Object.assign(document.createElement('b'),{{textContent:'CABINET VCA'}}))"></a>
<div class="ti"><span class="ic">{ICO['tel']}</span><div><b>Contacts :</b>WhatsApp : (+237) 672 950 994 | 671 005 489<br>Tél : (+237) 697 899 089 | (+33) 664 741 260</div></div>
<div class="ti"><span class="ic">{ICO['mail']}</span><div><b>E-mail :</b><a href="mailto:info@valorconsultancyafrica.com">info@valorconsultancyafrica.com</a></div></div>
<div class="ti"><span class="ic">{ICO['pin']}</span><div><b>Localisation</b>Yaoundé - Paris - Fort de France</div></div></div></div>
<div class="navwrap"><header class="navbar"><button class="burger" aria-label="Menu" onclick="document.body.classList.toggle('open')">☰</button><nav>{nav}</nav><a class="btn" href="{r}contact.html">Contact</a></header></div>
<aside class="float"><a href="mailto:info@valorconsultancyafrica.com" title="E-mail" style="background:#1fd16e">{ICO['mail']}</a><a href="https://www.linkedin.com/in/valor-consultancy-africa-492721244" target="_blank" rel="noopener" title="LinkedIn" style="background:#2f6fb6">{ICO['in']}</a><a href="https://wa.me/237672950994" target="_blank" rel="noopener" title="WhatsApp" style="background:#25d366">{ICO['wa']}</a></aside>
<a class="totop" href="#" aria-label="Haut de page" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false">{ICO['arrow']}</a>
<main>{ph}{content}</main>
<section class="brochure"><div class="wrap brin"><div><h3>Vous voulez en savoir plus sur nous ?</h3><p>Demandez notre brochure pour plus de détails sur notre travail</p></div><a class="btn" href="mailto:info@valorconsultancyafrica.com?subject=Demande de brochure">Demander la brochure</a></div></section>
<footer><div class="wrap fgrid"><div><img class="flogo" src="{LOGO}" alt="Cabinet VCA" onerror="this.style.display='none'"><h4 class="ghr">JOURS OUVRABLES</h4>
<p class="fi"><span class="ic">{ICO['pin']}</span>Yaoundé</p><p class="fi"><span class="ic">{ICO['tel']}</span>(+33) 664 741 260 / (+237) 691729371</p><p class="fi"><span class="ic">{ICO['mail']}</span>info@valorconsultancyafrica.com</p>
<p>Lundi – Jeudi : 08h00 – 17h00,<br>Vendredi : 08h00 – 16h00,<br>Sur rendez-vous.</p></div>
<div><h4>Services</h4><div class="flinks">{svcl}</div></div>
<div><h4>Newsletter</h4><form class="nl" onsubmit="location.href='mailto:info@valorconsultancyafrica.com?subject=Newsletter&body=Merci d\\'inscrire cette adresse : '+encodeURIComponent(this.m.value);return false"><input name="m" type="email" placeholder="Adresse e-mail" required><button aria-label="Envoyer">→</button></form>
<div class="soc"><a href="https://www.linkedin.com/in/valor-consultancy-africa-492721244" target="_blank" rel="noopener" aria-label="LinkedIn">{ICO['in']}</a><a href="https://wa.me/237672950994" target="_blank" rel="noopener" aria-label="WhatsApp">{ICO['wa']}</a></div></div></div>
<div class="copy">© 2026 Valor Consultancy Africa. Tous droits réservés.</div></footer>{extra}</body></html>'''

# ---------- accueil
def eyebrow(t,center=False): return f'<p class="eyebrow{" c" if center else ""}">{esc(t)}</p>'
svc_cards=''.join(f'<a class="sc" href="{s["url"]}"><div class="scimg">{"<img src=%s alt=\"\" loading=lazy onerror=\"this.parentNode.classList.add(&#39;noimg&#39;)\">"%s["img"] if s["img"] else ""}</div><h3>{esc(text(s["title"]).upper())}</h3><p>{esc(re.sub("^"+re.escape(text(s["title"])),"",text(s["content"],200),flags=re.I).strip()[:110])}…</p></a>' for s in services)
crs=''.join(f'<div class="cc"><h3>{esc(text(c["title"]))}</h3><p>{esc(text(c.get("excerpt",""),90))}</p><a class="plus" href="formations.html" aria-label="Voir">+</a></div>' for c in courses[:6])
team=[('Marie-Victoire VÉNUS-PLOTON','Présidente Fondatrice de VCA',MV),('Didier Boris ANOKALI LANGOLO','Consultant Junior',P('ANOKALI-300x300.jpg')),('Daniel VALIYA','Consultant Junior',P('DANIEL-394x450.jpg'))]
teamh=''.join(f'<div class="tm"><div class="tmimg"><img src="{i}" alt="{esc(n)}" loading="lazy"></div><div class="tmb"><div><b>{esc(n)}</b><span>{esc(p)}</span></div><a class="sq" href="marie-victoire-venus-ploton.html">+</a></div></div>' if 'Marie' in n else f'<div class="tm"><div class="tmimg"><img src="{i}" alt="{esc(n)}" loading="lazy"></div><div class="tmb"><div><b>{esc(n)}</b><span>{esc(p)}</span></div><i class="sq">+</i></div></div>' for n,p,i in team)
news=''.join(f'<a class="nw" href="{p["url"]}"><small>{fdate(p["date"])}</small><b>{esc(text(p["title"]))}</b><span>En savoir plus →</span></a>' for p in posts[:6])
logos=[P('uniceflogo.png'),P('logo-union-europeenne.jpg'),P('Union-Africaine.jpg.webp'),P('images.png'),P('logo_worldbank.jpg'),P('BAD-BON.jpg'),P('logo-4-4.png'),P('292343945_2152012041646901_885691130664562673_n.jpg'),P('IMG_5498.jpeg','IMG_5498-300x300.jpeg'),P('log.jpeg','log-600x585.jpeg'),P('300627615_362814642726030_7749023314184009791_n.jpg')]
logoh=''.join(f'<img src="{l}" alt="" loading="lazy" onerror="this.remove()">' for l in logos if l)
partners=['FINANCIA','ARRDEL-BEE','CEAAC','CEMAC','MINEPAT','Union européenne','Union africaine','MINDDEVEL','Hôtel Hilton','Fecafoot','Sefacil','Groupe Advans','ONU Femmes','CNAM','Sciences Po Paris','Sciences Po Lyon','EHESP','ZLECAf','Grand Port de Fort-de-France','PAK','AFD','PAD','Go Business Africa','Ethiopian Airlines']
chips=''.join(f'<span>{esc(x)}</span>' for x in partners)+'<a class="chip" href="et-aussi.html">Voir tous →</a>'
CONTACT=f'''<section class="ct"><div class="wrap ctgrid"><div class="ctl">{eyebrow('Contactez - nous')}<h2>Pour plus d’informations</h2>
<div class="ci"><b>Nous trouver</b>Yaoundé - Paris - Fort de France</div><div class="ci"><b>Nous appeler</b>(+33) 664 741 260 | (+237) 691729371</div><div class="ci"><b>Nous écrire</b><a href="mailto:info@valorconsultancyafrica.com">info@valorconsultancyafrica.com</a></div>
<div class="ci"><b>Nous suivre</b><a href="https://www.linkedin.com/in/valor-consultancy-africa-492721244" target="_blank" rel="noopener">VALOR CONSULTANCY AFRICA</a></div></div>
<form class="cf" onsubmit="location.href='mailto:info@valorconsultancyafrica.com?subject='+encodeURIComponent('Message de '+this.n.value)+'&body='+encodeURIComponent(this.m.value+'\\n\\n'+this.e.value);return false"><input name="n" placeholder="Votre nom" required><input name="e" type="email" placeholder="Votre e-mail" required><textarea name="m" rows="4" placeholder="Votre message" required></textarea><button class="btn" type="submit">Envoyer maintenant</button></form></div></section>'''
HERO=P('IMG-20241021-WA0035.jpg','qui-somme-nous-250x285.jpg.webp','qui-somme-nous.jpg') or MV
home=f'''<section class="hero"><div class="wrap herogrid"><div class="ht">{eyebrow('Qui sommes - nous?')}
<h1>Un cabinet de conseil fondé et dirigé par «une femme leader et d’impact en Afrique 2022, Ambassadrice de solutions pour l’Afrique 2023 &amp; 2024, grand prix de l’engagement pour l’Afrique »</h1>
<p class="lead">Le Cabinet Valor Consultancy Africa (VCA) est spécialisé dans le Conseil et l’Ingénierie en Organisation. Le cabinet VCA intervient en France, sur le continent africain, en liaison avec des partenaires internationaux pour élaborer avec vous et pour vous, <b>une stratégie</b> et obtenir <b>des résultats</b> adaptés.</p>
<p class="sig"><b>MARIE-VICTOIRE VÉNUS-PLOTON</b><span>Présidente Fondatrice de Valor Consultancy Africa</span></p></div>
<div class="hv"><div class="hvimg"><img src="{HERO}" alt="Distinction" onerror="this.onerror=null;this.src='{MV}'"></div></div></div></section>
<section class="sec"><div class="wrap">{eyebrow('Nos services',True)}<h2 class="c">Notre offre de services</h2><div class="scg">{svc_cards}</div></div></section>
<section class="sec alt"><div class="wrap">{eyebrow('Nos formations',True)}<h2 class="c">Notre offre de formations</h2><div class="ccg">{crs}</div><p class="c"><a class="btn ghost" href="formations.html">Toutes nos formations</a></p></div></section>
<section class="band"><div class="bandin"><p class="eyebrow w c">Valor Consultancy Africa</p><h2>Femme leader et d’impact en Afrique</h2><a class="play" href="https://www.youtube.com/watch?v=SF4aHwxHtZ0" target="_blank" rel="noopener" aria-label="Voir la vidéo"><i></i></a></div></section>
<section class="sec"><div class="wrap">{eyebrow('Equipe VCA',True)}<h2 class="c">Notre équipe</h2><p class="c mut">Des personnes compétentes, dynamiques et prêtes à vous accompagner.</p><div class="tmg">{teamh}</div></div></section>
<section class="sec alt"><div class="wrap">{eyebrow('Actualités',True)}<h2 class="c">Veille documentaire</h2><p class="c mut">Suivez nos dernières nouvelles et réflexions.</p><div class="nwg">{news}</div><p class="c"><a class="btn" href="actualites.html">Toutes les actualités</a></p></div></section>
<section class="sec"><div class="wrap">{eyebrow('Et aussi',True)}<h2 class="c">Et aussi...</h2><div class="logos">{logoh}</div><div class="chips">{chips}</div></div></section>
{CONTACT}'''
write('index.html',page('Accueil','Cabinet de conseil et d’ingénierie en organisation : France, Afrique, Antilles.',home,'index.html'))

# ---------- pages intérieures
def inner(slug,head,desc,cont,active,depth=0,out=None):
    c=f'<section class="sec"><div class="wrap narrow prose">{cont}</div></section>'
    write(out or slug,page(head,desc,c,active,depth,head))
import urllib.parse
ELE=json.load(open('elementor.json'))
def gal(pid):
    acc=[]
    def f(n):
        if isinstance(n,dict):
            for k,v in n.items():
                if k=='wp_gallery' and isinstance(v,list): acc.extend(v)
                else: f(v)
        elif isinstance(n,list):
            for x in n: f(x)
    f(json.loads(ELE[pid])); return acc
ATT={a['id']:a['guid'].split('uploads/')[-1] for a in D if a['type']=='attachment'}
def gal_imgs(pid):
    out=[]
    for g in gal(pid):
        if not isinstance(g,dict): continue
        u=(g.get('url') or ATT.get(str(g.get('id')),'')).split('uploads/')[-1]
        b=os.path.basename(u); stem=re.sub(r'-scaled(?=\.)','',b)
        h=resolve(b); p=('/wp-content/uploads/pool/'+h) if h else None
        if p: out.append(p)
    return out
ag=gal_imgs('3491')
agal=''.join(f'<a href="{i}" target="_blank" rel="noopener"><img src="{i}" alt="" loading="lazy"></a>' for i in ag)
inner('a-propos.html','À propos','Qui est Valor Consultancy Africa.',body(pages['a-propos']['content'])+(f'<div class="gal">{agal}</div>' if agal else '')+'<p><a class="btn" href="marie-victoire-venus-ploton.html">Découvrir la fondatrice</a> <a class="btn ghost" href="contact.html">Nous contacter</a></p>','a-propos.html')
# Marie-Victoire
MVP=P('IMG_20220424_214803-1536x2048.jpg','IMG_20220424_214803-scaled.jpg') or MV
bio="Consultante internationale : Conseil et Ingénierie en Organisation · Mastère Spécialisé Conseil et Ingénierie en Organisation (Label CGE), Conservatoire National des Arts et Métiers (CNAM Paris) · Ancienne élève de l’Institut des hautes études de l’éducation et de la formation (IH2EF) · Formation de coach : Neuro Active Coaching · Ancienne élève de l’École des Hautes Études en Santé Publique (EHESP Rennes) · DEA-DESS Économie du Développement, Université Blaise Pascal (Clermont-Ferrand) · Diplômée de Sciences Po Lyon, section Éco-Fi · Langues : français, anglais, espagnol, créole."
mvc=f'''<div class="mvgrid"><div class="mvimg"><img src="{MVP}" alt="Marie-Victoire Vénus-Ploton" onerror="this.onerror=null;this.src=\'{MV}\'"></div><div><p class="eyebrow">Qui est Marie-Victoire Vénus-Ploton ?</p><h2>Marie-Victoire VÉNUS PLOTON</h2><p class="mvr">PDG de VCA</p><p>marievictoire.venusploton@gmail.com<br>(+237) 672 950 994 / (+33) 6674 741 260<br>Yaoundé, Cameroun</p><p><a class="btn" href="mailto:info@valorconsultancyafrica.com?subject=Prise de rendez-vous">Prendre rendez-vous</a></p>
<details open class="acc"><summary>Femme Leader et d’Impact pour l’Afrique</summary><p>{bio}</p></details></div></div>'''
write('marie-victoire-venus-ploton.html',page('Marie-Victoire Vénus-Ploton','Présidente fondatrice de Valor Consultancy Africa.',f'<section class="sec"><div class="wrap">{mvc}</div></section>','a-propos.html',0,'Marie-Victoire Vénus-Ploton'))
# Agenda
agi=gal_imgs('10790')
agh=''.join(f'<a href="{i}" target="_blank" rel="noopener"><img src="{i}" alt="" loading="lazy"></a>' for i in agi)
write('agenda.html',page('Agenda','Agenda et photos des événements.',f'<section class="sec"><div class="wrap">{eyebrow("Portfolio",True)}<h2 class="c">Agenda</h2>'+(f'<div class="gal">{agh}</div>' if agh else '<p class="c mut">Les photos de l’agenda seront bientôt disponibles.</p>')+'</div></section>','agenda.html',0,'Agenda'))
# Et aussi
def unwrap(u):
    u=html.unescape(u or '')
    m=re.search(r'[?&]url=([^&]+)',u)
    return urllib.parse.unquote(m.group(1)) if m else u
alist=[]
def f3(n):
    if isinstance(n,dict):
        for k,v in n.items():
            if k=='list' and isinstance(v,list): alist.extend(v)
            else: f3(v)
    elif isinstance(n,list):
        for x in n: f3(x)
f3(json.loads(ELE['10792']))
items=[]
for i in alist:
    if not isinstance(i,dict): continue
    nm=text(i.get('content','')); lk=unwrap((i.get('link') or {}).get('url') if isinstance(i.get('link'),dict) else '')
    if nm: items.append((nm,lk))
eah=''.join(f'<a class="chip" href="{esc(l)}" target="_blank" rel="noopener nofollow">{esc(n)}</a>' if l.startswith('http') else f'<span class="chip">{esc(n)}</span>' for n,l in items)
write('et-aussi.html',page('Et aussi...','Nos partenaires et références.',f'<section class="sec"><div class="wrap">{eyebrow("Sites",True)}<h2 class="c">Et aussi...</h2><div class="chips big">{eah}</div></div></section>','et-aussi.html',0,'Et aussi...'))
inner('nous-rejoindre.html','Nous rejoindre','Rejoindre l’équipe VCA.',body(pages['nous-aimons']['content'])+'<p><a class="btn" href="mailto:info@valorconsultancyafrica.com?subject=Candidature">Envoyer ma candidature</a></p>','nous-rejoindre.html')
write('contact.html',page('Contact','Contacter Valor Consultancy Africa.',CONTACT,'contact.html',0,'Contact'))
write('services.html',page('Services','Nos services de conseil.',f'<section class="sec"><div class="wrap">{eyebrow("Services",True)}<h2 class="c">Notre offre de services</h2><p class="c mut">Nous positionnons nos clients à l’avant-garde de leur domaine. Un interlocuteur unique vous est dédié tout au long de la mission. Un devis gratuit est proposé.</p><div class="scg">{svc_cards}</div></div></section>','services.html',0,'Services'))
for s in services:
    img=f'<img class="rimg" src="{s["img"]}" alt="" onerror="this.remove()">' if s['img'] else ''
    inner('',svc_title(s),text(s['content'],150),f'{img}{body(s["content"])}<p><a class="btn" href="../contact.html">Demander un devis gratuit</a></p>','services.html',1,s['url'])
cl=''.join(f'<div class="cc"><h3>{esc(text(c["title"]))}</h3><p>{esc(text(c.get("excerpt",""),160))}</p></div>' for c in courses)
write('formations.html',page('Formations','Nos formations.',f'<section class="sec"><div class="wrap">{eyebrow("Nos formations",True)}<h2 class="c">Notre offre de formations</h2><div class="ccg">{cl}</div><p class="c"><a class="btn" href="contact.html">Nous contacter pour une formation</a></p></div></section>','formations.html',0,'Formations'))
idx=[]
for p in posts:
    write(p['url'],page(text(p['title']),text(p['content'],150),f'<section class="sec"><div class="wrap narrow prose"><small>{fdate(p["date"])}</small><h2>{esc(text(p["title"]))}</h2>{body(p["content"])}</div></section>','actualites.html',1,'Actualités'))
    idx.append([text(p['title']),p['date'][:10],text(p['content'],150),p['url']])
js='<script>const A='+json.dumps(idx,ensure_ascii=False)+r'''
let n=0;const L=document.getElementById('list'),Q=document.getElementById('q'),M=document.getElementById('more'),C=document.getElementById('cnt');
const F=d=>new Date(d).toLocaleDateString('fr-FR',{day:'numeric',month:'long',year:'numeric'});
const esc=s=>s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function render(reset){const q=Q.value.trim().toLowerCase();const r=A.filter(a=>!q||(a[0]+' '+a[2]).toLowerCase().includes(q));if(reset){n=24;L.innerHTML=''}
const from=L.children.length;r.slice(from,n).forEach(a=>L.insertAdjacentHTML('beforeend',`<a class="nw" href="${a[3]}"><small>${F(a[1])}</small><b>${esc(a[0])}</b><p>${esc(a[2])}</p><span>En savoir plus →</span></a>`));
M.style.display=r.length>n?'inline-block':'none';C.textContent=r.length+' article'+(r.length>1?'s':'')}
Q.oninput=()=>render(true);M.onclick=()=>{n+=24;render()};render(true);</script>'''
write('actualites.html',page('Actualités','Actualités et veille.',f'<section class="sec"><div class="wrap"><div class="bar"><input id="q" type="search" placeholder="Rechercher un article…"><span id="cnt"></span></div><div class="nwg" id="list"></div><p class="c"><button class="btn" id="more">Voir plus</button></p></div></section>','actualites.html',0,'Actualités',js))

# ---------- CSS
write('assets/style.css','''
:root{--g:#0FB86F;--g2:#2de27a;--y:#f2b632;--red:#D92F2F;--ink:#101213;--mut:#5b6266;--bg:#fff;--alt:#f4f7f5;--line:#e4e8e6;--dark:#2f3133;--grad:linear-gradient(90deg,#2de27a,#f2b632)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font:16px/1.7 "Roboto",Arial,sans-serif;color:#222;background:#fff}
img{max-width:100%;height:auto}a{color:var(--g)}h1,h2,h3,h4{font-family:"Roboto Condensed","Arial Narrow",Arial,sans-serif;color:var(--ink);line-height:1.15;margin:0 0 .6em}
h1{font-size:clamp(28px,3.6vw,44px);font-weight:700}h2{font-size:clamp(26px,3vw,38px);font-weight:700}h3{font-size:22px}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}.narrow{max-width:820px}.c{text-align:center}.mut{color:var(--mut)}
.top{background:var(--dark);color:#fff;font-size:14px;padding-bottom:42px}.topin{display:flex;gap:36px;align-items:center;padding-top:22px;padding-bottom:6px;flex-wrap:wrap}
.brand img{height:70px;display:block;background:#fff;border-radius:10px;padding:4px 10px}.brand b{color:var(--g)}
.ti{display:flex;gap:12px;align-items:flex-start;line-height:1.5}.ti b{display:block;color:#fff}.ti a{color:#fff;text-decoration:none}.ic{width:22px;height:22px;flex:none;border:1.500px solid var(--g);border-radius:4px;display:grid;place-items:center;margin-top:3px}.ic svg{width:13px;height:13px;fill:var(--g)}
.navwrap{max-width:1180px;margin:-34px auto 0;padding:0 24px;position:sticky;top:8px;z-index:30}
.navbar{background:#fff;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.14);display:flex;align-items:center;justify-content:space-between;padding:10px 14px 10px 28px;min-height:64px}
nav{display:flex;gap:6px;align-items:center;flex-wrap:wrap}nav>a,.dd>a{padding:10px 14px;color:#222;text-decoration:none;font-weight:500}nav a:hover,nav a.on{color:var(--g)}.dd{position:relative}.dd i{font-style:normal;font-size:11px}
.ddm{display:none;position:absolute;top:100%;left:0;background:#fff;min-width:260px;border-radius:10px;box-shadow:0 12px 30px rgba(0,0,0,.15);padding:8px 0}.dd:hover .ddm{display:block}.ddm a{display:block;padding:8px 18px;color:#222;text-decoration:none;font-size:15px}.ddm a:hover{background:var(--alt);color:var(--g)}
.btn{display:inline-block;background:var(--grad);color:#fff;padding:12px 30px;border-radius:30px;text-decoration:none;font-weight:700;border:0;font-size:16px;cursor:pointer;transition:.2s;font-family:Roboto,sans-serif}.btn:hover{filter:brightness(.93);transform:translateY(-1px)}.btn.ghost{background:transparent;color:var(--g);border:2px solid var(--g)}
.burger{display:none;background:none;border:0;font-size:26px;cursor:pointer}
.eyebrow{display:flex;align-items:center;gap:12px;color:#595959;font:400 16px "Roboto Condensed",sans-serif;margin:0 0 12px}.eyebrow:before{content:"";width:34px;height:3px;background:var(--grad);border-radius:2px}.eyebrow.c{justify-content:center}.eyebrow.w{color:#fff}
.hero{padding:70px 0 60px}.herogrid{display:grid;grid-template-columns:1.1fr .9fr;gap:50px;align-items:center}.lead{text-align:justify;font-size:17px}.sig{margin:26px 0 0}.sig b{display:block;color:var(--g);font:700 18px "Roboto Condensed"}.sig span{color:var(--red)}
.hvimg{border-radius:4px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.18);background:#222;max-width:420px;margin-left:auto}.hvimg img{display:block;width:100%;max-height:560px;object-fit:cover}
.sec{padding:70px 0}.alt{background:var(--alt)}
.scg{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:34px 28px;margin-top:34px}.sc{display:block;text-decoration:none;color:#222;text-align:center}
.scimg{aspect-ratio:16/10;overflow:hidden;background:linear-gradient(135deg,#dff5e9,#f6efd8);margin-bottom:16px}.scimg img{width:100%;height:100%;object-fit:cover;display:block;transition:.35s}.sc:hover img{transform:scale(1.05)}.sc h3{color:var(--g);font-size:21px;margin:0 0 6px}.sc p{color:var(--mut);margin:0;font-size:15.500px;padding:0 10px}
.ccg{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:30px;margin:34px 0}.cc{padding:8px 4px}.cc h3{font-size:22px}.cc p{color:#555;font-size:15px}.plus{display:inline-grid;place-items:center;width:36px;height:36px;border-radius:50%;background:var(--g2);color:#fff;text-decoration:none;font-size:22px;line-height:1}
.band{position:relative;margin:30px auto;max-width:1180px;min-height:420px;background:#2a3f7a url(/wp-content/uploads/pool/group-of-young-people-sitting-on-conference-together.jpg) center/cover;clip-path:polygon(0 8%,100% 0,100% 92%,0 100%);display:grid;place-items:center;text-align:center;color:#fff}
.band:before{content:"";position:absolute;inset:0;background:rgba(36,52,110,.55)}.bandin{position:relative;padding:60px 20px}.band h2{color:#fff;font-size:clamp(28px,4vw,46px)}
.play{display:inline-grid;place-items:center;width:84px;height:84px;border-radius:50%;background:var(--grad);margin-top:14px;box-shadow:0 0 0 14px rgba(255,255,255,.18)}.play i{border-style:solid;border-width:12px 0 12px 20px;border-color:transparent transparent transparent #fff;margin-left:5px}
.tmg{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:30px;margin-top:34px}.tm{background:#fff}.tmimg{aspect-ratio:1/1.150;background:#e3e8e5;overflow:hidden}.tmimg img{width:100%;height:100%;object-fit:cover;display:block}.tmb{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;padding:14px 8px 4px}.tmb b{display:block;font:700 22px/1.2 "Roboto Condensed";color:var(--ink)}.tmb span{color:var(--mut);font-size:14.500px}.sq{flex:none;width:38px;height:38px;background:var(--g2);color:#fff;font-style:normal;display:grid;place-items:center;font-size:22px}
.nwg{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin:30px 0}.nw{display:block;background:#fff;border:1px solid var(--line);border-bottom:3px solid var(--g2);padding:20px;text-decoration:none;color:#222}.nw:hover{box-shadow:0 12px 28px rgba(0,0,0,.09)}.nw small{color:var(--mut)}.nw b{display:block;font:700 20px/1.25 "Roboto Condensed";margin:6px 0;color:var(--ink)}.nw p{margin:4px 0 8px;color:var(--mut);font-size:14.500px}.nw span{color:var(--g);font-weight:500;font-size:14.500px}
.logos{display:flex;flex-wrap:wrap;gap:30px;justify-content:center;align-items:center;margin:30px 0}.logos img{height:64px;width:auto;max-width:150px;object-fit:contain;filter:grayscale(.2)}
.chips{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:18px}.chips span{background:var(--alt);border:1px solid var(--line);padding:6px 16px;border-radius:99px;font-size:14.500px}
.ct{background:linear-gradient(rgba(18,24,22,.88),rgba(18,24,22,.88)),url(/wp-content/uploads/pool/african-american-man-wearing-headphones-reading-good-news-in-email-getting-new-job-promotion-using-laptop-300x200.jpg.webp) center/cover #1a211e;color:#fff;padding:70px 0}
.ctgrid{display:grid;grid-template-columns:1fr 1fr;gap:50px}.ct h2{color:#fff}.ct .eyebrow{color:#cfd6d3}.ci{margin:16px 0}.ci b{display:block;color:var(--g2);font-family:"Roboto Condensed";font-size:18px}.ci a{color:#fff}
.cf{display:grid;gap:14px;align-content:start}.cf input,.cf textarea{width:100%;padding:14px 16px;border:0;border-radius:6px;font:inherit;background:#fff}.cf button{justify-self:start}
.brochure{background:#eafaf1;padding:34px 0}.brin{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}.brin h3{margin:0}.brin p{margin:4px 0 0;color:#444}
footer{background:linear-gradient(rgba(25,28,28,.94),rgba(25,28,28,.94)),#1c1f1f;color:#e6ebe9;padding-top:56px;font-size:15px}.fgrid{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:40px}
.flogo{height:84px;background:#fff;border-radius:10px;padding:4px 10px;margin-bottom:14px}.fgrid h4{color:#fff;font-size:26px;border-bottom:1px solid #3a4040;padding-bottom:10px}.ghr{color:var(--g2)!important;font-size:17px!important;border:0!important;margin:10px 0}
.fi{display:flex;gap:10px;margin:6px 0}.flinks a{display:block;color:#fff;text-decoration:none;font:700 15px "Roboto Condensed";padding:4px 0;letter-spacing:.2px}.flinks a:hover{color:var(--g2)}
.nl{display:flex}.nl input{flex:1;padding:12px;border:0;background:#444;color:#fff}.nl button{background:var(--grad);color:#fff;border:0;width:46px;font-size:18px;cursor:pointer}.soc{display:flex;gap:14px;margin-top:16px}.soc a svg{width:24px;height:24px;fill:var(--g2)}
.copy{border-top:1px solid #343a3a;margin-top:40px;padding:22px;text-align:center;font-size:15px}
.float{position:fixed;right:14px;top:40%;z-index:40;display:flex;flex-direction:column;gap:8px}.float a{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;box-shadow:0 4px 12px rgba(0,0,0,.2)}.float svg{width:19px;height:19px;fill:#fff}
.totop{position:fixed;right:18px;bottom:22px;z-index:40;width:48px;height:48px;border-radius:50%;background:var(--grad);display:grid;place-items:center;box-shadow:0 6px 16px rgba(0,0,0,.25)}.totop svg{width:22px;height:22px;fill:#fff}
.pagehead{background:linear-gradient(rgba(30,34,34,.85),rgba(30,34,34,.85)),#2f3133;color:#fff;padding:60px 0 50px;text-align:center}.pagehead h1{color:#fff;margin:0}.pagehead p{margin:8px 0 0;color:#cfd6d3}.pagehead a{color:var(--g2);text-decoration:none}
.prose img{border-radius:6px;margin:12px 0}.prose h2,.prose h3{margin-top:1.4em}.prose iframe{max-width:100%}.rimg{width:100%;max-height:360px;object-fit:cover;margin-bottom:18px}
.bar{display:flex;gap:16px;align-items:center;margin:0 0 20px}.bar input{flex:1;max-width:460px;padding:12px 16px;border:1px solid var(--line);border-radius:30px;font:inherit}#cnt{color:var(--mut);font-size:14px}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin:26px 0}.gal a{display:block;aspect-ratio:4/3;overflow:hidden;background:#e3e8e5}.gal img{width:100%;height:100%;object-fit:cover;margin:0;border-radius:0;transition:.3s}.gal a:hover img{transform:scale(1.05)}
.mvgrid{display:grid;grid-template-columns:.8fr 1.2fr;gap:44px;align-items:start}.mvimg img{width:100%;display:block;box-shadow:0 20px 50px rgba(0,0,0,.18)}.mvr{color:var(--red);font-weight:500;margin:0 0 12px}
.acc{margin-top:22px;border:1px solid var(--line)}.acc summary{cursor:pointer;padding:14px 18px;font:700 20px "Roboto Condensed";background:var(--alt)}.acc p{padding:0 18px 14px}
.chip{display:inline-block;background:var(--alt);border:1px solid var(--line);padding:6px 16px;border-radius:99px;font-size:14.500px;text-decoration:none;color:#222}a.chip:hover{border-color:var(--g);color:var(--g)}.chips.big{gap:14px}.chips.big .chip{font-size:16px;padding:9px 20px}
@media(max-width:860px){.mvgrid{grid-template-columns:1fr}}
@media(max-width:860px){.herogrid,.ctgrid,.fgrid{grid-template-columns:1fr}.hvimg{margin:0 auto}.burger{display:block}nav{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;padding:10px 20px 16px;flex-direction:column;align-items:flex-start;box-shadow:0 12px 20px rgba(0,0,0,.08);border-radius:0 0 12px 12px}body.open nav{display:flex}.navbar{position:relative}.dd .ddm{position:static;display:block;box-shadow:none;padding-left:10px}.float{display:none}.sec{padding:46px 0}.band{clip-path:none}}
''')
print(len(posts),'articles',len(services),'services',len(courses),'formations')
