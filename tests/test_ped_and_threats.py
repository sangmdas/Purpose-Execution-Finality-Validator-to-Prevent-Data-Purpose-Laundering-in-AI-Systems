from dataclasses import replace
import pytest
from purpose_finality import *

FIELDS=[
('requester_id','advertising-service','REQUESTER_MISMATCH'),('workload_id','ad-workload','WORKLOAD_MISMATCH'),('object_id','other','OBJECT_MISMATCH'),
('workflow_id','other','WORKFLOW_MISMATCH'),('operation','infer household income','OPERATION_MISMATCH'),('destination_id','advertising-profile-database','DESTINATION_MISMATCH'),
('policy_version',39,'POLICY_VERSION_MISMATCH')]
@pytest.mark.parametrize('field,value,reason',FIELDS)
def test_candidate_mismatch_denied(field,value,reason):
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,**{field:value}); d=s.ped.validate(a,r,c); assert not d.allowed and d.reason==reason and d.handle is None and d.lavr.body.result=='FAIL'

@pytest.mark.parametrize('field,value,reason',[
('order_exists',False,'WORKFLOW_NOT_FOUND'),('object_association_ok',False,'OBJECT_ASSOCIATION_MISMATCH'),('recipient_assignment_ok',False,'RECIPIENT_ASSIGNMENT_MISMATCH'),
('binding_store_available',False,'BINDING_STORE_UNAVAILABLE'),('binding_store_integrity_ok',False,'BINDING_STORE_INTEGRITY_FAILURE'),('attestation_ok',False,'ATTESTATION_FAILURE'),('force_timeout',True,'VALIDATION_TIMEOUT')])
def test_context_fail_closed(field,value,reason):
    s=PurposeSystem(); a,r,c=baseline(); c=replace(c,**{field:value}); d=s.ped.validate(a,r,c); assert not d.allowed and d.reason==reason

def test_no_binding_record_fails_closed():
    s=PurposeSystem(); a,r,c=baseline(); d=s.ped.validate(a,None,c); assert d.reason=='NO_BINDING_RECORD' and not d.allowed

def test_candidate_expired():
    s=PurposeSystem(); a,r,c=baseline(); c=replace(c,now_ms=a.expires_ms+1); assert s.ped.validate(a,r,c).reason=='CANDIDATE_EXPIRED'

def test_binding_expired():
    s=PurposeSystem(); a,r,c=baseline(); r=replace(r,valid_until_ms=c.now_ms-1); assert s.ped.validate(a,r,c).reason=='BINDING_EXPIRED'

def test_binding_revoked():
    s=PurposeSystem(); a,r,c=baseline(); r=replace(r,revoked=True); assert s.ped.validate(a,r,c).reason=='BINDING_REVOKED'

def test_purpose_relabel_does_not_override_binding_records():
    s=PurposeSystem(); a,r,c=baseline(); attack=replace(a,requester_id='advertising-service',workload_id='ad-workload',operation='infer household income',destination_id='advertising-profile-database',declared_purpose='delivery')
    c=replace(c,authenticated_requester='advertising-service',authenticated_workload='ad-workload')
    d=s.ped.validate(attack,r,c); assert not d.allowed and d.reason in {'REQUESTER_MISMATCH','WORKLOAD_MISMATCH','OPERATION_MISMATCH','DESTINATION_MISMATCH'}

def test_attested_unauthorized_workload_still_denied():
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,requester_id='advertising-service',workload_id='ad-workload',operation='infer household income',destination_id='advertising-profile-database'); c=replace(c,authenticated_requester='advertising-service',authenticated_workload='ad-workload',attestation_ok=True)
    d=s.ped.validate(a,r,c); assert not d.allowed

def test_attestation_pass_never_overrides_operation_mismatch():
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,operation='infer household income'); c=replace(c,attestation_ok=True); assert s.ped.validate(a,r,c).reason=='OPERATION_MISMATCH'

def test_malicious_trusted_binding_record_demonstrates_residual_risk():
    # Draft explicitly assumes PED/binding records are not attacker-controlled. If a trusted record is maliciously rewritten, the PED can be induced to allow.
    s=PurposeSystem(); a,r,c=baseline(); attack=replace(a,requester_id='advertising-service',workload_id='ad-workload',operation='infer household income',destination_id='advertising-profile-database')
    malicious=replace(r,requester_id='advertising-service',workload_id='ad-workload',allowed_operation='infer household income',allowed_destination='advertising-profile-database')
    c=replace(c,authenticated_requester='advertising-service',authenticated_workload='ad-workload')
    assert s.ped.validate(attack,malicious,c).allowed
