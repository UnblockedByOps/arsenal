from pyramid.view import notfound_view_config
from arsenalweb.views import site_layout

@notfound_view_config(renderer='arsenalweb:templates/404.pt')
def notfound_view(request):
    request.response.status = 404
    return {
        'error': 'Page not found.',
        'layout': site_layout('max'),
        'page_title_name': '404 Not Found',
        'column_selectors': {},
        'page_title_type': 'none',
    }
