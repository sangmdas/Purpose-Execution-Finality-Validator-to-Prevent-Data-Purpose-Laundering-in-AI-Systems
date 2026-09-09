from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from .core import canonical
class Ed25519Signer:
    def __init__(self,private=None): self.private=private or Ed25519PrivateKey.generate(); self.public=self.private.public_key()
    def sign(self,obj)->bytes:return self.private.sign(canonical(obj))
    def verify(self,obj,sig:bytes)->bool:
        try:self.public.verify(sig,canonical(obj));return True
        except InvalidSignature:return False
