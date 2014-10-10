from django.shortcuts import get_object_or_404, render
from .models import Competition


def authorized_user(func):
    """
    Check that user has read access to the competition
    """
    def decorator(request, *args, **kwargs):
        competition = get_object_or_404(Competition,
                                        slug=kwargs['competition_slug'])

        if competition.user_has_write_access(request.user):
            return func(request, *args, **kwargs)

        return render(request, 'competition/no_access.html', {
            'competition': competition,
        })

    return decorator