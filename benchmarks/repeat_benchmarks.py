import json,sys
sys.path.insert(0,'.')
from benchmarks.benchmark_matrix import bench_local,bench_loopback
variants=[('in_process_memory',lambda:bench_local('memory',2000,200),5.0),('in_process_sqlite',lambda:bench_local('sqlite',1500,150),10.0),('loopback_http_sidecar',lambda:bench_loopback(750,75),20.0)]
out={'repetitions':3,'variants':{}}
for name,fn,target in variants:
    runs=[]
    for i in range(3):
        st=fn();runs.append(st);print(name,i+1,st)
    p95s=[x['p95_ms'] for x in runs]
    out['variants'][name]={'target_p95_ms':target,'runs':runs,'p95_min_ms':min(p95s),'p95_max_ms':max(p95s),'all_runs_pass_target':all(x<=target for x in p95s)}
json.dump(out,open('benchmark_repeated_results.json','w'),indent=2)
