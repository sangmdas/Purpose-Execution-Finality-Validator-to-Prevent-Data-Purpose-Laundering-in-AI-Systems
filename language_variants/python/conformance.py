import json,sys
sys.path.insert(0,'src')
from purpose_finality import CandidateAct, BindingRecord, ValidationContext, PurposeSystem, digest
root=json.load(open('vectors/conformance_vectors.json'))
fail=0
for case in root['cases']:
    a=dict(case['act']); a['source_lineage']=tuple(a.get('source_lineage',[])); a=CandidateAct(**a)
    r=BindingRecord(**case['record']) if case['record'] else None
    c=ValidationContext(**case['context'])
    s=PurposeSystem(); got=s.ped.validate(a,r,c).reason
    if got!=case['expected'] or digest(a)!=case['act_digest']:
        print('FAIL',case['name'],got,case['expected'],digest(a)==case['act_digest']); fail+=1
print(f"Python conformance: {len(root['cases'])-fail}/{len(root['cases'])} passed")
raise SystemExit(1 if fail else 0)
