# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
from subprocess import Popen, PIPE, STDOUT
import json
import os
from flask import Flask, request, url_for, render_template



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
	return 'oi'


if __name__ == "__main__":
    app.run()