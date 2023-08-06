from kavyanarthaki.text import ml
from kavyanarthaki.db import data
from kavyanarthaki.vritham import predict, _compute, _TripletGanams


def syllables(text):
    if isinstance(text, ml):text = text.text
    return ml(text).syllables()

def gl(text):
    if isinstance(text, ml):text = text.text
    return ml(text).laghuguru()
 
def MathraCount(akshara_pattern): # calculate maathra input NJYSBMTRGL string/list
    return _compute(akshara_pattern)

def LetterCount(text):
    return len(ml(text))

def ConvertGanamsToGL(string): # get GL text from NJYSBMTRGL string
    if isinstance(string, list):
        try:string=''.join(string)
        except:return -1
    if isinstance(string, tuple):
        try:string=''.join(list(string))
        except:return -1
    output = ''
    for character in string:
        output+=_TripletGanams(character)
    return output
 
def ConvertGLToGanams(text): # get NJYSBMTRGL from GL string
    if isinstance(text, list):
        try:text=''.join(text)
        except:return -1
    if isinstance(text, tuple):
        try:text=''.join(list(text))
        except:return -1
    triplets = {'LLL':'N','LLG':'S','LGL':'J','LGG':'Y','GLL':'B','GLG':'R','GGL':'T','GGG':'M'}
    output = ''
    for i in range(0,len(text),3):
        if len(text[i:i+3]) == 3:output += triplets.get(text[i:i+3].upper(),'')
        else:output += text[i:i+3].upper()
    return output

def FindVritham_Sanskrit(*lines,flag=0,threshold=0.5): # check poem text GL in sanskrit database
    dat = [];output = []
    if flag==0:
        for line in lines:
            if isinstance(line,tuple) or isinstance(line,list):
                for j in line:
                    dat.append(j)
            else:dat.append(line)
    elif flag==1:
        with open(lines[0],'r') as poemfile:
            for line in poemfile:
                if len(line.rstrip())>0:
                    dat.append(line.rstrip())

    x = predict()
    for line in dat:
        output.append(x.sanskritvritham(line,threshold=threshold))
    return output

def FindVritham_Bhasha(*lines,flag=0): # check poem lines in bhasha vritham
    dat = []
    if flag==0:
        for line in lines:
            if isinstance(line,tuple) or isinstance(line,list):
                for j in line:
                    dat.append(j)
            else:dat.append(line)
    elif flag==1:
        with open(lines[0],'r') as poemfile:
            for line in poemfile:
                if len(line.rstrip())>0:
                    dat.append(line.rstrip())
    else:pass
    return predict().bhashavritham(dat)

def FindVritham_Any(*lines,flag=0):
    dat = []
    if flag==0:
        for line in lines:
            if isinstance(line,tuple) or isinstance(line,list):
                for j in line:
                    dat.append(j)
            else:dat.append(line)
    elif flag==1:
        with open(lines[0],'r') as poemfile:
            for line in poemfile:
                if len(line.rstrip())>0:
                    dat.append(line.rstrip())
    else:pass
    sanskrit_output = FindVritham_Sanskrit(*dat)
    notfound = False; errortext = "വൃത്ത പ്രവചനം: കണ്ടെത്താനായില്ല (ലക്ഷണം: കണ്ടെത്താനായില്ല)"
    if isinstance(sanskrit_output,list):
        for i in sanskrit_output:
            if i==errortext:notfound = True
    else:
        if sanskrit_output==errortext:notfound = True
    if notfound:return FindVritham_Bhasha(*dat)
    else:return sanskrit_output
            

def ConvertToVaythari(line):
    string = "".join(gl(line))
    def croptext(text):
        out = []
        while len(text)>0:
            if len(text)>5:out.append(text[0:5]);text = text[5:]
            else:out.append(text);text = ""
        return out
    def splitter(text):
        o = []
        for i in text.upper():
            if i == 'G':o.append('G')
            if i == 'L':
                if len(o)>0:
                    if 'G' in o[-1]:o.append('L')
                    else:
                        if len(o[-1])>=5:o.append('L')
                        else:o[-1] += 'L'
                else:o.append('L')
        return o
    l_sounds = {'G':"ധീം",'L':"ത",'LL':"തക",'LLL':"തകിട",'LLLL':"തകധിമി",'LLLLL':"തകതകിട"}    
    if isinstance(string,list):string="".join(string)
    string = string.upper()
    output = []
    if 'G' in string:dat = splitter(string)
    else:dat = croptext(string)
    for i in dat:
        output.append(l_sounds[i])
    return " ".join(output)
    
