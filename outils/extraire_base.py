import re,json
t=open('../big/posts.txt',encoding='utf-8',errors='ignore').read()
def parse(s):
    n=len(s);rows=[];p=0
    def tok(p):
        while s[p] in ' \n\t': p+=1
        if s[p]=="'":
            q=p+1;buf=[]
            while True:
                c=s[q]
                if c=='\\':
                    d=s[q+1]; buf.append({'n':'\n','r':'\r','t':'\t','0':'\0'}.get(d,d)); q+=2
                elif c=="'":
                    if s[q+1]=="'": buf.append("'"); q+=2
                    else: break
                else: buf.append(c); q+=1
            return ''.join(buf),q+1
        m=re.match(r'-?\d+(\.\d+)?|NULL',s[p:]); return m.group(0),p+m.end()
    while p<n:
        while p<n and s[p] in ' \n,': p+=1
        if p>=n or s[p]==';': break
        p+=1;row=[]
        while True:
            v,p=tok(p);row.append(v)
            while s[p] in ' \n': p+=1
            if s[p]==',': p+=1; continue
            if s[p]==')': p+=1; break
        rows.append(row)
    return rows
rows=[]
for part in t.split('INSERT INTO `d18vnp3nj3_posts`')[1:]:
    rows+=parse(part[part.index('VALUES')+6:])
keep=[dict(id=r[0],author=r[1],parent=r[17],type=r[20],status=r[7],title=r[5],slug=r[11],date=r[2],content=r[4],excerpt=r[6],guid=r[18],mime=r[21]) for r in rows if r[20] in('page','service','post','courses','attachment') and r[7] in('publish','inherit')]
json.dump(keep,open('all.json','w'),ensure_ascii=False)
print(len(keep))
