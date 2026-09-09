from dataclasses import replace
import pytest
from purpose_finality import *

def test_derived_value_blocked_at_sink_by_source_lineage_even_with_valid_handle():
    s=PurposeSystem(); a=derived_act(); now=a.created_ms
    # Simulate a record that otherwise authorizes the derived write. Sink-side lineage remains independently load-bearing.
    r=BindingRecord(a.object_id,a.workflow_id,a.requester_id,a.workload_id,a.operation,a.destination_id,a.policy_version,now+60000)
    c=ValidationContext(now+1,a.requester_id,a.workload_id)
    d=s.ped.validate(a,r,c); assert d.allowed
    p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1')
    assert s.sink.verify_and_effect(a,d.handle,p,c)=='LINEAGE_RESTRICTION_MISMATCH'

def test_same_source_lineage_allowed_for_delivery_destination():
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,source_lineage=('address-619',)); d=s.ped.validate(a,r,c); assert d.allowed; p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1'); assert s.sink.verify_and_effect(a,d.handle,p,c)=='EFFECTUATED'

def test_omitting_lineage_is_not_proven_safe_limitation_case():
    # Deliberate limitation demonstration: if a producer can strip lineage before the enforced boundary, sink cannot infer it from content alone.
    s=PurposeSystem(); a=derived_act(); a=replace(a,source_lineage=()); r=BindingRecord(a.object_id,a.workflow_id,a.requester_id,a.workload_id,a.operation,a.destination_id,a.policy_version,a.created_ms+60000); c=ValidationContext(a.created_ms+1,a.requester_id,a.workload_id)
    d=s.ped.validate(a,r,c); assert d.allowed; p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1'); assert s.sink.verify_and_effect(a,d.handle,p,c)=='EFFECTUATED'

def test_lavr_generated_for_pass_and_fail():
    s=PurposeSystem(); a,r,c=baseline(); d1=s.ped.validate(a,r,c); d2=s.ped.validate(replace(a,act_id='bad',operation='infer household income',nonce='n2'),r,c); assert d1.lavr.body.result=='PASS'; assert d2.lavr.body.result=='FAIL'; assert len(s.lavr.items)==2

def test_lavr_chain_verifies():
    s=PurposeSystem(); a,r,c=baseline(); s.ped.validate(a,r,c); s.ped.validate(replace(a,act_id='2',nonce='2'),r,c); assert s.lavr.verify()

def test_lavr_chain_detects_tamper():
    s=PurposeSystem(); a,r,c=baseline(); s.ped.validate(a,r,c); x=s.lavr.items[0]; s.lavr.items[0]=replace(x,signature='00'+x.signature[2:]); assert not s.lavr.verify()

@pytest.mark.parametrize('reason_field,mut',[
('requester',{'requester_id':'x'}),('workload',{'workload_id':'x'}),('operation',{'operation':'x'}),('destination',{'destination_id':'x'}),('policy',{'policy_version':99})])
def test_fail_lavr_contains_act_digest_and_reason(reason_field,mut):
    s=PurposeSystem(); a,r,c=baseline(); bad=replace(a,act_id='bad-'+reason_field,nonce='n-'+reason_field,**mut); d=s.ped.validate(bad,r,c); assert not d.allowed; assert d.lavr.body.act_digest==digest(bad); assert d.lavr.body.reason!='ALLOW'
