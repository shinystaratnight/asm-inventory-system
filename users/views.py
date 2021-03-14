from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from users.forms import LoginForm

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
        
        messages.error(request, 'Username or password is incorrect.')
    
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')


def password_reset(request):
    if request.method == 'POST':
        pass

    return render(request, 'users/password_recovery.html')