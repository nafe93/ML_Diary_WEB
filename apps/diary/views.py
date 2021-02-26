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

DATE_FORMAT = '%Y-%m-%d'


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
        categories = [i['Category'] for i in categories.values()]

        context = {
            'categories': categories
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
        print(category)
        update_category = DiaryCategory.objects.filter(
            Category=str(category).split("=")[1],
            author=request.user
        ).update(Category=str(new_category))

        print(update_category)

        messages.add_message(
            request, messages.SUCCESS, 'Категория успешно обновлена!'
        )

        return HttpResponseRedirect(f'/diary/category/update/category={new_category}')


class CategoryDelete(LoginRequiredMixin, TemplateView):
    """View for diary category delete."""
    template_name = 'category_preview.html'
    login_url = '/login/'

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
    """View for diary category preview."""
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