from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile, pytest
from purpose_finality import *

def issue(s):
    a,r,c=baseline(); d=s.ped.validate(a,r,c); p=s.sink.make_proof(d.handle,s.sink.challenge(),'holder-1'); return a,c,d,p

@pytest.mark.parametrize('workers,attempts',[(2,10),(4,32),(8,64),(16,100),(32,128)])
def test_memory_replay_concurrency_exactly_one(workers,attempts):
    s=PurposeSystem(); a,c,d,p=issue(s)
    with ThreadPoolExecutor(max_workers=workers) as ex: out=list(ex.map(lambda _:s.sink.verify_and_effect(a,d.handle,p,c),range(attempts)))
    assert out.count('EFFECTUATED')==1 and out.count('REPLAY_DETECTED')==attempts-1

@pytest.mark.parametrize('workers,attempts',[(2,8),(4,16),(8,32),(16,64)])
def test_sqlite_replay_concurrency_exactly_one(workers,attempts,tmp_path):
    s=PurposeSystem(str(tmp_path/'replay.db')); a,c,d,p=issue(s)
    with ThreadPoolExecutor(max_workers=workers) as ex: out=list(ex.map(lambda _:s.sink.verify_and_effect(a,d.handle,p,c),range(attempts)))
    assert out.count('EFFECTUATED')==1 and out.count('REPLAY_DETECTED')==attempts-1

def test_sqlite_persistence_across_reopen(tmp_path):
    path=str(tmp_path/'r.db'); s=PurposeSystem(path); a,c,d,p=issue(s); assert s.sink.verify_and_effect(a,d.handle,p,c)=='EFFECTUATED'; s.replay.conn.close()
    store=SQLiteReplay(path); sink=FinalitySink('data-release-sink',s.sign_key,s.pop_keys,store,{'address-619':{('obtain delivery destination','assigned-courier-6')}}); assert sink.verify_and_effect(a,d.handle,p,c)=='REPLAY_DETECTED'
