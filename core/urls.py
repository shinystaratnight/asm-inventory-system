"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, i18n
from users.views import loginPage, logoutUser
from masters.views import dashboardPage

urlpatterns = [
    # url(r'^jsi18n/$', javascript_catalog),
    path('i18n/', include(i18n)),
]

urlpatterns += i18n.i18n_patterns(
    path('', dashboardPage, name='dashboard'),
    
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),

    path('master/', include('masters.urls')),

    path('admin/', admin.site.urls),
    path("", include("pages.urls")),
)
