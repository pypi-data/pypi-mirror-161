#!/bin/env python3
"""
--------------------------------------------------------------------------------
  @author         : Michaël Costa michael.costa@mcos.nc
  @date           : 01/08/2022
  @version        : 1.0.0
  @description    : Decrypt data from Laboro crytpo.
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
  crypto_key = input("\033[93mEnter key: \033[0m")
  crypto.key = crypto_key
  encrypted = input("\033[93mEnter encrypted data (including $crypt$ prefix): \033[0m")
  encrypted = encrypted.replace("$crypt$", "")
  data = crypto.decrypt(encrypted)
  print(f"\033[93m{80 * '='}\033[0m")
  print(f"\033[93mData: \033[97m{data}\033[0m")


# ------------------------------------------------------------------------------
#  Entry point
# ------------------------------------------------------------------------------
if __name__ == '__main__':
  main()
