from datetime import date, datetime

from dateutil.rrule import DAILY, rrule
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic.base import RedirectView, TemplateView
from django.http import HttpResponse
from django.http import JsonResponse

from .models import DiaryEntry, DiaryCategory, DiaryImage, DiaryTasks

import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


DATE_FORMAT = '%Y-%m-%d'


def month_index(index):
    maps = {
        'Январь': 1,
        'Февраль': 2,
        'Март': 3,
        'Апрель': 4,
        'Май': 5,
        'Июнь': 6,
        'Июль': 7,
        'Август': 8,
        'Сентябрь': 9,
        'Октябрь': 10,
        'Ноябрь': 11,
        'Декабрь': 12,
    }
    return maps.get(index)


def month_names(index):
    maps = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }
    return maps.get(index)


def raw_queryset_as_values_list(raw_qs):
    columns = raw_qs.columns
    for row in raw_qs:
        yield tuple(getattr(row, col) for col in columns)


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar.html'
    login_url = '/login/'

    def get(self, request):
        current_year = timezone.now().year

        a = date(current_year, 1, 1)
        b = date(current_year, 12, 31)

        months = {}
        existing_entries = {
            entry.date: True if entry.date else False
            for entry in DiaryEntry.objects.filter(
                author=request.user,
            ).exclude(text="")
        }

        for dt in rrule(DAILY, dtstart=a, until=b):
            months.setdefault(month_names(dt.month), [])

            if dt.day == 1:
                for i in range(dt.weekday()):
                    months[month_names(dt.month)].append('-')

            months[month_names(dt.month)].append(
                (dt.date(), existing_entries.get(dt.date(), False))
            )

        last_days = [
            timezone.now() - timezone.timedelta(days=i)
            for i in range(0, 5)
        ]

        for index, day in enumerate(last_days):
            e = DiaryEntry.objects.filter(
                date=day, author=self.request.user
            ).first()
            last_days[index] = (day, bool(e.text if e else False))

        context = {
            'months': months,
            'last_days': last_days,
            'current_month': month_names(timezone.now().month),
            'current_day': timezone.now().day,
            'title': 'Django Diary - Даты',
        }
        return self.render_to_response(context)


class CurrentDayRedirectView(RedirectView):
    """View to redirect user to current day diary."""

    def get_redirect_url(self, *args, **kwargs):
        now = timezone.now()
        return f'/diary/date-{now.strftime(DATE_FORMAT)}'


class EntryPreviewView(LoginRequiredMixin, TemplateView):
    """View for diary entry preview."""
    template_name = 'entry_preview.html'
    login_url = '/login/'

    def get(self, request, date):
        try:
            date = datetime.strptime(date or '', DATE_FORMAT)
        except ValueError:
            raise Http404()

        entry, created = DiaryEntry.objects.get_or_create(
            author=request.user, date=date,
            defaults={'text': ''}
        )

        context = {
            'prev_date': (entry.date - timezone.timedelta(days=1)),
            'next_date': (entry.date + timezone.timedelta(days=1)),
            'entry': entry,
            'title': entry.date,
        }

        return self.render_to_response(context)


class EntryEditView(EntryPreviewView):
    template_name = 'entry_edit.html'
    login_url = '/login/'

    def post(self, request, date=None):
        text = request.POST.get('text')

        DiaryEntry.objects.update_or_create(
            author=request.user,
            date=date,
            defaults={
                'text': text
            }
        )

        messages.add_message(
            request, messages.SUCCESS, 'Дневник успешно сохранен!'
        )

        return HttpResponseRedirect(f'/diary/date-{date}')


class SearchView(TemplateView):
    """
    TODO
    1. Normal query in URL
    2. Pagination
    3. Message - not found
    """
    template_name = 'search.html'

    def get(self, request, search=None):
        context = self.get_context_data()

        context['results'] = DiaryEntry.objects.filter(
            text__iregex=search
        ) if search else None
        context['search'] = search
        context['title'] = 'Django Diary - Поиск'

        return self.render_to_response(context)

    def post(self, request):
        search = request.POST.get('search')
        return self.get(request, search=search)


class CategoryView(LoginRequiredMixin, TemplateView):
    """View for diary category preview."""
    template_name = 'category_preview.html'
    login_url = '/login/'

    def get(self, request, date=None):
        categories = DiaryCategory.objects.all().filter(author_id=request.user.id)

        context = {
            'categories': categories.values()
        }

        return self.render_to_response(context)


class CategoryAdd(LoginRequiredMixin, TemplateView):
    """View for diary category add."""
    template_name = 'category_add.html'
    login_url = '/login/'

    def post(self, request):

        if request.method == "POST":

            category = request.POST.get('category')

            if len(str(category)) > 0 and str(category).isspace() == False:

                new_category = DiaryCategory(
                    date=datetime.now().date(),
                    Category=category,
                    author=request.user
                )

                new_category.save()

                messages.add_message(
                    request, messages.SUCCESS, 'Категория успешно сохранена!'
                )

                return HttpResponseRedirect(f'/diary/category/add/')

            else:
                messages.add_message(
                    request, messages.SUCCESS, 'Категорию не удалось сохранить!'
                )

                return HttpResponseRedirect(f'/diary/category/add/')

        else:
            messages.add_message(
                request, messages.SUCCESS, 'Категорию не удалось сохранить!'
            )

            return HttpResponseRedirect(f'/diary/category/add/')


class CategoryUpdate(LoginRequiredMixin, TemplateView):
    """View for diary category update view."""
    template_name = 'category_update.html'
    login_url = '/login/'

    def get(self, request, category=None):
        if request.method == "GET":
            context = {
                'category': str(category).split("=")[1]
            }

            return self.render_to_response(context)


class CategorySaveUpdate(LoginRequiredMixin, TemplateView):
    """View for diary category add."""
    template_name = 'category_update.html'
    login_url = '/login/'

    def post(self, request, category=None):
        new_category = request.POST.get('new_category')

        update_category = DiaryCategory.objects.filter(
            Category=str(category).split("=")[1],
            author=request.user
        ).update(Category=str(new_category))

        messages.add_message(
            request, messages.SUCCESS, 'Категория успешно обновлена!'
        )

        return HttpResponseRedirect(f'/diary/category/update/category={new_category}')


class CategoryDelete(LoginRequiredMixin, TemplateView):
    """View for diary category delete."""

    def post(self, request):

        if request.is_ajax():

            category = json.loads(request.body)

            my_category = category['category_to_delete']

            delete_category = DiaryCategory.objects.filter(
                Category=my_category,
                author=request.user
            ).delete()

            return JsonResponse({"success": True})

        else:

            return JsonResponse({"success": False})


class TaskPreviewView(LoginRequiredMixin, TemplateView):
    """View for diary tasks preview."""
    template_name = 'task_preview.html'
    login_url = '/login/'

    def get(self, request):
        tasks = DiaryTasks.objects.raw(
            f"SELECT * FROM diary_diarytasks "
            f"left join diary_diarycategory "
            f"on diary_diarytasks.category_id = diary_diarycategory.id "
            f"where diary_diarytasks.date = '{datetime.now().date()}';"
        )
        context = {
            'tasks': tasks
        }

        return self.render_to_response(context)


class TaskPreviewViewDate(LoginRequiredMixin, TemplateView):
    """View for diary tasks preview by date."""

    def post(self, request):
        if request.is_ajax():
            get_request = json.loads(request.body)
            get_month_from, get_day_from, get_year_from = str(get_request['date_from']).split(" ")

            get_day_from = get_day_from[:-1]
            get_month_from = month_index(get_month_from)
            date_from = str(get_year_from) + "-" + str(get_month_from) + "-" + str(get_day_from)

            get_month_to, get_day_to, get_year_to = str(get_request['date_to']).split(" ")

            get_day_to = get_day_to[:-1]
            get_month_to = month_index(get_month_to)
            date_to = str(get_year_to) + "-" + str(get_month_to) + "-" + str(get_day_to)

            tasks = DiaryTasks.objects.raw(
                f"SELECT * FROM diary_diarytasks "
                f"left join diary_diarycategory "
                f"on diary_diarytasks.category_id = diary_diarycategory.id "
                f"where diary_diarytasks.date >= '{date_from}' and diary_diarytasks.date <= '{date_to}'"
                f"order by diary_diarytasks.date desc;"
            )

        list_tasks = raw_queryset_as_values_list(tasks)
        list_tasks = list(list_tasks)

        return JsonResponse({"success": list_tasks})


class TaskAdd(LoginRequiredMixin, TemplateView):
    """View for diary task add."""
    template_name = 'task_add.html'
    login_url = '/login/'

    def get(self, request):
        categories = DiaryCategory.objects.all().filter(author_id=request.user.id)
        categories = [i for i in categories.values()]

        context = {
            'categories': categories
        }

        return self.render_to_response(context)


class TaskSave(LoginRequiredMixin, TemplateView):
    """View for diary task add."""
    template_name = 'task_add.html'
    login_url = '/login/'

    def post(self, request):

        task = request.POST.get('task')
        completion_percent = request.POST.get('completion_percent')
        task_category = request.POST.get('task_category')
        date_create_task_text = request.POST.get('date_create_task_text')

        if (len(str(task)) > 0 and str(task).isspace() == False) and \
                (len(str(completion_percent)) > 0 and str(completion_percent).isspace() == False) and \
                (len(str(task_category)) > 0 and str(task_category).isspace() == False) and \
                (len(str(date_create_task_text)) > 0 and str(date_create_task_text).isspace() == False):

            get_month_from, get_day_from, get_year_from = str(date_create_task_text).split(" ")

            get_day_from = get_day_from[:-1]
            get_month_from = month_index(get_month_from)
            date_create = str(get_year_from) + "-" + str(get_month_from) + "-" + str(get_day_from)

            new_task = DiaryTasks(
                task=str(task),
                completion_percent=int(completion_percent),
                category_id=int(task_category),
                date=date_create,
                author=request.user
            )

            new_task.save()

            messages.add_message(
                request, messages.SUCCESS, 'Задача успешно сохранена!'
            )

            return HttpResponseRedirect(f'/diary/tasks/add/')

        else:
            messages.add_message(
                request, messages.SUCCESS, 'Задачу не удалось сохранить!'
            )

            return HttpResponseRedirect(f'/diary/tasks/add/')


class TaskDelete(LoginRequiredMixin, TemplateView):
    """View for diary task delete."""

    def post(self, request):

        if request.is_ajax():

            task_id = json.loads(request.body)
            task_id = int(task_id['task_delete'])

            task = DiaryTasks.objects.filter(
                id=task_id,
                author=request.user
            ).delete()

            return JsonResponse({"success": True})

        else:

            return JsonResponse({"success": False})


class TaskUpdate(LoginRequiredMixin, TemplateView):
    """View for diary task update."""
    template_name = 'task_update.html'
    login_url = '/login/'

    def get(self, request, task_id=None):
        categories = DiaryCategory.objects.all().filter(author_id=request.user.id)
        categories = [i for i in categories.values()]

        tasks = DiaryTasks.objects.raw(
            f"SELECT * FROM diary_diarytasks "
            f"left join diary_diarycategory "
            f"on diary_diarytasks.category_id = diary_diarycategory.id "
            f"where diary_diarytasks.id = '{task_id}'"
        )

        context = {
            'categories': categories,
            'tasks': tasks
        }

        return self.render_to_response(context)


class TaskUpdateSave(LoginRequiredMixin, TemplateView):
    """View for diary task update."""
    template_name = 'task_update.html'
    login_url = '/login/'

    def post(self, request, task_id=None):
        task = request.POST.get('task')
        completion_percent = request.POST.get('completion_percent')
        task_category = request.POST.get('task_category')
        date_update_task_text = request.POST.get('date_update_task_text')

        if (len(str(task)) > 0 and str(task).isspace() == False) and \
                (len(str(completion_percent)) > 0 and str(completion_percent).isspace() == False) and \
                (len(str(task_category)) > 0 and str(task_category).isspace() == False) and \
                (len(str(date_update_task_text)) > 0 and str(date_update_task_text).isspace() == False):

            get_month_from, get_day_from, get_year_from = str(date_update_task_text).split(" ")

            get_day_from = get_day_from[:-1]
            get_month_from = month_index(get_month_from)
            date_update = str(get_year_from) + "-" + str(get_month_from) + "-" + str(get_day_from)

            update_task = DiaryTasks.objects.filter(
                id=task_id,
                author=request.user
            ).update(
                task=str(task),
                completion_percent=int(completion_percent),
                category_id=int(task_category),
                date=date_update
            )

            messages.add_message(
                request, messages.SUCCESS, 'Задача успешно обновлена!'
            )

            return HttpResponseRedirect(f'/diary/tasks/update/' + task_id)

        else:

            messages.add_message(
                request, messages.SUCCESS, 'Задачу не удалось обновить!'
            )

            return HttpResponseRedirect(f'/diary/tasks/update/' + task_id)


class StatisticsPreview(LoginRequiredMixin, TemplateView):
    """View for diary tasks preview by date."""

    """View for diary statistics."""
    template_name = 'statistics_preview.html'
    login_url = '/login/'

    def post(self, request):

        if request.is_ajax():

            get_request = json.loads(request.body)
            get_month_from, get_day_from, get_year_from = str(get_request['date_from']).split(" ")

            get_day_from = get_day_from[:-1]
            get_month_from = month_index(get_month_from)
            date_from = str(get_year_from) + "-" + str(get_month_from) + "-" + str(get_day_from)

            get_month_to, get_day_to, get_year_to = str(get_request['date_to']).split(" ")

            get_day_to = get_day_to[:-1]
            get_month_to = month_index(get_month_to)
            date_to = str(get_year_to) + "-" + str(get_month_to) + "-" + str(get_day_to)

            categories_id = tuple(get_request["categories_id"])

            tasks = DiaryTasks.objects.raw(
                f"SELECT * FROM diary_diarytasks "
                f"left join diary_diarycategory "
                f"on diary_diarytasks.category_id = diary_diarycategory.id "
                f"where diary_diarytasks.date >= '{date_from}' and diary_diarytasks.date <= '{date_to}'"
                f"and diary_diarytasks.category_id in {categories_id} "
                f"order by diary_diarytasks.date desc;"
            )

            list_tasks = raw_queryset_as_values_list(tasks)
            list_tasks = list(list_tasks)
            # create df
            df = pd.DataFrame(list_tasks)
            df = df[[1, 2, 3, 8]]
            df.columns = ['date', 'task', 'complete', 'category']
            # unique class
            categories = list(pd.unique(df.category))

            # create mean
            grouped_frame = df.groupby(['date', 'category']).mean('complete')
            grouped_frame['date'] = grouped_frame.index.get_level_values(0)
            grouped_frame['category'] = grouped_frame.index.get_level_values(1)
            grouped_frame.reset_index(drop=True, inplace=True)


            X = []
            Y = []
            for category in categories:
                x = list(grouped_frame[grouped_frame['category'] == category]['date'])
                y = list(grouped_frame[grouped_frame['category'] == category]['complete'])
                X.append(x)
                Y.append(y)

            # pie
            score_by_category = df.groupby(['category']).sum()
            score = score_by_category.sum()
            norm_score = score_by_category / score
            pie = list(norm_score['complete'])

            return JsonResponse({"x": X, "y": Y, "categories": categories, "pie": pie})

        return JsonResponse({"x": [], "y": [], "categories": []})

class StatisticsCategories(LoginRequiredMixin, TemplateView):
    """View for diary task add."""
    template_name = 'statistics_preview.html'
    login_url = '/login/'

    def get(self, request):
        categories = DiaryCategory.objects.all().filter(author_id=request.user.id)
        categories = [i for i in categories.values()]

        context = {
            'categories': categories
        }

        return self.render_to_response(context)