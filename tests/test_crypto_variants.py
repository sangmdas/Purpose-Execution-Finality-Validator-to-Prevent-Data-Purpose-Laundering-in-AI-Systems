from dataclasses import replace
from purpose_finality import *

def test_ed25519_candidate_signature_roundtrip():
    a,_,_=baseline(); s=Ed25519Signer(); sig=s.sign(a); assert s.verify(a,sig)

def test_ed25519_detects_candidate_mutation():
    a,_,_=baseline(); s=Ed25519Signer(); sig=s.sign(a); assert not s.verify(replace(a,operation='infer household income'),sig)

def test_ed25519_handle_body_roundtrip():
    ps=PurposeSystem(); a,r,c=baseline(); d=ps.ped.validate(a,r,c); s=Ed25519Signer(); sig=s.sign(d.handle.body); assert s.verify(d.handle.body,sig)

def test_ed25519_detects_handle_body_mutation():
    ps=PurposeSystem(); a,r,c=baseline(); d=ps.ped.validate(a,r,c); s=Ed25519Signer(); sig=s.sign(d.handle.body); assert not s.verify(replace(d.handle.body,destination_id='ads-db'),sig)
