# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
from subprocess import Popen, PIPE, STDOUT
import json, os, time
from flask import Flask, request, url_for, render_template, send_file
from base64 import b64decode, b64encode
from werkzeug.utils import secure_filename


diretorio = './'

def gerar_nome(inicio=''):
	numero = inicio+str(random.randint(123456,999999))
	return numero


def checa_resolucao(path):
	comando = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json {}".format(path)
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
	
	
	comando = 'ffmpeg -ss 0 -t 7 -i {} -vf "scale={}:{}:flags=lanczos:force_original_aspect_ratio=decrease,fps=15, pad={}:{}:-1:-1:color=white@0.0,split[s0][s1];[s0]palettegen=reserve_transparent=on:transparency_color=ffffff [p];[s1][p]paletteuse" -loop 0 {}.webp'.format(path,valor1,valor2,quadrado,quadrado,nome)
	subpro = Popen(comando, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	output = subpro.stdout.read()
	if 'Conversion failed' in str(output):
		os.system('rm '+nome+'.webp')
		comando = 'ffmpeg -ss 0 -t 7 -i {} -vf "scale=-1:{}:flags=lanczos:force_original_aspect_ratio=decrease,fps=15, pad={}:{}:-1:-1:color=white@0.0,split[s0][s1];[s0]palettegen=reserve_transparent=on:transparency_color=ffffff [p];[s1][p]paletteuse" -loop 0 {}.webp'.format(path,quadrado,quadrado,quadrado,nome)
		subpro = Popen(comando, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
		output = subpro.stdout.read()

	while not os.path.isfile((nome+'.webp')):
		time.sleep(0.1)
	return (nome+'.webp')


app = Flask(__name__) 

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/qr", methods=['GET', 'POST'])
def pegaqr():
	local = diretorio+'arquivos/'
	if request.method == 'POST':
		arquivo = request.files['file']
		nome = secure_filename(arquivo.filename)
		aleatorio = gerar_nome()
		arquivo.save(local+aleatorio+nome)
		nome = aleatorio+nome
		return {'status': 200,'sucess':True, 'content': 'http://204.48.24.92:5000/files/'+nome, 'nome': nome}

@app.route("/files/<nome>")
def file(nome):
	arquivo = diretorio+'arquivos/'+nome
	if os.path.isfile(arquivo) and '.png' not in arquivo:
		return send_file(arquivo, as_attachment=True)
	elif os.path.isfile(arquivo) and '.png' in arquivo:
		
		with open(arquivo, "rb") as file:
			encoded_string = b64encode(file.read()).decode("utf-8")
		return render_template('qr.html', qr=encoded_string)
	else:
		return 'arquivo nao encontrado'

@app.route("/webp", methods=['GET', 'POST'])
def webp():
	local = diretorio+'arquivos/'
	print(local, os.system('ls'))
	conteudo = request.json
	if conteudo != None:
		if 'arquivo' in conteudo and 'nome' in conteudo:
			arquivo = conteudo['arquivo']
			nome = conteudo['nome']
			print(nome)
			bytes = b64decode(arquivo, validate=True)
			print('salvando', local)
			f = open(local+nome, 'wb')
			f.write(bytes)
			f.close()

			convertido = convert_to_webp(local+nome)
			with open(convertido, "rb") as file:
				encoded_string = b64encode(file.read()).decode("utf-8")

			return {'status': 200,'sucess':True, 'content': encoded_string, 'nome': "{}.webp".format(nome)}


		else:
			return {'status': 200,'sucess':False, 'content':'falta de elemento no json'}
	else:
		return {'status': 200, 'sucess':False, 'content':'json nao recebido'}


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
			return {'status': 200,'sucess':True, 'content': 'http://204.48.24.92:5000/files/'+convertido, 'nome': convertido}
		else:
			return {'status': 200,'sucess':False,'content': 'precisa ser mp4'}
	else:
		return 'apenas POST'
