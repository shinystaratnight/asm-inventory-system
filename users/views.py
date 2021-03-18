from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.forms import LoginForm
from django.contrib.auth.models import User

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard/index.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = request.GET.get('next', 'dashboard')
                return redirect(redirect_url)
        else:
            messages.error(request, 'Username or password is incorrect.')
    return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def page_not_found(request, exception):
    return render(request, 'error/404.html')

def internal_error(request):
    return render(request, 'error/500.html')
