from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib import auth
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/')
	else:
		if request.method == 'GET' and 'next' in request.GET:
			return render_to_response('login.html', {'next' : request.GET['next']})
		else:
			return render_to_response('login.html', {'next' : ''})

#@login_required(login_url='/login/')
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/login/')