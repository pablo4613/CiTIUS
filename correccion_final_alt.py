#!/usr/bin/env python

import re
import openai
from docx2python import docx2python
import docx
import os
import csv
openai.api_key = "XXX" #Introducir aquí la llave


#Funcion con la que obtendremos la respuesta del modelo

def correccion(prompt, model="gpt-3.5-turbo",temperature=0):
    messages = [
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


#Funcion para la lectura del documento Word con las preguntas

def lec_preguntas(file):
	result=docx2python(file)
	texto=result.text
	preguntas=re.split(r"[0-9]\)\t\([0-9.]* punto[\w,. ]*\)",texto) #dividimos el texto en preguntas
	for i in range(1,len(preguntas)):
		preguntas[i]=preguntas[i].strip()
		preguntas[i]=re.sub(r"\([0-9.]* punto[\w,. ]*\)","",preguntas[i]) #eliminamos el '(x puntos)' al inicio de cada ejercicio
		preguntas[i]=re.sub(r".*punto.*","",preguntas[i]) #eliminamos todos los parrafos que traten sobre puntuacion
		preguntas[i]=re.sub("\n+","\n\n",preguntas[i]) #eliminamos grades espacios en blanco
		preguntas[i]=re.sub(r"\n[\w.\- <,/]*[iI]mage[\w.\- >,]*\n","",preguntas[i]) #eliminamos el texto que queda en las imagenes
		preguntas[i]=re.split(r'[abciv]+\)[ \t]',preguntas[i]) #dividimos las preguntas en apartados
	return preguntas


#Funcion para la lectura del documento Word con las respuestas

def lec_respuestas(file):
	result=docx2python(file)
	texto=result.text
	respuestas=re.split(r"Pregunta [0-9]:",texto) #dividimos el texto en respuestas
	for i in range(len(respuestas)):
		respuestas[i]=respuestas[i].strip()
		respuestas[i]=re.split(r'[abciv]+\)\t',respuestas[i]) #dividimos las respuestas en apartados
	return respuestas


#Funcion con la que obtenemos las calificaciones de un examen

def cal_examen(examen_preguntas, examen_respuestas):
	prompt='Tu tarea es evaluar la respuesta a una pregunta de un examen de programación. Para ello razona primero tu respuesta y compárala con la respuesta proporcionada. No la evalúes hasta que no hayas respondido tú mismo a la pregunta. La pregunta está delimitada por <...> y la respuesta a evaluar está entre "...". El formato de tu respuesta debe ser el siguiente, respétalo sin añadir ningún comentario adicional y asegúrate de escribir una nota numérica sobre 100: \nPregunta: \n(copia aquí la pregunta del examen entre <...>) \n\n Respuesta: \n(copia aquí la respuesta del alumno entre "...") \n\n Calificación: \nLa nota es (nota sobre 100)%.'
	notas={}
	preguntas = lec_preguntas(examen_preguntas)
	respuestas = lec_respuestas(examen_respuestas)
	for i in range(1,len(preguntas)):
		if len(preguntas[i]) == 1:
			print(respuestas[i])
			cor = correccion(prompt+'<'+preguntas[i][0]+'>'+'"'+respuestas[i][0]+'"')
			print(cor)
			nota = re.search(r'Calificación:[ \n]*[a-zA-Z .,]*([0-9]*%)',cor)
			print('\nNota: '+nota[1])
			notas['Pregunta '+str(i)]=nota[1]
		else:
			for j in range(1,len(preguntas[i])):  #iteramos sobre cada apartado
				print('PREGUNTA {} APARTADO {}:\n'.format(i,j))
				cor = correccion(prompt+'<'+preguntas[i][0]+'\n'+preguntas[i][j]+'>'+'"'+respuestas[i][j-1]+'"')
				print(cor)
				nota = re.search(r'Calificación:[ \n]*[a-zA-Z .,]*([0-9]*%)',cor)
				print('\nNota: '+nota[1])
				print('\n\n--------\n\n')
				notas['Pregunta {} apartado {}'.format(i,j)]=nota[1]
		print('\n\n--------------------------\n\n')
	return notas

def calculo_nota_final(notas):
	nota_final = (int(notas['Pregunta 1'][:-1])/100)*1.5 + (int(notas['Pregunta 2 apartado 1'][:-1])/100)*0.5 + (int(notas['Pregunta 2 apartado 2'][:-1])/100)*0.5 + (int(notas['Pregunta 2 apartado 3'][:-1])/100)*0.5 + (int(notas['Pregunta 3 apartado 1'][:-1])/100)*0.5 + (int(notas['Pregunta 3 apartado 2'][:-1])/100)*0.5 + (int(notas['Pregunta 3 apartado 3'][:-1])/100)*0.25 + (int(notas['Pregunta 3 apartado 4'][:-1])/100)*0.25 + (int(notas['Pregunta 4'][:-1])/100)*1 + (int(notas['Pregunta 5'][:-1])/100)*1 + (int(notas['Pregunta 6'][:-1])/100)*2 + (int(notas['Pregunta 7 apartado 1'][:-1])/100)*0.5 + (int(notas['Pregunta 7 apartado 2'][:-1])/100)*0.5 + (int(notas['Pregunta 7 apartado 3'][:-1])/100)*0.5
	return nota_final


#----------------------------------------------

if __name__ == '__main__':
	files = os.listdir('.')  #Directorio en el que están guardados los exámenes
	examenes = []
	for file in files:
		if re.match(r'Examen_[0-9.]+', file) is not None:
			examenes.append(file)
	notas_total = []
	for examen in examenes:
		notas = cal_examen('exmayo2023.docx', examen)
		nota_final = calculo_nota_final(notas)
		notas['Nota final'] = nota_final
		notas['Nota real'] = re.search(r'_([0-9.]+)\.',examen)[1]
		notas['Examen'] = examen
		notas_total.append(notas)
	print(notas_total)
	keys = list(notas_total[0].keys())
	keys = [keys[-1]] + keys[:-1]  #Ponemos el nombre del examen al que correponden las notas al inicio
	with open('calificaciones_alt.csv', 'w') as calificaciones:
		writer = csv.DictWriter(calificaciones, fieldnames=keys)
		writer.writeheader()
		writer.writerows(notas_total)

