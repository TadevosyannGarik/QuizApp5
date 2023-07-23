from django.urls import path
from . import views, utils

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
]
