#!/usr/bin/env python3
import source.libs.define as lib
# Only a small number of simple methods will be here, use scipy.stats for others.

def percentile(data, percentile):
    # http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
    import math
    data = sorted(data)
    k = (len(data)-1) * percentile/100
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    d0 =data[int(f)] * (c-k)
    d1 = data[int(c)] * (k-f)
    return d0+d1


def median(data):
    data = sorted(data)
    if len(data) % 2 == 0:
        return (data[int(len(data)/2)-1] + data[int(len(data)/2)]) / 2
    else:
        return data[int(len(data)/2)]

def mean(data):
    return sum(data)/max(len(data), 1)


def iqr(data):
    return percentile(data, 75) - percentile(data, 25)


def outliers(data, upper=True, lower=False):
    result = []
    iq = iqr(data)
    if upper:
        result += [x for x in data if x > (percentile(data, 75) + iq)]
    if lower:
        result += [x for x in data if x < (percentile(data, 25) - iq)]
    return result



# The Chi-squared Statistic is a measure of how similar two categorical probability distributions are. 
# If the two distributions are identical, the chi-squared statistic is 0, if the distributions are very
# different, some higher number will result.
def chi_square(C, E):
    # C[x] = count of item x
    # E[x] = expected count of item x
    result = 0
    for i in C:
        if i not in E:
            continue
        result += (C[i] - E[i]) ** 2 / E[i]
    # TODO should return anything else?
    return {'value' : result}


# The index of coincidence is a measure of how similar a frequency distribution is to the uniform 
# distribution. The I.C. of a piece of text does not change if the text is enciphered with 
# a substitution cipher. 
# Keysize allows to involve every n-th character, which can beat Vinegere and similar ciphers
def index_of_coincidence(text, keysize=1, alphabet='abcdefghijklmnopqrstuvwxyz'):
    if keysize == 0:
        return 0
    text = ''.join([x for x in text if alphabet is None or x in alphabet])
    # prepare test strings based on keysize
    texts = []
    for i in range(0, keysize):
        texts.append(text[i::keysize])
    result = 0
    for text in texts:
        
        N = len(text) # number of characters
        # get frequencies of letters in text
        n = {}
        for x in text:
            if x not in n:
                n[x] = 1
            else:
                n[x] += 1
        summ = sum([n[x]*(n[x]-1) for x in n])
        if N != 0 and N != 1:
            result += summ*len(alphabet)/(N*(N-1))
    return result/len(texts)

