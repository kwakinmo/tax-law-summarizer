# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
# from konlpy.tag import Twitter
import pandas as pd
import re


def preprocess(filename):

    data_csv = pd.read_csv(filename + '.csv', encoding='euc-kr', engine='python')
    column_list = data_csv.columns.values.tolist()
    raw_data_series = pd.Series()
    for column_name in column_list:
        if column_name.find('내용') != -1:  # generalize 덜 함.
            raw_data_series = data_csv[column_name]
    preprocess_data = []

    if '별' in filename:
        for raw_data in raw_data_series:
            replaced_data = BeautifulSoup(raw_data, 'lxml').text.replace('&#x0D', ' ').replace('\xa0', ' ').\
                replace('\u3000', ' ').replace('✽', ' ').replace('\t', ' ')
            replaced_data = re.sub("<.*?>", "", replaced_data)
            preprocess_data.append(' '.join(replaced_data.split()))
            preprocess_data = list(filter(None, preprocess_data))
    else:
        for raw_data in raw_data_series:
            contents = BeautifulSoup(raw_data, 'lxml').find_all(["p", "div"],
                                                    {'class': re.compile('.*content.*|.*bg.*inner.*')})
            for i in range(len(contents)):
                preprocess_data.append(' '.join(contents[i].text.replace('&#x0D', ' ').replace('\xa0', ' ')
                                                .replace('\u3000', ' ').replace('✽',' ').replace('\t', ' ').split()))
            preprocess_data = list(filter(None, preprocess_data))

    return preprocess_data


def split_into_sentences(text):

    prefixes = "(1|2|3|4|5|6|7|8|9|0|www|가|나|라|마|바|사|아|자)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    websites = "[.](com|net|org|io|gov|co|go|kr)"

    text = " " + text + "  "
    text = text.replace("\n", " ")
    text = re.sub(prefixes, "\\1<prd>", text)
    text = re.sub(websites, "<prd>\\1", text)
    text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
    if "”" in text: text = text.replace(".”", "”.")
    if "\"" in text: text = text.replace(".\"", "\".")
    if "!" in text: text = text.replace("!\"", "\"!")
    if "?" in text: text = text.replace("?\"", "\"?")
    text = text.replace(".", ".<stop>")
    text = text.replace("?", "?<stop>")
    text = text.replace("!", "!<stop>")
    text = text.replace("<prd>", ".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]

    return sentences


def data2sentence(data):

    sentences_set = set()
    for k in range(len(data)):
        sentences = split_into_sentences(data[k])
        for j in range(len(sentences)):
            sentences_set.add(sentences[j])

    return sentences_set


def keyword_matching(sentence_set, keywords):
    # twitter = Twitter()
    match_data = set()

    for sentence in sentence_set:
        # morphed = []
        # morphed = twitter.morphs(sentence)
        for i in range(len(keywords)):
            if keywords[i] not in sentence: # morphed
                break
            elif i == len(keywords) - 1:
                match_data.add(sentence)
            else:
                continue

    return match_data


def data2file(data,filename):

    file = open(filename + '_matched_Data.txt', 'w', encoding='UTF8')
    for item in data:
        file.write("%s\n" % item)

    return


if __name__ == '__main__':
    keywords = ['상속세', '증여세']
    filename = '월간조세(id,제목,내용,등록일자,게시자)_20180427'
    preprocessed_data = preprocess(filename)
    data2sen = data2sentence(preprocessed_data)
    matched_data = keyword_matching(data2sen, keywords)
    data2file(matched_data, filename)