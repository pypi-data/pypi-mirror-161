#!/bin/env python3
"""
--------------------------------------------------------------------------------
  @author         : Michaël Costa michael.costa@mcos.nc
  @date           : 01/08/2022
  @version        : 1.0.0
  @description    : Encrypt string data from user input for Laboro usage.
--------------------------------------------------------------------------------
  Versions:
  1.0.0  01/08/2022 - Michaël Costa - Cre: Create
--------------------------------------------------------------------------------
"""
from laboro.crypto import Crypto


# ------------------------------------------------------------------------------
#  Objects and functions
# ------------------------------------------------------------------------------
def main():
  crypto = Crypto()
  crypto_key = input("\033[93mEnter key (Press 'Enter' to generate a new key): \033[0m")
  crypto.key = crypto_key
  if crypto.key is None or len(crypto.key) == 0:
    print("\033[97mGenerating a new key...\033[0m")
    crypto.key = crypto.gen_key()
  data = input("\033[93mEnter data: \033[0m")
  encrypted = crypto.encrypt(data)
  print(f"\033[93m{80 * '='}\033[0m")
  print(f"\033[93mCrypt key: \033[97m{crypto.key}\033[0m")
  print(f"\033[93mEncrypted data: \033[97m$crypt${encrypted}\033[0m")


# ------------------------------------------------------------------------------
#  Entry point
# ------------------------------------------------------------------------------
if __name__ == '__main__':
  main()
