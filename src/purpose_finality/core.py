from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from typing import Optional
import hashlib, hmac, json, os, sqlite3, threading, time, uuid


def canonical(obj) -> bytes:
    if hasattr(obj, '__dataclass_fields__'):
        obj = asdict(obj)
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(obj) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def sign(key: bytes, obj) -> str:
    return hmac.new(key, canonical(obj), hashlib.sha256).hexdigest()

def ct_eq(a: str,b: str)->bool:
    return hmac.compare_digest(a,b)

@dataclass(frozen=True)
class CandidateAct:
    version: int
    act_id: str
    requester_id: str
    workload_id: str
    object_id: str
    workflow_id: str
    operation: str
    destination_id: str
    declared_purpose: str  # deliberately untrusted metadata
    nonce: str
    created_ms: int
    expires_ms: int
    policy_version: int
    source_lineage: tuple[str, ...] = ()
    derived_object_id: str = ''

@dataclass(frozen=True)
class BindingRecord:
    object_id: str
    workflow_id: str
    requester_id: str
    workload_id: str
    allowed_operation: str
    allowed_destination: str
    policy_version: int
    valid_until_ms: int
    revoked: bool = False

@dataclass(frozen=True)
class ValidationContext:
    now_ms: int
    authenticated_requester: str
    authenticated_workload: str
    order_exists: bool = True
    object_association_ok: bool = True
    recipient_assignment_ok: bool = True
    binding_store_available: bool = True
    binding_store_integrity_ok: bool = True
    attestation_ok: bool = True
    force_timeout: bool = False

@dataclass(frozen=True)
class LAVRBody:
    seq: int
    prev_hash: str
    act_digest: str
    result: str
    reason: str
    policy_version: int
    timestamp_ms: int

@dataclass(frozen=True)
class LAVR:
    body: LAVRBody
    signature: str

@dataclass(frozen=True)
class HandleBody:
    handle_id: str
    act_digest: str
    object_id: str
    workflow_id: str
    operation: str
    requester_id: str
    workload_id: str
    destination_id: str
    policy_version: int
    nonce: str
    issued_ms: int
    expires_ms: int
    pop_key_id: str

@dataclass(frozen=True)
class ExecutionHandle:
    body: HandleBody
    signature: str

@dataclass(frozen=True)
class HolderProofBody:
    handle_id: str
    act_digest: str
    sink_id: str
    challenge: str
    pop_key_id: str

@dataclass(frozen=True)
class HolderProof:
    body: HolderProofBody
    signature: str

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    handle: Optional[ExecutionHandle]
    lavr: LAVR

class LAVRChain:
    def __init__(self, key: bytes):
        self.key=key; self._lock=threading.Lock(); self._seq=0; self._prev='0'*64; self.items=[]
    def append(self, act: CandidateAct, result: str, reason: str, now_ms: int)->LAVR:
        with self._lock:
            self._seq += 1
            body=LAVRBody(self._seq,self._prev,digest(act),result,reason,act.policy_version,now_ms)
            lavr=LAVR(body,sign(self.key,body))
            self._prev=digest(lavr)
            self.items.append(lavr)
            return lavr
    def verify(self)->bool:
        prev='0'*64
        for i,x in enumerate(self.items,1):
            if x.body.seq!=i or x.body.prev_hash!=prev or not ct_eq(x.signature,sign(self.key,x.body)):
                return False
            prev=digest(x)
        return True

class PED:
    def __init__(self, key: bytes, lavr_chain: LAVRChain, max_handle_ms: int=2000):
        self.key=key; self.lavr=lavr_chain; self.max_handle_ms=max_handle_ms
    def validate(self, act: CandidateAct, rec: Optional[BindingRecord], ctx: ValidationContext, pop_key_id='holder-1')->Decision:
        reason='ALLOW'
        if ctx.force_timeout: reason='VALIDATION_TIMEOUT'
        elif not ctx.binding_store_available: reason='BINDING_STORE_UNAVAILABLE'
        elif not ctx.binding_store_integrity_ok: reason='BINDING_STORE_INTEGRITY_FAILURE'
        elif rec is None: reason='NO_BINDING_RECORD'
        elif ctx.now_ms > act.expires_ms: reason='CANDIDATE_EXPIRED'
        elif ctx.now_ms > rec.valid_until_ms: reason='BINDING_EXPIRED'
        elif rec.revoked: reason='BINDING_REVOKED'
        elif act.policy_version != rec.policy_version: reason='POLICY_VERSION_MISMATCH'
        elif ctx.authenticated_requester != act.requester_id or act.requester_id != rec.requester_id: reason='REQUESTER_MISMATCH'
        elif ctx.authenticated_workload != act.workload_id or act.workload_id != rec.workload_id: reason='WORKLOAD_MISMATCH'
        elif act.object_id != rec.object_id: reason='OBJECT_MISMATCH'
        elif act.workflow_id != rec.workflow_id: reason='WORKFLOW_MISMATCH'
        elif act.operation != rec.allowed_operation: reason='OPERATION_MISMATCH'
        elif act.destination_id != rec.allowed_destination: reason='DESTINATION_MISMATCH'
        elif not ctx.order_exists: reason='WORKFLOW_NOT_FOUND'
        elif not ctx.object_association_ok: reason='OBJECT_ASSOCIATION_MISMATCH'
        elif not ctx.recipient_assignment_ok: reason='RECIPIENT_ASSIGNMENT_MISMATCH'
        # Attestation is NOT authority. A failed required attestation can deny, but passing never overrides above checks.
        elif not ctx.attestation_ok: reason='ATTESTATION_FAILURE'
        allowed=(reason=='ALLOW')
        lavr=self.lavr.append(act,'PASS' if allowed else 'FAIL',reason,ctx.now_ms)
        if not allowed: return Decision(False,reason,None,lavr)
        hb=HandleBody(str(uuid.uuid4()),digest(act),act.object_id,act.workflow_id,act.operation,act.requester_id,act.workload_id,act.destination_id,act.policy_version,act.nonce,ctx.now_ms,min(act.expires_ms,ctx.now_ms+self.max_handle_ms),pop_key_id)
        return Decision(True,'ALLOW',ExecutionHandle(hb,sign(self.key,hb)),lavr)

class InMemoryReplay:
    def __init__(self): self._lock=threading.Lock(); self._used=set()
    def consume(self, hid:str)->bool:
        with self._lock:
            if hid in self._used:return False
            self._used.add(hid);return True

class SQLiteReplay:
    def __init__(self,path=':memory:'):
        self.path=path; self._lock=threading.Lock(); self.conn=sqlite3.connect(path,check_same_thread=False,timeout=30,isolation_level=None)
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.execute('CREATE TABLE IF NOT EXISTS used(handle_id TEXT PRIMARY KEY, used_ms INTEGER NOT NULL)')
    def consume(self,hid:str)->bool:
        with self._lock:
            try:
                self.conn.execute('BEGIN IMMEDIATE')
                self.conn.execute('INSERT INTO used VALUES(?,?)',(hid,int(time.time()*1000)))
                self.conn.execute('COMMIT');return True
            except sqlite3.IntegrityError:
                self.conn.execute('ROLLBACK');return False

class FinalitySink:
    def __init__(self,sink_id:str,key:bytes,pop_keys:dict[str,bytes],replay,lineage_rules:dict[str,set[tuple[str,str]]]|None=None):
        self.sink_id=sink_id; self.key=key; self.pop_keys=pop_keys; self.replay=replay; self.lineage_rules=lineage_rules or {}
    def challenge(self)->str: return os.urandom(16).hex()
    def make_proof(self,handle:ExecutionHandle,challenge:str,pop_key_id:str)->HolderProof:
        body=HolderProofBody(handle.body.handle_id,handle.body.act_digest,self.sink_id,challenge,pop_key_id)
        return HolderProof(body,sign(self.pop_keys[pop_key_id],body))
    def verify_and_effect(self,act:CandidateAct,handle:ExecutionHandle,proof:HolderProof,ctx:ValidationContext,effect=lambda:None)->str:
        if not ct_eq(handle.signature,sign(self.key,handle.body)): return 'INVALID_HANDLE_SIGNATURE'
        b=handle.body
        if digest(act)!=b.act_digest:return 'ACT_DIGEST_MISMATCH'
        if act.object_id!=b.object_id:return 'OBJECT_MISMATCH'
        if act.workflow_id!=b.workflow_id:return 'WORKFLOW_MISMATCH'
        if act.operation!=b.operation:return 'OPERATION_MISMATCH'
        if act.requester_id!=b.requester_id:return 'REQUESTER_MISMATCH'
        if act.workload_id!=b.workload_id:return 'WORKLOAD_MISMATCH'
        if act.destination_id!=b.destination_id:return 'DESTINATION_MISMATCH'
        if act.policy_version!=b.policy_version:return 'POLICY_VERSION_MISMATCH'
        if act.nonce!=b.nonce:return 'NONCE_MISMATCH'
        if ctx.authenticated_requester!=b.requester_id:return 'REQUESTER_MISMATCH'
        if ctx.authenticated_workload!=b.workload_id:return 'WORKLOAD_MISMATCH'
        if ctx.now_ms>b.expires_ms:return 'HANDLE_EXPIRED'
        for src in act.source_lineage:
            if src in self.lineage_rules and (act.operation,act.destination_id) not in self.lineage_rules[src]:
                return 'LINEAGE_RESTRICTION_MISMATCH'
        pb=proof.body
        if pb.handle_id!=b.handle_id or pb.act_digest!=b.act_digest or pb.sink_id!=self.sink_id or pb.pop_key_id!=b.pop_key_id:return 'POP_BINDING_MISMATCH'
        k=self.pop_keys.get(pb.pop_key_id)
        if not k or not ct_eq(proof.signature,sign(k,pb)):return 'POP_FAILURE'
        if not self.replay.consume(b.handle_id):return 'REPLAY_DETECTED'
        effect();return 'EFFECTUATED'

class PurposeSystem:
    def __init__(self,replay='memory'):
        self.sign_key=b'ped-reference-signing-key-v1'; self.pop_keys={'holder-1':b'holder-one-key-v1','holder-2':b'holder-two-key-v1'}
        self.lavr=LAVRChain(b'lavr-chain-key-v1'); self.ped=PED(self.sign_key,self.lavr)
        self.replay=InMemoryReplay() if replay=='memory' else SQLiteReplay(replay if replay not in ('sqlite',) else ':memory:')
        self.sink=FinalitySink('data-release-sink',self.sign_key,self.pop_keys,self.replay,{'address-619':{('obtain delivery destination','assigned-courier-6')}})

def baseline(now=1_800_000_000_000):
    act=CandidateAct(1,'act-001','delivery-service','delivery-workload','address-619','delivery-order-842','obtain delivery destination','assigned-courier-6','delivery','nonce-001',now,now+10_000,38)
    rec=BindingRecord('address-619','delivery-order-842','delivery-service','delivery-workload','obtain delivery destination','assigned-courier-6',38,now+60_000,False)
    ctx=ValidationContext(now+1,'delivery-service','delivery-workload')
    return act,rec,ctx

def derived_act(now=1_800_000_000_000):
    return CandidateAct(1,'act-derived','advertising-service','ad-workload','income-estimate-52','ad-profile-workflow','write advertising profile','advertising-profile-database','advertising','nonce-derived',now,now+10_000,38,('address-619',),'income-estimate-52')
