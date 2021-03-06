from django.shortcuts import reverse


def extra_context(request):
    return {
        'menu': (
            ('Сегодня', reverse('diary:current-day')),
            ('Календарь', reverse('diary:calendar')),
            ('Задачи', reverse('diary:task-preview')),
            ('Категории', reverse('diary:category')),
            ('Статистика', reverse('diary:analysis')),
            ('Поиск', reverse('diary:search'))
            # ('Tags', '/tags/'),
        )
    }
