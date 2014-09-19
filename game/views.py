from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .forms import GameForm, CompetitionForm
from .models import Competition, Game, HistoricalScore, Score, Team

from .decorators import authorized_user


def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('competition_detail', kwargs={
            'competition_slug': 'default-competition'
        }))
    else:
        return render(request, 'user/login.html')


@login_required
def competition_list_all(request):
    return render(request, 'competition/list_all.html')


@login_required
@authorized_user
def team_detail(request, competition_slug, team_id):
    competition = get_object_or_404(Competition, slug=competition_slug)
    team = get_object_or_404(Team, pk=team_id)

    head2head = team.get_head2head(competition)
    last_results = team.get_recent_stats(competition, 10)
    longest_streak = team.get_longest_streak(competition)

    wins = team.get_wins(competition)
    defeats = team.get_defeats(competition)
    games = wins + defeats
    score = team.get_score(competition)

    context = {
        'team': team,
        'head2head': head2head,
        'last_results': last_results,
        'longest_streak': longest_streak,
        'games': games,
        'wins': wins,
        'defeats': defeats,
        'score': score,
        'competition': competition,
        'stats_per_week': team.get_stats_per_week(),
    }

    return render(request, 'game/team.html', context)


@login_required
@authorized_user
def team_general_detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    return render(request, 'game/team_general.html', {'team': team})


@login_required
def competition_add(request):
    if request.method == 'POST':
        form = CompetitionForm(request.POST)

        if form.is_valid():
            competition = form.save()

            return redirect('competition_detail',
                            competition_slug=competition.slug)
    else:
        form = CompetitionForm()

    return render(request, 'competition/new.html', {'form': form})


@login_required
@authorized_user
def competition_detail(request, competition_slug):
    """
    User logged in => homepage
    User not logged => login page
    User not authorized in competition => homepage
    """
    competition = get_object_or_404(Competition, slug=competition_slug)

    latest_results = Game.objects.get_latest(competition)
    score_board = Score.objects.get_score_board(competition)

    context = {
        'latest_results': latest_results,
        'score_board': score_board,
        'competition': competition,
        'user_can_edit_competition': competition.user_has_write_access(request.user),
    }

    return render(request, 'competition/detail.html', context)


@login_required
@authorized_user
def competition_detail_score_chart(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)
    score_chart_data = HistoricalScore.objects.get_latest_results_by_team(
        50, competition, True
    )
    return HttpResponse(score_chart_data, mimetype='application/json')


@login_required
@authorized_user
def game_add(request, competition_slug):
    competition = get_object_or_404(Competition, slug=competition_slug)

    if request.method == 'POST':
        form = GameForm(request.POST, competition=competition)

        if form.is_valid():
            Game.objects.announce(
                form.cleaned_data['winner'],
                form.cleaned_data['loser'],
                competition
            )

            return redirect(reverse('competition_detail', kwargs={
                'competition_slug': competition.slug
            }))
    else:
        form = GameForm(competition=competition)

    return render(request, 'game/add.html', {
        'form': form,
        'competition': competition,
    })


@login_required
@authorized_user
def game_remove(request, game_id, competition_slug):
    game = get_object_or_404(Game, pk=game_id)
    competition = get_object_or_404(Competition, slug=competition_slug)

    last_game = Game.objects.get_latest(competition)[0]

    if last_game.id == game.id:
        Game.objects.delete(game, competition)
        messages.add_message(request, messages.SUCCESS, 'Last game was deleted.')
    else:
        messages.add_message(request, messages.ERROR, 'Trying to delete a game that is not the last.')

    return redirect('game.views.competition_detail', competition_slug=competition_slug)
