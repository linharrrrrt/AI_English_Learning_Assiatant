from django.urls import path

from . import views

from django.contrib import admin

app_name = 'polls'   # 重点是这一行

urlpatterns = [
    # 例如: /polls/
    # path('', views.index, name='index'),
    path('', views.translation_page, name='translation_page'),
    path('admin/', admin.site.urls),
    path('translate/', views.translate, name='translate'),
    path('add_sentence/', views.add_sentence, name='add_sentence'),
    path('addMultipleSentences/', views.addMultipleSentences, name='addMultipleSentences'),
    path('get_sentence/', views.get_sentence, name='get_sentence'),
    path('getSentence_by_mark_sentence/', views.getSentence_by_mark_sentence, name='getSentence_by_mark_sentence'),
    path('add_word/', views.add_word, name='add_word'),
    path('get_word/', views.add_word, name='get_word'),
    path('input_sentences/', views.input_sentences, name='Input_Sentences'),
    path('words/', views.words_list, name='words'),
    path('sentences/', views.sentences_list, name='sentences'),
    path('<int:sentence_id>/view_sentence/', views.view_sentence, name='view_sentence'),
    path('<int:sentence_id>/mark_sentence/', views.mark_sentence, name='mark_sentence'),
    path('<int:sentence_id>/delete_sentence/', views.delete_sentence, name='delete_sentence'),
    path('<int:word_id>/remove_word/', views.remove_word, name='remove_word'),
]