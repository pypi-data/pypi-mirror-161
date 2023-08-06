import re


class Vault:
  """The ``laboro.vault.Vault`` class manages sensible informations that should not appear in log files.

  **Note:** Even if they will not appear in log files or `stdout`, **data stored in Vault are NOT encrypted** in the memory and are still recoverable by object inspection and debugger tools."""

  @property
  def protected(self):
    return "******"

  def __init__(self):
    self.secrets = list()
    self.pattern = None

  def add(self, string):
    """Adds a secret to the vault.

    Arguments:
      string: A string that should never appears in the logs.
    """
    self.secrets.append(str(string))
    self.pattern = re.compile(f"{'|'.join(self.secrets)}")

  def is_secret(self, string):
    """Checks if a string is registered is the Vault.

    Arguments:
      string: The string to check.

    Returns:
      ``bool``: *True* if ``string`` is a registered secret in this Vault, *False* otherwise.
    """
    return string in self.secrets

  def protect(self, string):
    """Redacts any string containing one of the secrets registered in this Vault.

    Arguments:
      string: The string to redact if necessary.

    Returns:
      ``str``: The ``string`` with all registered secrets redacted.
    """
    if self.pattern is not None:
      return re.sub(self.pattern, self.protected, str(string))
    return string

  def clear(self):
    """Clear the vault. All secret stored in vault will be deleted.
    """
    self.secrets = list()
    self.pattern = None
