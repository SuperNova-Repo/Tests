# -*- coding: utf-8 -*-
"""
main.py - Addon Entry Point

This is the main entry point for the Kodi addon. It handles:
- Parsing URL parameters from Kodi
- Routing requests to appropriate handlers
- Smart dependency management with instant auto-confirmation
"""

# =============================================================================
# MAIN EXECUTION
# =============================================================================
# Only run when executed directly (not when imported)
if __name__ == "__main__":
    
    import sys
    import json
    import xbmc
    import xbmcgui
    
    # -------------------------------------------------------------------------
    # DEPENDENCY CHECK & INSTALLATION
    # -------------------------------------------------------------------------
    # Auto-install 'inputstream.ffmpegdirect' with auto-confirmation.
    # Uses explicit window ID (10100=yesnodialog) so SendClick works
    # reliably on any skin, including slow-rendering ones on Android.

    if not xbmc.getCondVisibility("System.HasAddon(inputstream.ffmpegdirect)"):
        xbmc.executebuiltin("InstallAddon(inputstream.ffmpegdirect)")

        # Wait for the confirm dialog to appear (Android needs 1-3s)
        for _ in range(20):
            xbmc.sleep(250)
            if xbmc.getCondVisibility("Window.IsActive(yesnodialog)"):
                break

        # Auto-confirm: target Yes button (ID 11) explicitly in DialogConfirm
        for _ in range(60):
            if xbmc.getCondVisibility("Window.IsActive(yesnodialog)"):
                xbmc.executebuiltin("SendClick(10100,11)")
            xbmc.sleep(500)
            if xbmc.getCondVisibility("System.HasAddon(inputstream.ffmpegdirect)"):
                break

        if not xbmc.getCondVisibility("System.HasAddon(inputstream.ffmpegdirect)"):
            xbmcgui.Dialog().ok(
                "Error - Missing Dependency",
                "Please install FFmpegDirect manually or restart Kodi and try again.\n"
                "Without FFmpegDirect this addon cannot function properly."
            )
            sys.exit()
    
    # Import addon modules
    from resources.lib import utils, vjlive, vjackson
    
    # =========================================================================
    # PARAMETER PARSING
    # =========================================================================
    params = dict(utils.parse_qsl(sys.argv[2][1:]))
    channel_name = params.get("name")
    action = params.pop("action", None)
    
    # =========================================================================
    # REQUEST ROUTING
    # =========================================================================
    # TV Favorites actions (have both name and action params)
    if channel_name and action == "addTvFavorit":
        vjlive.change_favorit(channel_name, group=params.get("group", ""))
    
    elif channel_name and action == "delTvFavorit":
        vjlive.change_favorit(channel_name, delete=True)
        
    elif channel_name and action == "renameTvFavorit":
        vjlive.rename_favorit_dialog(channel_name)
        
    elif channel_name and action == "moveTvFavoritUp":
        vjlive.move_favorit_logic(channel_name, "up")
        
    elif channel_name and action == "moveTvFavoritDown":
        vjlive.move_favorit_logic(channel_name, "down")

    elif channel_name and action == "moveTvFavoritTop":
        vjlive.move_favorit_logic(channel_name, "top")

    elif channel_name and action == "moveTvFavoritBottom":
        vjlive.move_favorit_logic(channel_name, "bottom")
    
    elif channel_name:
        urls = None
        urls_param = params.get("urls")
        if urls_param:
            try:
                urls = json.loads(urls_param)
            except (json.JSONDecodeError, TypeError):
                pass
        group = params.get("group")
        vjlive.livePlay(channel_name, urls, group=group)
    
    elif action is None:
        vjackson._index(params)
        
    elif action == "show_countries":
        vjackson._show_countries(params)
    
    elif action == "channelsbycategory":
        vjlive.channels_by_group(params.get("group", "Germany"))
    
    elif action == "settings":
        utils.addon.openSettings()
    
    elif action == "livecategories":
        vjackson._livecategories(params)
    
    elif action == "favchannels":
        vjlive.favchannels()
        
    elif action == "makem3u":
        vjlive.makem3u(params.get("group"))
    
    elif action == "delallTvFavorit":
        utils.clear_all_favorites()
        utils.notify("All TV Favorites removed")
        xbmc.executebuiltin("Container.Refresh")
    
    elif action == "exportFavorites":
        utils.export_favorites()
    
    elif action == "importFavorites":
        utils.import_favorites()
    
    else:
        handler = getattr(vjackson, f"_{action}", None)
        if handler:
            handler(params)
        else:
            utils.log(f"Unknown action: {action}", "main")