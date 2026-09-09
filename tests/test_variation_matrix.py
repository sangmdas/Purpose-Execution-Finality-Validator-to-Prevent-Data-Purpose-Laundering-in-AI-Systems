from dataclasses import replace
import pytest
from purpose_finality import *

@pytest.mark.parametrize('purpose',['delivery','DELIVERY','targeted_marketing','', 'x'*128])
def test_declared_purpose_string_never_substitutes_for_external_records_on_legitimate_binding(purpose):
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,declared_purpose=purpose); d=s.ped.validate(a,r,c); assert d.allowed

@pytest.mark.parametrize('declared',['delivery','customer_support','legitimate_interest','consent','security','fraud_prevention'])
def test_self_asserted_good_sounding_purpose_cannot_rescue_wrong_operation(declared):
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,operation='infer household income',declared_purpose=declared); d=s.ped.validate(a,r,c); assert not d.allowed and d.reason=='OPERATION_MISMATCH'

@pytest.mark.parametrize('delta',[0,1,10,100,1000,1999,2000])
def test_handle_lifetime_is_clamped(delta):
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,expires_ms=c.now_ms+delta); d=s.ped.validate(a,r,c)
    if delta<0: assert not d.allowed
    else:
        assert d.allowed and d.handle.body.expires_ms<=c.now_ms+2000

@pytest.mark.parametrize('version',[0,1,37,39,40,1000])
def test_wrong_policy_versions_fail(version):
    s=PurposeSystem(); a,r,c=baseline(); a=replace(a,policy_version=version); d=s.ped.validate(a,r,c); assert not d.allowed and d.reason=='POLICY_VERSION_MISMATCH'
