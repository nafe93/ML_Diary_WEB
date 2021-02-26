from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^$',
        views.CurrentDayRedirectView.as_view(),
        name='current-day'
    ),
    url(
        r'^date-(?P<date>[\w-]+)/$',
        views.EntryPreviewView.as_view(),
        name='entry-preview'
    ),
    url(
        r'^date-(?P<date>[\w-]+)/edit/$',
        views.EntryEditView.as_view(),
        name='entry-edit'
    ),
    url(
        r'^calendar/$',
        views.CalendarView.as_view(),
        name='calendar'
    ),
    url(
        r'^category/$',
        views.CategoryView.as_view(),
        name='category'
    ),
    url(
        r'^category/add/$',
        views.CategoryAdd.as_view(),
        name='category_add'
    ),
    url(
        r'^category/update/(?P<category>.+)$',
        views.CategoryUpdate.as_view(),
        name='category_update'
    ),
    url(
        r'^category/save/update/(?P<category>.+)$',
        views.CategorySaveUpdate.as_view(),
        name='category_save_update'
    ),
    url(
        r'^category/delete/$',
        views.CategoryDelete.as_view(),
        name='category_delete'
    ),
    url(
        r'^tasks/$',
        views.TaskPreviewView.as_view(),
        name='task-preview'
    ),
    url(
        r'^search/$',
        views.SearchView.as_view(),
        name='search'
    ),
]
