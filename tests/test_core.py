from dataclasses import replace
import pytest
from purpose_finality import *

def issue(system=None):
    s=system or PurposeSystem(); act,rec,ctx=baseline(); d=s.ped.validate(act,rec,ctx); assert d.allowed
    ch=s.sink.challenge(); proof=s.sink.make_proof(d.handle,ch,'holder-1'); return s,act,rec,ctx,d,proof

def test_legitimate_request_effectuates_once():
    s,act,rec,ctx,d,p=issue(); n=[]
    assert s.sink.verify_and_effect(act,d.handle,p,ctx,lambda:n.append(1))=='EFFECTUATED'
    assert n==[1]

def test_replay_denied():
    s,act,rec,ctx,d,p=issue(); assert s.sink.verify_and_effect(act,d.handle,p,ctx)=='EFFECTUATED'; assert s.sink.verify_and_effect(act,d.handle,p,ctx)=='REPLAY_DETECTED'

@pytest.mark.parametrize('field,value,expected',[
('object_id','other','ACT_DIGEST_MISMATCH'),('workflow_id','other','ACT_DIGEST_MISMATCH'),('operation','infer household income','ACT_DIGEST_MISMATCH'),
('destination_id','advertising-profile-database','ACT_DIGEST_MISMATCH'),('requester_id','advertising-service','ACT_DIGEST_MISMATCH'),('workload_id','ad-workload','ACT_DIGEST_MISMATCH'),
('declared_purpose','marketing','ACT_DIGEST_MISMATCH'),('nonce','other','ACT_DIGEST_MISMATCH'),('policy_version',39,'ACT_DIGEST_MISMATCH')])
def test_post_issue_mutation_fails(field,value,expected):
    s,act,rec,ctx,d,p=issue(); mutated=replace(act,**{field:value}); assert s.sink.verify_and_effect(mutated,d.handle,p,ctx)==expected

def test_handle_signature_tamper():
    s,act,rec,ctx,d,p=issue(); h=replace(d.handle,signature='00'+d.handle.signature[2:]); assert s.sink.verify_and_effect(act,h,p,ctx)=='INVALID_HANDLE_SIGNATURE'

def test_wrong_pop_key():
    s,act,rec,ctx,d,p=issue(); ch=s.sink.challenge(); bad=s.sink.make_proof(d.handle,ch,'holder-2'); assert s.sink.verify_and_effect(act,d.handle,bad,ctx)=='POP_BINDING_MISMATCH'

def test_pop_signature_tamper():
    s,act,rec,ctx,d,p=issue(); bad=replace(p,signature='00'+p.signature[2:]); assert s.sink.verify_and_effect(act,d.handle,bad,ctx)=='POP_FAILURE'

def test_handle_expiry():
    s,act,rec,ctx,d,p=issue(); later=replace(ctx,now_ms=d.handle.body.expires_ms+1); assert s.sink.verify_and_effect(act,d.handle,p,later)=='HANDLE_EXPIRED'

def test_authenticated_requester_rechecked_at_sink():
    s,act,rec,ctx,d,p=issue(); bad=replace(ctx,authenticated_requester='other'); assert s.sink.verify_and_effect(act,d.handle,p,bad)=='REQUESTER_MISMATCH'

def test_authenticated_workload_rechecked_at_sink():
    s,act,rec,ctx,d,p=issue(); bad=replace(ctx,authenticated_workload='other'); assert s.sink.verify_and_effect(act,d.handle,p,bad)=='WORKLOAD_MISMATCH'
