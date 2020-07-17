# coding: utf-8
import unidecode
from flask import Flask, render_template, escape, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from datetime import datetime
from chatterbot.response_selection import get_first_response
from chatterbot.comparisons import levenshtein_distance
from chatterbot.conversation import Statement
from chatterbot.tagging import PosHypernymTagger
from chatterbot import utils
from chatterbot.logic import LogicAdapter
from chatterbot import filters
import csv
import sys
import os
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import nltk
from newspaper import Article
from newspaper import news_pool
from googlesearch import search
import wikipedia


import logging

logging.basicConfig(level=logging.INFO)

data_e_hora_atuais = datetime.now()
data_e_hora_em_texto = data_e_hora_atuais.strftime("%d/%m/%Y %H:%M")

app = Flask(__name__)




englishBot = ChatBot(
    "Chatterbot",
    input_adapter="chatterbot.input.VariableInputTypeAdapter",
    output_adapter="chatterbot.output.OutputAdapter",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        #'custom_preprocessors.PreprocessorCustom1'
    ],
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Desculpe, não compreendi a pergunta! Poderia informar o assunto desejado?',
            'maximum_similarity_threshold': 0.80,
            #'statement_comparison_function': ChatBot.comparisons.levenshtein_distance,
            #'response_selection_method': ChatBot.response_selection.get_first_response
        },
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.BestMatch',
        #'chatterbot.logic.TimeLogicAdapter',
    ],
    database_uri='sqlite:///database.db',
    statement_comparison_function = levenshtein_distance,
    response_selection_method = get_first_response
#read_only=True
)

trainer = ListTrainer(englishBot)

conv = open('chats.txt', encoding='utf-8').readlines()
#convinic = open('chatsinic.txt', encoding='utf-8').readlines()
#convcpf = open('chatscpf.txt', encoding='utf-8').readlines()
#convparc = open('chatsparc.txt', encoding='utf-8').readlines()
#convirpf = open('chatsirpf.txt', encoding='utf-8').readlines()

trainer.train(conv)
#trainer.train(convparc)
#trainer.train(convirpf)
#trainer.train(convcpf)

trainer.export_for_training('./my_export.json')


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get")
# function for the bot response
def get_bot_response():
    #userText = unidecode._unidecode(request.args.get('msg')).strip().lower() request.args.get('msg')
    #print(userText)
    userText = unidecode._unidecode(request.args.get('msg')).strip().lower()
    msg = userText
    response = englishBot.get_response(userText)
    if float(response.confidence) > 0.8:
        return str(englishBot.get_response(userText))
    elif float(response.confidence) > 0.4:
        wikipedia.set_lang("pt")
        a = msg
        result = wikipedia.search(a, results=1)
        page = wikipedia.summary(result, sentences=5)
        content = page
        # print(content)
        return str(content)
    elif float(response.confidence) == 0:
        entrada = str(msg).lower()
        p1 = 'http://receita.economia.gov.br/@@busca?advanced_search=False&sort_on=&SearchableText='
        p2 = '&portal_type%3Alist=Document&created.query%3Arecord%3Alist%3Adate=1970-01-02&created.range%3Arecord=min'
        html = str(p1 + entrada + p2)
        stop2 = nltk.corpus.stopwords.words('portuguese')
        stop2.append('faço')
        stop2.append('um')
        stop2.append('gostaria')
        stop2.append('fazer')
        stop2.append('saber')
        stop2.append('posso')
        stop2.append('como')
        splitter = re.compile('\\W+')
        lista_palavras = []
        lista = [p for p in splitter.split(entrada) if p != '']
        for p in lista:
            if p not in stop2:
                if len(p) > 1:
                    lista_palavras.append(p)
        ar = len(lista_palavras)
        ax = str(lista_palavras[0:ar])
        e = str(ax).replace(',', ' ').strip('[]')
        e.strip("'")
        page = requests.get(html, verify=False, stream=False)
        soup = BeautifulSoup(page.content, 'lxml')
        cla = soup.find(class_='searchResults')
        links = cla.find_all('a')
        namess = soup.find_all('a')
        ra = (lista_palavras)
        # CRIAR A LISTA DE LINKS SITE RFB
        listr = []
        for link in links:
            texto = str(link.get_text()).lower().replace('ã', 'a').replace('-', ' ').replace('ç', 'c').split()
            # print(len(texto))
            url = str(link.get('href'))
            # print(len(url))
            urls = str(link.get('href')).lower().replace('/', ' ').replace('-', ' ').replace('.', ' ').split()
            # print(len(urls))
            if entrada in texto:
                listr.append(url)
            for i in range(0, ar):
                if lista_palavras[i] in texto:
                    listr.append(url)
                elif lista_palavras[i] in urls:
                    listr.append(url)

        listag = []
        rec = 'site:receita.economia.gov.br intext:' + msg + " -filetype:pdf -.pdf"
        for urla in search(rec, tld='com.br', lang='pt-br', stop=3, pause=2):
            listag.append(urla)

        g = int(len(listag))
        #print(g)

        listago = []
        for z in range(0, g):
            ur = str(listag[z])
            listago.append(ur)

        # print(listago)
        # print(len(listago))
        qo = int(len(listago))
        # print(listr)
        # print(len(listr))
        listaunida = listago + listr
        conj = list(set(listaunida))
        # print(conj)
        # print(len(conj))
        # print(type(conj))

        # print(p)
        # print(len(p))
        j = len(conj)

        reports2 = []
        news_pool.set(reports2, threads_per_source=2)
        news_pool.join()
        for r in range(0, j):
            ia = str(conj[r])
            article = Article(ia, language="pt")
            try:
                article.download()
                article.parse()
                article.text
                article.nlp()
                article.summary
            except:
                pass

            reports2.append(str(article.summary).replace('\n', ' '))
        # print(len(reports2))

        resposta_finalc = set(reports2)
        resposta_final = (str(resposta_finalc).replace('\n', ' ').replace('[', ' ').replace(']', ' ').replace(',', ' ').replace("'", ' ').replace('{', ' ').replace("}", ' '))

        f = csv.writer(open('chats.txt', 'a', encoding='utf-8'))
        f.writerow([msg + '\n' + resposta_final])

        return str(resposta_final)



if __name__ == '__main__':
    app.run()
