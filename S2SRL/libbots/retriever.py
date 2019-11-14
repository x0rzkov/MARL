# -*- coding: utf-8 -*-
import json
import string
import os
from functools import cmp_to_key
import random

class Retriever():
    def __init__(self):
        self.getDict944k()
        self.getDict944kWeak()
        self.typelist = ['Simple Question (Direct)_',
            'Verification (Boolean) (All)_',
            'Quantitative Reasoning (Count) (All)_',
            'Logical Reasoning (All)_',
            'Comparative Reasoning (Count) (All)_',
            'Quantitative Reasoning (All)_',
            'Comparative Reasoning (All)_'
            ]

    def getDict944k(self):
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("NS-CQA\\") + len("NS-CQA\\")]
        filename = os.path.abspath(rootPath + 'data\\auto_QA_data\\CSQA_result_question_type_944k.json')
        with open(filename, "r", encoding='UTF-8') as CSQA_List:
            self.dict944k = json.load(CSQA_List)

    def getDict944kWeak(self):
        curPath = os.path.abspath(os.path.dirname(__file__))
        rootPath = curPath[:curPath.find("NS-CQA\\") + len("NS-CQA\\")]
        filename = os.path.abspath(rootPath + 'data\\auto_QA_data\\CSQA_result_question_type_count944k.json')
        with open(filename, "r", encoding='UTF-8') as CSQA_List_weak:
            self.dict944k_weak = json.load(CSQA_List_weak)

    def takequestion(self, dict_item):
        takequestionvalues = list(dict_item.values())[0]
        return self.CalculatesimilarityStr(takequestionvalues, question) * (-1)

    def Retrieve(self, N, key_name, key_weak, question):
        dict_candicate = self.dict944k_weak
        if key_name in self.dict944k:
            candidate_list = self.dict944k[key_name]
            sort_candidate = sorted(candidate_list, key=self.takequestion)

            # remove the quesiton itself
            for candidateItem in sort_candidate:
                if list(candidateItem.values())[0] == question:
                    sort_candidate.remove(candidateItem)
                    break

            topNList = sort_candidate if len(sort_candidate) <= N else sort_candidate[0:N]

            # if don't have enough matches, search without relation match
            if len(topNList) < N:
                print(len(topNList), " found of ", N)
                if key_weak in dict_candicate:
                    weak_list = dict_candicate[key_weak]
                    sort_candidate_weak = sorted(weak_list, key=self.takequestion)
                    for c_weak in sort_candidate_weak:
                        if len(topNList) == N:
                            break
                        if c_weak not in topNList:
                            topNList.append(c_weak)
                            print(len(topNList))

            return topNList

    # The input of the model is constrained by the maximum number of tokens.
    # When finding top-N, it should considered whether the question in full training dateset
    # is removed from the model or not.
    def RetrieveWithMaxTokens(self, N, key_name, key_weak, question, train_data_944k):
        dict_candicate = self.dict944k_weak
        if key_name in self.dict944k and key_name in train_data_944k:
            candidate_list = self.dict944k[key_name]
            sort_candidate = sorted(candidate_list, key=self.takequestion)

            # remove the quesiton itself
            for candidateItem in sort_candidate:
                if list(candidateItem.values())[0] == question:
                    sort_candidate.remove(candidateItem)
                    break

            topNList = sort_candidate if len(sort_candidate) <= N else sort_candidate[0:N]

            # if don't have enough matches, search without relation match
            if len(topNList) < N:
                print(len(topNList), " found of ", N)
                if key_weak in dict_candicate:
                    weak_list = dict_candicate[key_weak]
                    sort_candidate_weak = sorted(weak_list, key=self.takequestion)
                    for c_weak in sort_candidate_weak:
                        if len(topNList) == N:
                            break
                        if c_weak not in topNList:
                            topNList.append(c_weak)
                            print(len(topNList))

            return topNList

    def MoreSimilarity(self, sentence1, sentence2):
        return True
        # sim1 = self.Calculatesimilarity(sentence1, question)
        # sim2 = self.Calculatesimilarity(sentence2, question)
        # # print(question, sentence1, sim1)
        # # print(question, sentence2, sim2)
        # similarity_result = sim1 > sim2
        # return similarity_result

    def Calculatesimilarity(self, sentence1, sentence2):
        trantab = str.maketrans({key: None for key in string.punctuation})
        s1 = str(sentence1.values()).translate(trantab)
        s2 = sentence2.translate(trantab)
        list1 = s1.split(' ')
        list2 = s2.split(' ')
        intersec = set(list1).intersection(set(list2))
        union = set([])
        union.update(list1)
        union.update(list2)
        jaccard = float(len(intersec)) / float(len(union)) if len(union) != 0 else 0
        return jaccard

    def CalculatesimilarityStr(self, sentence1, sentence2):
        trantab = str.maketrans({key: None for key in string.punctuation})
        s1 = sentence1.translate(trantab)
        s2 = sentence2.translate(trantab)
        list1 = s1.split(' ')
        list2 = s2.split(' ')
        intersec = set(list1).intersection(set(list2))
        union = set([])
        union.update(list1)
        union.update(list2)
        jaccard = float(len(intersec)) / float(len(union)) if len(union) != 0 else 0
        return jaccard

    def AnalyzeQuestion(self, question_info):
        entity_count = len(question_info.value['entity'])
        relation_count = len(question_info.value['relation'])
        type_count = len(question_info.value['type'])
        question = question_info.value['question']
        relation_list = question_info.value['relation']
        relation_str = '_'.join(relation_list)
        key_name = '{0}{1}_{2}_{3}_{4}'.format(type_name, entity_count, relation_count, type_count,
                                               relation_str)
        key_weak = '{0}{1}_{2}_{3}'.format(type_name, entity_count, relation_count, type_count)
        return key_name, key_weak, question

if __name__ == "__main__":
    retriever = Retriever()
    result_dict = {}
    with open("RL_train_TR.question", "r", encoding='UTF-8') as questions:
        load_dict = json.load(questions)
        # keys = list(load_dict.keys())
        # random.shuffle(keys)
        #
        # shuffled_load_dict = dict()
        # for key in keys:
        #     shuffled_load_dict.update({key: load_dict[key]})

        q_topK_map = {}

        current_type = 0

        for i in range(0, 6):
            current_type = i
            current_type_count = 0
            # for key, value in shuffled_load_dict.items():
            for key, value in load_dict.items():
                entity_count = len(value['entity'])
                relation_count = len(value['relation'])
                type_count = len(value['type'])
                question = value['question']
                relation_list = value['relation']
                relation_str = '_'.join(relation_list)

                type_name = retriever.typelist[0]
                for typei in retriever.typelist:
                    if typei in key:
                        type_name = typei
                if type_name == retriever.typelist[current_type]:
                    current_type_count += 1

                    if current_type_count >= 20:
                        break
                    else:
                        key_name = '{0}{1}_{2}_{3}_{4}'.format(type_name, entity_count, relation_count, type_count,
                                                               relation_str)
                        key_weak = '{0}{1}_{2}_{3}'.format(type_name, entity_count, relation_count, type_count)

                        topNlist = retriever.Retrieve(5, key_name, key_weak, question)
                        if True:
                            # current_type_count += 1
                            key_question = key + ' : ' + question
                            item_key = {key_question: topNlist}
                            q_topK_map.update(item_key)


        with open('top5_4weak11.13.json', 'w', encoding='utf-8') as f:
            json.dump(q_topK_map, f, indent=4)


