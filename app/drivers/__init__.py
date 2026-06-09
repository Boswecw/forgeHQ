"""forgeHQ drivers — the transport edge that emits shaped artifacts downstream.

Kept separate from the pure, transport-free shaping/domain core: drivers may do
I/O (HTTP) to the persistence boundary (DataForge-Local), the core may not.
"""
