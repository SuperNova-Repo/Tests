# -*- coding: utf-8 -*-
"""
vjackson.py - Directory Navigation Module

This module handles the addon's navigation structure and directory listings:
- Main index (country/region selection)
- Category navigation
- Refresh handlers for countries and channels
- Helper functions for creating directory items

The module acts as a router for the addon's menu structure,
delegating to vjlive.py for actual channel listing and playback.
"""

import sys
from urllib.parse import quote_plus

from xbmcgui import ListItem

# =============================================================================
# IMPORTS
# =============================================================================
try:
    from resources.lib import utils
except ImportError:
    from lib import utils

# =============================================================================
# INFOTAGGER
# =============================================================================
from infotagger.listitem import ListItemInfoTag


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _set_listitem_info(listitem, info_labels):
    """
    Set info labels on a ListItem.
    """
    info_tag = ListItemInfoTag(listitem, 'video')
    info_tag.set_info(info_labels)


# =============================================================================
# NAVIGATION HANDLERS
# =============================================================================

def _index(params):
    """
    Display the main index with three specific options:
    1. Country List
    2. TV Favorites
    3. Settings
    """
    utils.set_content("files")
    
    # 1. Country List
    addDir2("Country List", "show_countries", isFolder=True)
    
    # 2. TV Favorites
    # Keep context menu for quick cleanup
    fav_ctx = [
        ("Make M3U", f"RunPlugin({sys.argv[0]}?action=makem3u&group=favorites)"),
        ("Import Favorites", f"RunPlugin({sys.argv[0]}?action=importFavorites)"),
        ("Export Favorites", f"RunPlugin({sys.argv[0]}?action=exportFavorites)"),
        ("Remove All Favorites", f"RunPlugin({sys.argv[0]}?action=delallTvFavorit)"),
        ("Settings", f"RunPlugin({sys.argv[0]}?action=settings)")
    ]
    addDir2("TV Favorites", "favchannels", context=fav_ctx, isFolder=True)
    
    # 3. Settings
    addDir2("Settings", "settings", isFolder=False)
    
    utils.end(cacheToDisc=False)


def _show_countries(params):
    """
    Display the list of available countries/regions.
    (Formerly the main index).
    """
    utils.set_content("files")
    
    from resources.lib import vjlive
    
    # --- Red Refresh entry at top ---
    addDir2("[COLOR red]Refresh Country List[/COLOR]", "refresh_countries", isFolder=True)
    
    countries = vjlive.get_available_countries()
    
    for country in countries:
        # Create Context Menu with Make M3U option
        # We quote the group name to handle spaces/special chars safely in the URL
        safe_country = quote_plus(country)
        
        cm = [
            ("Make M3U", f"RunPlugin({sys.argv[0]}?action=makem3u&group={safe_country})"),
            ("Settings", f"RunPlugin({sys.argv[0]}?action=settings)")
        ]
        
        addDir2(country, "channelsbycategory", 
                context=cm,
                group=country)
    
    utils.end(cacheToDisc=False)


def _livecategories(params):
    """
    Display live categories (backward compatibility).
    Now redirects to show_countries to maintain structure.
    """
    _show_countries(params)


def _refresh_countries(params):
    """
    Force-refresh the country list, show progress, and cleanly reload.
    """
    import xbmc
    import xbmcgui
    from resources.lib import vjlive
    
    progress = xbmcgui.DialogProgress()
    progress.create('', 'Refreshing country list...')
    progress.update(30)
    
    vjlive.refresh_country_cache()
    
    progress.update(70, 'Fetching fresh list...')
    vjlive.get_available_countries(use_cache=False)
    
    progress.update(100)
    progress.close()
    
    utils.notify("Country list refreshed")
    utils.end(succeeded=False)
    # Go back to parent, then refresh
    xbmc.executebuiltin("Action(ParentDir)")
    xbmc.sleep(300)
    xbmc.executebuiltin("Container.Refresh")


def _refresh_channels(params):
    """
    Force-refresh the channel list for a specific group, show progress, and reload.
    """
    import xbmc
    import xbmcgui
    from resources.lib import vjlive
    
    group = params.get("group", "Germany")
    
    progress = xbmcgui.DialogProgress()
    progress.create('', f'Refreshing channels for {group}...')
    progress.update(30)
    
    vjlive.refresh_group_cache(group)
    
    progress.update(70, 'Fetching fresh list...')
    vjlive.getchannels_by_group(group)
    
    progress.update(100)
    progress.close()
    
    utils.notify(f"{group} channels refreshed")
    utils.end(succeeded=False)
    # Go back to parent (the channel list), then force it to refresh
    xbmc.executebuiltin("Action(ParentDir)")
    xbmc.sleep(300)
    xbmc.executebuiltin("Container.Refresh")


# =============================================================================
# DIRECTORY ITEM CREATION
# =============================================================================

def addDir(name, params, isFolder=True, context=None):
    """
    Add a directory item to the current listing.
    Uses Kodi's default folder icon.
    """
    listitem = ListItem(name)
    
    # Work on a copy so we don't mutate the caller's list
    context = list(context) if context else []
    
    if not context:
        context.append(("Settings", f"RunPlugin({sys.argv[0]}?action=settings)"))
    
    listitem.addContextMenuItems(context)
    
    info_labels = {"title": name, "plot": " "}
    _set_listitem_info(listitem, info_labels)
    
    utils.add(params, listitem, isFolder)


def addDir2(name, action, context=None, isFolder=True, **params):
    """
    Convenience wrapper for addDir with automatic action parameter.
    
    Example:
        addDir2("Germany", "channelsbycategory", group="Germany")
    """
    params["action"] = action
    addDir(name, params, isFolder, context or [])