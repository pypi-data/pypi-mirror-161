from crudlfap.models import URL, Controller
from crudlfap.router import Router
from crudlfap.views import generic


class ControllerRouter(Router):
    model = Controller

    views = [
        generic.DetailView,
        generic.ListView.clone(
            search_fields=(
                'app',
                'model',
            ),
            table_fields=(
                'app',
                'model',
            ),
        ),
    ]


# useless ?
# ControllerRouter().register()


class URLRouter(Router):
    model = URL
    icon = 'link'

    views = [
        generic.DetailView,
        generic.ListView.clone(
            search_fields=(
                'name',
                'controller__app',
                'controller__model',
            ),
            table_fields=(
                'controller',
                'id',
                'fullurlpath',
            ),
        ),
    ]


URLRouter().register()
