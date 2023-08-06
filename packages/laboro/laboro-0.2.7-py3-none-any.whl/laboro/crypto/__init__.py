from cryptography.fernet import Fernet
from laboro.error import LaboroError


_BLOCK_SIZE = 16


class Crypto:
  @property
  def key(self):
    if self._key is None:
      return None
    return self._key.decode()

  @key.setter
  def key(self, key):
    try:
      if key is not None:
        self._key = key.encode()
    except Exception as err:
      err_msg = f"[LaboroCryptoError] {err.__class__.__name__}: {err}"
      raise LaboroError(err_msg) from err

  def __init__(self):
    self._key = None

  def encrypt(self, data):
    try:
      crypto = Fernet(self._key)
      return crypto.encrypt(data.encode("utf-8")).decode("utf-8")
    except Exception as err:
      err_msg = f"[LaboroCryptoError] {err.__class__.__name__}: {err}"
      raise LaboroError(err_msg) from err

  def decrypt(self, encrypted):
    try:
      crypto = Fernet(self._key)
      return crypto.decrypt(encrypted.encode("utf-8")).decode("utf-8")
    except Exception as err:
      err_msg = f"[LaboroCryptoError] {err.__class__.__name__}: {err}"
      raise LaboroError(err_msg) from err

  def gen_key(self):
    return Fernet.generate_key().decode()
