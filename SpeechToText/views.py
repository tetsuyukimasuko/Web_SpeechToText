# coding: UTF-8

from django.shortcuts import render
from django import forms
from django.utils.translation import ugettext_lazy as _
from .forms import WAVForm
from .WatsonSpeechRecognition import WatsonSTT
import csv
import io

# Create your views here.


def csvToDict(csv_file):
    result={}
    f=io.TextIOWrapper(csv_file)
    reader=csv.reader(f)
    for row in reader:
        word=row[0]
        sounds=row[1:]
        sound=[]
        for s in sounds:
            if s!='':
                sound.append(s)
        result.setdefault(word,sound)

    return result



def index(request):
    if request.method=='GET':
        return render(request,'index.html',{'form' : WAVForm(),})
    elif request.method=='POST':
        form=WAVForm(request.POST,request.FILES)
        if not form.is_valid():
            raise ValueError('invalid form')
        else:
            wav=request.FILES['WAV']
            size=wav.size
            if size>104857600:
                raise forms.ValidationError(_('Please keep filesize under 100 MB.'))


            WSTT=WatsonSTT('6ee201f0-a5fb-4cb7-9051-cce08478f9fa','vH5FYNyS0q0P')

            try:
                dict=request.FILES['dict']
                dict=csvToDict(dict)
                id=WSTT.CreateCustomModel('temp')
                print(WSTT.AddCustomWords(id,dict))
                use_dict=True
            except:
                use_dict=False

            if use_dict:
                print('こんばーと')
                text=WSTT.RecognizeAudioWithSession(wav,customization_id=id)
            else:
                text=WSTT.RecognizeAudioWithSession(wav)

            form=WAVForm()
            if use_dict:
                WSTT.DeleteCustomModel(id)
            
            return render(request,'convert.html',{'text' : text,'form' : form})