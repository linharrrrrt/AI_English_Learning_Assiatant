from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
# Create your views here.
from django.template import loader
from .models import Words,Sentence
from . import forms
import random

from openai import OpenAI
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

def translation_page(request):
    return render(request, 'translation_page.html')

import os

BASE_URL = os.getenv('OPENAI_API_BASE')
API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def get_ai_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        temperature=0.21,
        max_tokens=600,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content


@csrf_exempt
def translate(request):
    
    if request.method == 'POST':
        sentence = request.POST.get('sentence')
        # 配置你的OpenAI API密钥
        translation = get_ai_response("翻译为中文："+sentence)
        print("translation: ", translation)
        return JsonResponse({'translation': translation})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_word(request):
    if request.method == 'POST':
        word = request.POST.get('word')
        sentence_val = request.POST.get('sentence')
        print("word: ", word)
        print("sentence: ", sentence_val)
        sentence = Sentence.objects.filter(sentence=sentence_val).first()
        word_information = get_ai_response(word+"在这个句子中的中文意思是什么？请只回答在该句中的含义、词性和发音即可，回答的格式按照\"单词或词组,词性,发音,含义\"的格式，不要回答其他的内容:"+sentence_val)
        word_information= word_information.split(',')
        type = word_information[1]
        pronunciation = word_information[2]
        mean = word_information[3]
        new_word = Words.objects.create(word=word, pronunciation=pronunciation, type=type, mean=mean, sentence=sentence)
        data = {
            'word': new_word.word,
            'pronunciation': new_word.pronunciation,
            'type': new_word.type,
            'mean': new_word.mean,
            'add_date': new_word.add_date.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化日期
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_sentence(request):
    if request.method == 'POST':
        sentence = request.POST.get('sentence')
        translation = get_ai_response("翻译为中文："+sentence)
        syntactic_analysis = get_ai_response("请对下面这个句子进行分解，保留标点符号，每个部分之间添加/符号，请只输出划分后的句子，不要回答其他内容，这是英文句子："+sentence)
        sentence = Sentence.objects.create(sentence=sentence, syntactic_analysis=syntactic_analysis, translation=translation)
        data = {
            'id': sentence.id,
            'sentence': sentence.sentence,  # 假设模型字段名为sentence_text
            'syntactic_analysis': sentence.syntactic_analysis,  # 假设模型字段名为sentence_text
            'translation': sentence.translation,
            'add_date': sentence.add_date.strftime('%Y-%m-%d'),  # 格式化日期
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def addMultipleSentences(request):
    if request.method == 'POST':
        sentences = request.POST.get('sentence')
        count = 0
        for sentence in sentences.splitlines():
            if len(sentence)>0:
                print(sentence)
                count += 1
                translation = get_ai_response("翻译为中文："+sentence)
                syntactic_analysis = get_ai_response("请对下面这个句子进行分解，保留标点符号，每个部分之间添加/符号，请只输出划分后的句子，不要回答其他内容，这是英文句子："+sentence)
                sentence = Sentence.objects.create(sentence=sentence, syntactic_analysis=syntactic_analysis, translation=translation)
        return JsonResponse({'success': 'Sentences added successfully, added '+str(count)+' sentences'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_words(request):
    if request.method == 'POST':
        sentence = request.POST.get('sentence')
        sentence = Sentence.objects.filter(sentence=sentence).first()
        # words = sentence.words.all()
        words = Words.objects.filter(sentence=sentence)
        return JsonResponse({'words': words})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_sentence(request):
    if request.method == 'POST':
        unlearned_sentence_ids = Sentence.objects.filter(learned=False).values_list('id', flat=True)
    
        if unlearned_sentence_ids:
            # 随机选择一个ID
            random_id = random.choice(unlearned_sentence_ids)
            # 根据随机选择的ID获取Sentence对象
            sentence = Sentence.objects.get(id=random_id)
            sentence.learned = True
            words = sentence.words.all()
            
            # 序列化Sentence对象
            sentence_data = serializers.serialize('json', [sentence])
            
            # 序列化Word对象
            words_data = serializers.serialize('json', words)
            
            # 构建响应数据
            data = {
                'sentence': sentence_data,
                'words': words_data,
            }
            print(data)
            
            # 返回JSON响应
            return JsonResponse(data)
        else:
            sentence = None
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def getSentence_by_mark_sentence(request):
    if request.method == 'POST':
        sentence = request.POST.get('sentence')
        sentence = Sentence.objects.filter(sentence=sentence).first()
        sentence.learned = True  # 简化了切换learned状态的逻辑
        sentence.save()

        unlearned_sentence_ids = Sentence.objects.filter(learned=False).values_list('id', flat=True)
    
        if unlearned_sentence_ids:
            # 随机选择一个ID
            random_id = random.choice(unlearned_sentence_ids)
            # 根据随机选择的ID获取Sentence对象
            sentence = Sentence.objects.get(id=random_id)
            sentence.learned = True
            words = sentence.words.all()
            # 序列化Sentence对象
            sentence_data = serializers.serialize('json', [sentence])
            # 序列化Word对象
            words_data = serializers.serialize('json', words)
            
            # 构建响应数据
            data = {
                'sentence': sentence_data,
                'words': words_data,
            }
            print(data)
            
            # 返回JSON响应
            return JsonResponse(data)
        else:
            sentence = None
    return JsonResponse({'error': 'Invalid request'}, status=400)

def input_sentences(request):
    # Your logic to display the input sentences page
    return render(request, 'translation_page.html')

def words_list(request):
    # Your logic to display the words list page
    words = Words.objects.all()
    return render(request, 'word_list.html', {'words': words})

def sentences_list(request):
    sentences = Sentence.objects.all()
    # Your logic to display the sentences list page
    return render(request, 'sentence_list.html',  {'sentences': sentences})

def view_sentence(request, sentence_id):
    sentence = get_object_or_404(Sentence, pk=sentence_id)
    # Your logic to display the sentences list page
    return render(request, 'sentence_detail.html',  {'sentence': sentence})

def delete_sentence(request,sentence_id):
    # Your logic to delete a sentence
    sentence = get_object_or_404(Sentence, pk=sentence_id)
    # 删除对象
    sentence.delete()
    # 尝试获取HTTP请求的Referer头部，即用户之前所在的页面URL
    referer_url = request.META.get('HTTP_REFERER')
    # 如果Referer头部存在，并且不为空，则重定向回Referer URL
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        # 如果Referer头部不存在或为空，重定向到默认页面，比如句子列表
        # return HttpResponseRedirect(reverse('polls:sentences'))
        # 重定向到单词列表页面或其他适当的页面
        return HttpResponseRedirect(reverse('polls:sentences'))  # 假设'word_list_url'是单词列表页面的URL名称

def remove_word(request, word_id):
    # Your logic to delete a word
    word = get_object_or_404(Words, pk=word_id)
    # 删除对象
    word.delete()

    # 尝试获取HTTP请求的Referer头部，即用户之前所在的页面URL
    referer_url = request.META.get('HTTP_REFERER')

    # 如果Referer头部存在，并且不为空，则重定向回Referer URL
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        # 如果Referer头部不存在或为空，重定向到默认页面，比如句子列表
        # return HttpResponseRedirect(reverse('polls:sentences'))
        # 重定向到单词列表页面或其他适当的页面
        return HttpResponseRedirect(reverse('polls:words'))  # 假设'word_list_url'是单词列表页面的URL名称
 
def mark_sentence(request, sentence_id):
    # Your logic to mark a sentence as learned
    sentence = get_object_or_404(Sentence, pk=sentence_id)
    sentence.learned = not sentence.learned  # 简化了切换learned状态的逻辑
    sentence.save()

    # 尝试获取HTTP请求的Referer头部，即用户之前所在的页面URL
    referer_url = request.META.get('HTTP_REFERER')

    # 如果Referer头部存在，并且不为空，则重定向回Referer URL
    if referer_url:
        return HttpResponseRedirect(referer_url)
    else:
        # 如果Referer头部不存在或为空，重定向到默认页面，比如句子列表
        return HttpResponseRedirect(reverse('polls:sentences'))