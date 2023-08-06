from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class MarketManagerMarketBrowserMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Market Browser"),
            "fas fa-store-alt fa-fw",
            "marketmanager:marketbrowser",
            navactive=["marketmanager:marketbrowser"],
        )

    def render(self, request):
        if request.user.has_perm("marketmanager.basic_market_browser"):
            return MenuItemHook.render(self, request)
        return ""


class MarketManagerMarketManagerMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Market Manager"),
            "fas fa-store-alt-slash fa-fw",
            "marketmanager:marketmanager",
            navactive=["marketmanager:marketmanager"],
        )

    def render(self, request):
        if request.user.has_perm("marketmanager.advanced_market_browser"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return MarketManagerMarketBrowserMenuItem()


# @hooks.register("menu_item_hook")
# def register_menu():
#     return MarketManagerMarketManagerMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "marketmanager", r"^marketmanager/")
