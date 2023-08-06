"""


GPU Platform Utilities (gpu.platform)
*************************************

This module provides access to GPU Platform definitions.

:func:`device_type_get`

:func:`renderer_get`

:func:`vendor_get`

:func:`version_get`

"""

import typing

def device_type_get() -> str:

  """

  Get GPU device type.

  """

  ...

def renderer_get() -> str:

  """

  Get GPU to be used for rendering.

  """

  ...

def vendor_get() -> str:

  """

  Get GPU vendor.

  """

  ...

def version_get() -> str:

  """

  Get GPU driver version.

  """

  ...
