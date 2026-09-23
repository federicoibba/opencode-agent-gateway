"""Reconcile the agents in this repo into Open WebUI.

The package is run as ``python -m workspace_sync`` (see ``__main__``). Modules:

* ``constants`` — tags, directory names and the gateway session header;
* ``text``      — small YAML/text helpers;
* ``libraries`` — load skills, MCPs and prompts from the shared libraries;
* ``agents``    — discover agents, resolve ``extends``, validate conflicts;
* ``webui``     — open-webui HTTP client and the gateway connection;
* ``sync``      — build and upsert models, skills, prompts and folders;
* ``cli``       — argument parsing, the dry-run plan and the run loop.
"""

__all__ = ["cli"]
