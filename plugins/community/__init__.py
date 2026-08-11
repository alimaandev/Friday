"""Community plugin marketplace — drop a module folder here, then install it
from Settings → Plugins (or via the `/plugins` API). Only plugins listed in
``plugins/manifest.json`` are loaded into the tool registry."""

from plugins.community.fun import ShrugPlugin

__all__ = ["ShrugPlugin"]
