from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.template import loader

from .models import Choice, Question


def vote(request, question_id):
    if request.user.is_authenticated:
        if request.user.has_perm("polls.vote"):
            question = get_object_or_404(Question, pk=question_id)
            try:
                selected_choice = question.choice_set.get(pk=request.POST['choice'])
            except (KeyError, Choice.DoesNotExist):
                # Redisplay the question voting form.
                return render(request, 'polls/detail.html', {
                    'question': question,
                    'error_message': "You didn't select a choice.",
                })
            else:
                selected_choice.votes += 1
                selected_choice.save()
                # Always return an HttpResponseRedirect after successfully dealing
                # with POST data. This prevents data from being posted twice if a
                # user hits the Back button.
                return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        else:
            return render(request, 'polls/permission_error.html', {"user": request.user})
    else:
        return render(request, 'polls/login_error.html')


def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
