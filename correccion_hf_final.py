from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from docx2python import docx2python
import re
import torch

#Lectura del documento Word
result=docx2python('exmayo2023.docx')
texto=result.text

preguntas=re.split(r"[0-9]\)\t\([0-9.]* punto[\w,. ]*\)",texto) #dividimos el texto en preguntas

#"Limpiamos" las preguntas
for i in range(1,len(preguntas)):
        preguntas[i]=preguntas[i].strip()
        preguntas[i]=re.sub(r"\([0-9.]* punto[\w,. ]*\)","",preguntas[i]) #eliminamos el '(x puntos)' al inicio de cada ejercicio
        preguntas[i]=re.sub(r".*punto.*","",preguntas[i]) #eliminamos todos los parrafos que traten sobre puntuacion
        preguntas[i]=re.sub("\n+","\n\n",preguntas[i]) #eliminamos grades espacios en blanco
        preguntas[i]=re.sub(r"\n[\w.\- <,/]*[iI]mage[\w.\- >,]*\n","",preguntas[i]) #eliminamos el texto que queda en las imagenes

#Tokenizamos las preguntas
checkpoint = "google/flan-ul2"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
print(preguntas[2])
inputs = tokenizer(preguntas[2], return_tensors="pt")
print(inputs)
print(tokenizer.batch_decode(inputs['input_ids']))

#Las pasamos al modelo
model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
outputs = model.generate(**inputs, max_length=200)
print(outputs)
respuesta = tokenizer.batch_decode(outputs, skip_special_tokens=True)
print(respuesta)

