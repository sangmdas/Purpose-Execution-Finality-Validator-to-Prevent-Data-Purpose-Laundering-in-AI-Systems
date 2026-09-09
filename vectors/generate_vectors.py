import json,sys
from dataclasses import asdict,replace
sys.path.insert(0,'src')
from purpose_finality import *

a,r,c=baseline()
cases=[]
def add(name,aa=a,rr=r,cc=c,expected='ALLOW'):
    cases.append({'name':name,'act':asdict(aa),'record':asdict(rr) if rr else None,'context':asdict(cc),'expected':expected,'act_digest':digest(aa)})
add('allow-baseline')
add('deny-requester',replace(a,requester_id='ad'),expected='REQUESTER_MISMATCH')
add('deny-workload',replace(a,workload_id='ad-workload'),expected='WORKLOAD_MISMATCH')
add('deny-object',replace(a,object_id='other'),expected='OBJECT_MISMATCH')
add('deny-workflow',replace(a,workflow_id='other'),expected='WORKFLOW_MISMATCH')
add('deny-operation',replace(a,operation='infer household income'),expected='OPERATION_MISMATCH')
add('deny-destination',replace(a,destination_id='ads-db'),expected='DESTINATION_MISMATCH')
add('purpose-relabel-still-allow',replace(a,declared_purpose='TARGETED_MARKETING'),expected='ALLOW')
add('deny-policy-version',replace(a,policy_version=39),expected='POLICY_VERSION_MISMATCH')
add('deny-revoked',rr=replace(r,revoked=True),expected='BINDING_REVOKED')
add('deny-binding-expired',rr=replace(r,valid_until_ms=c.now_ms-1),expected='BINDING_EXPIRED')
add('deny-no-record',rr=None,expected='NO_BINDING_RECORD')
add('deny-order-missing',cc=replace(c,order_exists=False),expected='WORKFLOW_NOT_FOUND')
add('deny-association',cc=replace(c,object_association_ok=False),expected='OBJECT_ASSOCIATION_MISMATCH')
add('deny-assignment',cc=replace(c,recipient_assignment_ok=False),expected='RECIPIENT_ASSIGNMENT_MISMATCH')
add('deny-binding-store-unavailable',cc=replace(c,binding_store_available=False),expected='BINDING_STORE_UNAVAILABLE')
add('deny-binding-integrity',cc=replace(c,binding_store_integrity_ok=False),expected='BINDING_STORE_INTEGRITY_FAILURE')
add('deny-attestation',cc=replace(c,attestation_ok=False),expected='ATTESTATION_FAILURE')
add('deny-timeout',cc=replace(c,force_timeout=True),expected='VALIDATION_TIMEOUT')
json.dump({'schema':1,'cases':cases},open('vectors/conformance_vectors.json','w'),indent=2)
print(len(cases))
