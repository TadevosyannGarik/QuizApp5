from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('topics/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('discipline/add/', views.add_discipline, name='add_discipline'),
    path('discipline/list/', views.discipline_list, name='discipline_list'),
    path('topic/add/', views.add_topic, name='add_topic'),
    path('topic/list/', views.topic_list, name='topic_list'),
    path('topic/incorrect/add/', views.add_incorrect_answer, name='add_incorrect_answer'),
    path('question/add/', views.add_question, name='add_question'),
    path('tests/', views.test_list, name='test_list'),
    path('register/', views.register, name='student_registration'),
    path('success/', views.success, name='success'),
    path('login/', views.login_view, name='login'),
    path('after/login', views.after_login, name='after_login')
]
