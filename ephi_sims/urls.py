"""
URL configuration for ephi_sims project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
# from .views import home, chat_view, new_chat
from sims import views
# from .views import send_patient

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # path('plan', views.plan_list, name='plan'),
    # path('sims/', include('sims.urls')),
    path('plans/', views.plan_list, name='plan_list'),
    path('create/', views.plan_create, name='plan_create'),
    path('update/<int:pk>/', views.plan_update, name='plan_update'),
    path('delete/<int:pk>/', views.plan_delete, name='plan_delete'),
    # path('send-patient/', send_patient, name='send_patient'),
    path("chat/", views.chat_page, name="chat_page"),
    path("api/message/", views.message_proxy, name="message_proxy"),
    # path('chat/', new_chat, name='new_chat'),
    # path('<str:id>/', chat_view, name='chat'),

]

