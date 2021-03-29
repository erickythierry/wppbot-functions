# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
from subprocess import Popen, PIPE, STDOUT
import json
import os
from flask import Flask, request, url_for, render_template, send_file
from base64 import b64decode, b64encode
from werkzeug.utils import secure_filename
from youtube_search import YoutubeSearch


diretorio = os.getcwd()+'/'

def gerar_nome(inicio=''):
	numero = inicio+str(random.randint(123456,999999))
	return numero


def checa_resolucao(path):
	comando = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json {path}'
	subpro = Popen(comando, shell=True, stdout=PIPE)
	subprocess_return = subpro.stdout.read()
	jsn = subprocess_return.decode('utf-8')
	jsn = json.loads(jsn)
	jsn = jsn["streams"][0]
	altura = int(jsn["height"])
	largura = int(jsn["width"])
	retorno = [largura, altura]
	return retorno

def convert_to_webp(path):
	resolucao = checa_resolucao(path)
	nome = gerar_nome(path)
	quadrado = 200
	if resolucao[0]>resolucao[1]:
		valor1 = quadrado
		valor2 = -1
	else:
		valor1 = -1
		valor2 = quadrado
	
	
	comando = f'''ffmpeg -ss 0 -t 7 -i {path} -vf "scale={valor1}:{valor2}:flags=lanczos:force_original_aspect_ratio=decrease,fps=15, pad={quadrado}:{quadrado}:-1:-1:color=white@0.0,split[s0][s1];[s0]palettegen=reserve_transparent=on:transparency_color=ffffff [p];[s1][p]paletteuse" -loop 0 {nome}.webp'''
	subpro = Popen(comando, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	output = subpro.stdout.read()
	if 'Conversion failed' in str(output):
		os.system('rm '+nome+'.webp')
		comando = f'''ffmpeg -ss 0 -t 7 -i {path} -vf "scale=-1:{quadrado}:flags=lanczos:force_original_aspect_ratio=decrease,fps=15, pad={quadrado}:{quadrado}:-1:-1:color=white@0.0,split[s0][s1];[s0]palettegen=reserve_transparent=on:transparency_color=ffffff [p];[s1][p]paletteuse" -loop 0 {nome}.webp'''
		subpro = Popen(comando, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
		output = subpro.stdout.read()

	while not os.path.isfile((nome+'.webp')):
		time.sleep(0.1)
	return (nome+'.webp')


app = Flask(__name__) 

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/files/<nome>")
def file(nome):
	arquivo = diretorio+'arquivos/'+nome
	if os.path.isfile(arquivo):
		return send_file(arquivo, as_attachment=True)
	else:
		return 'arquivo nao encontrado'



@app.route("/2webp", methods=['GET', 'POST'])
def webp2():
	local = diretorio+'arquivos/'
	if request.method == 'POST':
		arquivo = request.files['file']
		nome = secure_filename(arquivo.filename)
		if '.mp4' in nome:
			arquivo.save(local+nome)
			convertido = convert_to_webp(local+nome)
			convertido = convertido.replace(local, '')
			return {'status': 200,'sucess':True, 'content': 'https://33a9be1a27ff.ngrok.io/files/'+convertido, 'nome': convertido}
		else:
			return {'status': 200,'sucess':False,'content': 'precisa ser mp4'}
	else:
		return 'apenas POST'


@app.route("/buscar", methods=["GET", "POST"])
def buscaVideo():
	data = request.form
	textoBusca = data.get("texto")
	numeroDeResultados = int(data.get("num"))
	if numeroDeResultados == None or numeroDeResultados == 0 or not numeroDeResultados:
		numeroDeResultados = 3
	
	results = YoutubeSearch(textoBusca, max_results=numeroDeResultados).to_dict()
	results = json.dumps(results, ensure_ascii=False)
	return results

