import re
import openai 
from docx2python import docx2python
import docx
openai.api_key = "XXX" #Introducir aquí la llave 


#Funcion con la que obtendremos la respuesta de GPT-4

def respuesta(prompt, model="gpt-3.5-turbo",temperature=0):
    messages = [
	{"role": "system", "content": "Estás respondiendo a las preguntas de un examen de informática centrado en el lenguaje de programación C"},
	{"role": "user", "content": "Escribe un programa en C que escriba: Hello World"},
	{"role": "assistant", "content": "El siguiente código está escrito en C: \n\'\'\' \n#include <stdio.h> \nint main(void) \n{ \n\tprintf(\"Hello World\\n\"); \n\treturn 0; \n} \n\'\'\'"},
	{"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
    )
    return response.choices[0].message["content"]


#Lectura del documento Word

result=docx2python('exmayo2023.docx')
texto=result.text

preguntas=re.split(r"[0-9]\)\t\([0-9.]* punto[\w,. ]*\)",texto) #dividimos el texto en preguntas


#Respuesta a las preguntas

file=docx.Document()

prompt='La siguiente es una pregunta de un examen de programación del primer año del grado de ingeniería informática. Hay bastante tiempo para responder, así que tómate el tiempo que sea necesario para dar una respuesta completa y razonada paso a paso. La pregunta está delimitada por < >. Además en el caso de que tengas que escribir código, primero especifica el lenguaje en el que está escrito, y luego escribe dicho código delimitándolo con \'\'\' antes de la primera línea y después de la última, tal y como has hecho anteriormente.'
print(prompt)

for i in range(1,len(preguntas)):
	preguntas[i]=preguntas[i].strip()
	preguntas[i]=re.sub(r"\([0-9.]* punto[\w,. ]*\)","",preguntas[i]) #eliminamos el '(x puntos)' al inicio de cada ejercicio
	preguntas[i]=re.sub(r".*punto.*","",preguntas[i]) #eliminamos todos los parrafos que traten sobre puntuacion	
	preguntas[i]=re.sub("\n+","\n\n",preguntas[i]) #eliminamos grades espacios en blanco
	preguntas[i]=re.sub(r"\n[\w.\- <,/]*[iI]mage[\w.\- >,]*\n","",preguntas[i]) #eliminamos el texto que queda en las imagenes
	file.add_paragraph('Pregunta '+str(i)+': \n\n'+preguntas[i]+'\n\n\nRespuesta '+str(i)+': \n\n'+respuesta(prompt+'<'+preguntas[i])+'>')
	if i!=len(preguntas):
		file.add_page_break()
file.save("C:/Users/Usuario/Desktop/CiTIUS/llm-para-el-desarrollo-y-correccion-de-codigo/respuestas_prompt.docx")



