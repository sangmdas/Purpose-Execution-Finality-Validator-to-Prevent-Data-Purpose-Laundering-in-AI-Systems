from __future__ import annotations
import json, os, statistics, sys, tempfile, threading, time, urllib.request
from dataclasses import asdict, replace
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
sys.path.insert(0,'src')
from purpose_finality import *

def pct(xs,p):
    s=sorted(xs); return s[min(len(s)-1,max(0,int((len(s)-1)*p)))]
def stats(xs):
    return {k:round(v,4) for k,v in {
        'p50_ms':pct(xs,.50),'p95_ms':pct(xs,.95),'p99_ms':pct(xs,.99),'mean_ms':statistics.mean(xs),'min_ms':min(xs),'max_ms':max(xs)}.items()}

def fresh(i,base,rec,ctx):
    a=replace(base,act_id=f'act-{i}',nonce=f'nonce-{i}',created_ms=ctx.now_ms,expires_ms=ctx.now_ms+10_000)
    return a,rec,ctx

def one_local(s,a,r,c):
    d=s.ped.validate(a,r,c)
    if not d.allowed: raise RuntimeError(d.reason)
    p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1')
    out=s.sink.verify_and_effect(a,d.handle,p,c)
    if out!='EFFECTUATED': raise RuntimeError(out)

def bench_local(replay,n,warmup):
    path=None
    if replay=='sqlite':
        fd,path=tempfile.mkstemp(prefix='ef-bench-',suffix='.db');os.close(fd);s=PurposeSystem(path)
    else:s=PurposeSystem()
    base,r,c=baseline()
    for i in range(warmup): one_local(s,*fresh(-i-1,base,r,c))
    xs=[]
    for i in range(n):
        a,rr,cc=fresh(i,base,r,c); t=time.perf_counter_ns(); one_local(s,a,rr,cc); xs.append((time.perf_counter_ns()-t)/1e6)
    if path:
        s.replay.conn.close(); os.unlink(path)
        wal=path+'-wal'; shm=path+'-shm'
        for x in (wal,shm):
            if os.path.exists(x): os.unlink(x)
    return stats(xs)

class Handler(BaseHTTPRequestHandler):
    system=PurposeSystem()
    def log_message(self,*args): pass
    def do_POST(self):
        n=int(self.headers.get('content-length','0')); payload=json.loads(self.rfile.read(n))
        ad=payload['act']; ad['source_lineage']=tuple(ad.get('source_lineage',[])); a=CandidateAct(**ad); r=BindingRecord(**payload['record']); c=ValidationContext(**payload['context'])
        try: one_local(self.system,a,r,c); out={'result':'EFFECTUATED'}; code=200
        except Exception as e: out={'result':'DENY','reason':str(e)}; code=403
        raw=json.dumps(out,separators=(',',':')).encode(); self.send_response(code);self.send_header('content-type','application/json');self.send_header('content-length',str(len(raw)));self.end_headers();self.wfile.write(raw)

def bench_loopback(n,warmup):
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler); th=threading.Thread(target=server.serve_forever,daemon=True);th.start();url=f'http://127.0.0.1:{server.server_port}/finality'
    base,r,c=baseline()
    def req(i):
        a,rr,cc=fresh(i,base,r,c); body=json.dumps({'act':asdict(a),'record':asdict(rr),'context':asdict(cc)},separators=(',',':')).encode(); request=urllib.request.Request(url,data=body,headers={'content-type':'application/json'},method='POST');
        with urllib.request.urlopen(request,timeout=5) as resp:
            if json.loads(resp.read())['result']!='EFFECTUATED':raise RuntimeError('deny')
    for i in range(warmup):req(-i-1)
    xs=[]
    for i in range(n): t=time.perf_counter_ns();req(i);xs.append((time.perf_counter_ns()-t)/1e6)
    server.shutdown();server.server_close();return stats(xs)

def main():
    cfg=[('in_process_memory',int(os.getenv('EF_BENCH_MEMORY_N','3000')),300,5.0),('in_process_sqlite',int(os.getenv('EF_BENCH_SQLITE_N','2000')),200,10.0),('loopback_http_sidecar',int(os.getenv('EF_BENCH_HTTP_N','1000')),100,20.0)]
    out={'clock':'time.perf_counter_ns','host_scope':'single Linux host; no external network/TEE/HSM','variants':{}}
    for name,n,w,target in cfg:
        st=bench_loopback(n,w) if name.startswith('loopback') else bench_local('sqlite' if 'sqlite' in name else 'memory',n,w)
        out['variants'][name]={'iterations':n,'warmup':w,'target_p95_ms':target,'measured':st,'target_pass':st['p95_ms']<=target};print(name,out['variants'][name])
    json.dump(out,open('benchmark_matrix_results.json','w'),indent=2)
if __name__=='__main__':main()
