import random,string,sys
from dataclasses import replace
sys.path.insert(0,'src')
from purpose_finality import *
rng=random.Random(20260909)
# 1,000 post-issuance load-bearing mutations.
s=PurposeSystem();a,r,c=baseline();d=s.ped.validate(a,r,c);p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1')
fields=['requester_id','workload_id','object_id','workflow_id','operation','destination_id','nonce','policy_version']
mutation_pass=0
for i in range(1000):
    f=rng.choice(fields);v=(38+rng.randint(1,1000)) if f=='policy_version' else f'mut-{i}-{rng.randrange(10**9)}';bad=replace(a,**{f:v});out=s.sink.verify_and_effect(bad,d.handle,p,c);mutation_pass += out!='EFFECTUATED'
# 500 purpose-relabel attacks with unauthorized operation/destination/requester.
relabel_pass=0
for i in range(500):
    ps=PurposeSystem();aa,rr,cc=baseline();label=''.join(rng.choice(string.ascii_letters) for _ in range(rng.randint(0,40)));attack=replace(aa,act_id=f'relabel-{i}',nonce=f'r-{i}',requester_id='advertising-service',workload_id='ad-workload',operation='infer household income',destination_id='advertising-profile-database',declared_purpose=label);cc=replace(cc,authenticated_requester='advertising-service',authenticated_workload='ad-workload');de=ps.ped.validate(attack,rr,cc);relabel_pass += not de.allowed
# 500 wrong-holder PoP attempts.
pop_pass=0
for i in range(500):
    ps=PurposeSystem();aa,rr,cc=baseline();aa=replace(aa,act_id=f'pop-{i}',nonce=f'p-{i}');de=ps.ped.validate(aa,rr,cc);proof=ps.sink.make_proof(de.handle,ps.sink.challenge(),'holder-2');out=ps.sink.verify_and_effect(aa,de.handle,proof,cc);pop_pass += out!='EFFECTUATED'
print({'seed':20260909,'post_issue_mutations':f'{mutation_pass}/1000 denied','purpose_relabels':f'{relabel_pass}/500 denied','wrong_pop':f'{pop_pass}/500 denied','total':mutation_pass+relabel_pass+pop_pass})
if (mutation_pass,relabel_pass,pop_pass)!=(1000,500,500):raise SystemExit(1)
