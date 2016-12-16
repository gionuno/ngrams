#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 19:45:00 2016

@author: quien
"""
import io;
import re;
import os;

import glob;
import string;

import numpy as np;
import numpy.random as rd;

import matplotlib.pyplot as plt;

def cleantxt(T,spaces):
    regex = re.compile("[%s]"%re.escape(string.punctuation+string.digits));
    aux = regex.sub("",T);
    return re.sub("\s+"," " if spaces else "",aux).strip().lower();

def txt2num(T):
    idx  = 0;
    A = [];
    for idx in range(len(T)):
        if 'a' <= T[idx] <= 'z':
            A.append(ord(T[idx])-ord('a'));
        elif T[idx] == ' ':
            A.append(26);
    return np.array(A);

def getidxmat(n):
    return  np.array([np.r_[np.power(27,np.arange(i,-1,-1)),np.zeros(n-i-1,dtype=int)] for i in range(n)]);
 
def getfromidx(i):
    a = "";
    while True:
        if i % 27 == 26:
            a = ' ' + a;
        else:
            a = chr(i%27+ord('a')) + a;
        i = i / 27;
        if i == 0:
            break;
    return a;

def getfromstr(s):
    i = 0;
    for a in s:
        i *= 27;
        if a == ' ':
            i += 26;
        else:
            i += ord(a)-ord('a');
    return i;

class ngrams:
    def __init__(self,n):
        self.n = n;
        self.P = [np.zeros(27**n_) for n_ in range(1,self.n+1)];
        self.idx_mat = getidxmat(self.n);
    def calculate(self,x):
        for idx in range(len(x)):
            print 'book num: ',idx,x[idx].shape;
            for jdx in range(x[idx].shape[0]):
                aux = x[idx][jdx:jdx+self.n];
                aux_kdx = np.dot(self.idx_mat[0:len(aux),0:len(aux)],aux);
                for kdx in range(len(aux_kdx)):
                    self.P[kdx][aux_kdx[kdx]] += 1.0;
        for kdx in range(self.n):
            self.P[kdx] /= np.sum(self.P[kdx]);

books = glob.glob("books/*.txt");
text = [];
nums = [];
for book in books:
    print book;
    with io.open(book,'r') as file_:
        b = file_.read().encode('ascii','ignore');
        t = cleantxt(b,True);
        text.append(t);
        nums.append(txt2num(t));

s = [a for a in string.ascii_lowercase+' '];

def entropy(p):
    aux = p[p>0.];
    return -np.dot(aux,np.log2(aux));

print 'Calculating 1,2,3,4,5-grams with spaces';
grams = ngrams(5);
grams.calculate(nums);
print 'Done';

'''
Checar que pedo con letras solas
'''
p_ = np.copy(grams.P[0]);
p_ /= np.sum(p_);
h_1 = entropy(p_);
print "H( p(x) ):",h_1;
plt.bar(np.arange(27),p_),
plt.xticks(0.5+np.arange(27),s);

'''
Checar que pedo con pares de letras xy.
'''
p_ = np.copy(grams.P[1]).reshape((27,27)).T;
h_2 = entropy(p_);
print "H( p(x,y) ):",h_2;
plt.imshow(p_,interpolation='nearest'),
plt.xticks(np.arange(27),s),
plt.yticks(np.arange(27),s);

'''
Checar que pedo q* y *u, donde * es cualquier letra
'''

idx = getfromstr('q'); # s = q*
p_ = np.copy(grams.P[1][27*idx:27*idx+27]);
p_ /= np.sum(p_);
h_y = entropy(p_);
print "H( p(y|x='q') ):",h_y;
plt.bar(np.arange(27),p_),
plt.xticks(0.5+np.arange(27),s);

idx = getfromstr('u'); # s = *u
p_ = np.copy(grams.P[1][idx::27]);
p_ /= np.sum(p_);
h_x = entropy(p_);
print "H( p(x|y='u') ):",h_x;
plt.bar(np.arange(27),p_),
plt.xticks(0.5+np.arange(27),s);

'''
Juego de Shannon con 4 gramas
'''

S = 'in the beginning';
p = grams.P[4];
for idx in range(1000):
    jdx = getfromstr(S[-4:]);
    p_ = np.copy(p[27*jdx:27*jdx+27]);
    p_ /= np.sum(p_);
    aux = rd.choice(27,1,p=p_)[0];
    S += s[aux];
print S;

with io.open('test.txt','w') as f:
    f.write(unicode(S));
