from threading import local
import scipy.spatial
import numpy as np
import os, json
import glob
import re
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from tokenizers import Tokenizer
from datetime import datetime
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from sklearn.metrics import classification_report
from sklearn.metrics import multilabel_confusion_matrix

torch.manual_seed(1)
import pandas as pd
import torch
import random
import itertools
# import pickle
import time
import pickle5 as pickle

start = time.time()

class patent_classification:
    def __init__(self, num_test, test_csv_path, train_csv_path, test_embed_path, train_embed_path):
        self.num_test = num_test
        self.test_csv_path = test_csv_path
        self.train_csv_path = train_csv_path
        self.test_embed_path = test_embed_path
        self.train_embed_path = train_embed_path
        self.F1Measure_list = []
        self.Recall_list = []
        self.Accuracy_list = []
        self.Precision_list = []
        self.Hamming_Loss_list = []

    def read_embeddings(self):
        #Load sentences & embeddings from disc
        with open(self.test_embed_path, "rb") as fIn:
            stored_data = pickle.load(fIn)
            stored_patent_test_embeddings_id = stored_data['patent_id']
            test_embeddings = stored_data['claim_embeddings']
        
        with open(self.train_embed_path, "rb") as fIn:
            stored_data = pickle.load(fIn)
            stored_patent_train_embeddings_id = stored_data['patent_id']
            claim_embeddings = stored_data['claim_embeddings']
        return stored_patent_test_embeddings_id, test_embeddings, stored_patent_train_embeddings_id, claim_embeddings

# test_embeddings = torch.load('/home/ubuntu/storage_data/df_claim_test_133_n.pkl', map_location=torch.device('cpu'))
# claim_embeddings = torch.load('/home/ubuntu/storage_data/df_claim_train_133_n.pkl', map_location=torch.device('cpu'))


    def get_top_n_similar_patents_df(self, new_claim, claim_embeddings, stored_patent_train_embeddings_id):
        search_hits_list = []
        search_hits = util.semantic_search(new_claim, claim_embeddings, 10000, 5000000, 20)
    #     # embedder = SentenceTransformer('bert-base-nli-stsb-mean-tokens')
    #     embedder = SentenceTransformer('/home/ubuntu/deeppatentsimilarity/results/stsb_augsbert_SS_roberta-base-2021-01-06_22-14-54')
    # #     embedder = SentenceTransformer('roberta-base-nli-stsb-mean-tokens')
    # #     embedder = SentenceTransformer('/home/ubuntu/deeppatentsimilarity/results/stsb_augsbert_SS_roberta-base-2021-01-06_22-14-54/')
    # #     query_embeddings = embedder.encode([new_claim])
    #     query_embeddings = new_claim
        
    # #     query_embeddings = torch.load('/home/ubuntu/deeppatentsimilarity/patentdata/claim_embeddings_24_AugSBERT_test.pt', map_location=torch.device('cpu'))
    
    # #     query_embeddings = tokenizer([new_claim], padding=True, truncation=True, max_length=128, return_tensors='pt')
    
    #     # list of patent claims
    # #     claim_embeddings = embedder.encode(claims)
    # #     claim_embeddings = torch.load('/home/ubuntu/deeppatentsimilarity/patentdata/claim_embeddings_24_AugSBERT.pt', map_location=torch.device('cpu'))
    
    
    #     # get top 100 patent claims based on cosine similarity
    #     top_n = 40
    #     distances = scipy.spatial.distance.cdist(query_embeddings, claim_embeddings, "cosine")[0]
    # #     distances = sentence_transformers.util.semantic_search(query_embeddings, claim_embeddings, "cosine")[0]
    
    #     results = zip(range(len(distances)), distances)
    #     results = sorted(results, key=lambda x: x[1])
    
        # save similar patents info
        top_claim_order = []
        top_claim_ids = []
        top_similarity_scores = []
        
    #     # print('New_claim: ' + new_claim + '\n')
    
    #     # Find the closest 100 patent claims for each new_claim based on cosine similarity
    #     for idx, distance in results[0:top_n]:
    #         top_claim_ids.append(patent_id[idx])
    #         top_claims.append(claims[idx])
    #         top_similarity_scores.append(round((1-distance), 4))
    # #         print('Patent ID: ' + str(patent_id[idx]))
    # #         print('PubMed Claim: ' + claims[idx])
    # #         print('Similarity Score: ' + "%.4f" % (1-distance))
    # #         print('\n')
            
        for item in range(len(search_hits[0])):
            top_claim_order = search_hits[0][item].get('corpus_id')
            top_claim_ids.append(stored_patent_train_embeddings_id[top_claim_order])
            top_similarity_scores.append(search_hits[0][item].get('score'))
            
        top_100_similar_patents_df = pd.DataFrame({
            'top_claim_ids': top_claim_ids,
            'cosine_similarity': top_similarity_scores,
    #         'claims': top_claims,
        })
    
            
        
        return top_100_similar_patents_df
    
    def F1Measure(self, results, y_true, y_pred):
        save_F1 = []
        temp = 0
        for i in range(y_true.shape[0]):
            if (sum(y_true[i]) == 0) and (sum(y_pred[i]) == 0):
                continue
            temp_save = (2*sum(np.logical_and(y_true[i], y_pred[i])))/ (sum(y_true[i])+sum(y_pred[i]))
            save_F1.append(temp_save)
            temp += temp_save
    
        save_F1 = pd.DataFrame(save_F1)
        save_F1_ids = pd.concat([results, save_F1], axis=1, ignore_index=True)
        f1score = temp/ y_true.shape[0]
        # if f1score > 0.46:
        #     save_F1_ids.to_csv(r'/home/ubuntu/storage_data_new/output/221121/section_output_save_F1'+'-'+str(k)+'-'+str(f1score)+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.csv', index = False)
        #     #write string to file
        #     multilabel_confusion = multilabel_confusion_matrix(y_true, y_pred)
        #     output = open('/home/ubuntu/storage_data_new/output/221121/section_multilabel_confusion'+'-'+str(k)+'-'+str(f1score)+'-'+'.pkl', 'wb')
        #     pickle.dump(multilabel_confusion, output)
        #     output.close()
        #     label_names = self.df_claim_cpc_test.columns[6:].to_list()
        #     #open text file
        #     text_file = open(r'/home/ubuntu/storage_data_new/output/221121/section_report_F1'+'-'+str(k)+'-'+str(f1score)+'-'+'.txt', "w")
        #     #write string to file
        #     results_a = classification_report(y_true, y_pred,target_names=label_names)
        #     n = text_file.write(results_a)
        #     #close file
        #     text_file.close()
            
        return temp/ y_true.shape[0]
    
    def Recall(self, y_true, y_pred):
        temp = 0
        for i in range(y_true.shape[0]):
            if sum(y_pred[i]) == 0:
                continue
            temp+= sum(np.logical_and(y_true[i], y_pred[i]))/ sum(y_pred[i])
        return temp/ y_true.shape[0]
    
    def Precision(self, y_true, y_pred):
        temp = 0
        for i in range(y_true.shape[0]):
            if sum(y_true[i]) == 0:
                continue
            temp+= sum(np.logical_and(y_true[i], y_pred[i]))/ sum(y_true[i])
        return temp/ y_true.shape[0]
    
    def Hamming_Loss(self, y_true, y_pred):
        temp=0
        for i in range(y_true.shape[0]):
            temp += np.size(y_true[i] == y_pred[i]) - np.count_nonzero(y_true[i] == y_pred[i])
        return temp/(y_true.shape[0] * y_true.shape[1])
    
    def Accuracy(self, y_true, y_pred):
        temp = 0
        for i in range(y_true.shape[0]):
            temp += sum(np.logical_and(y_true[i], y_pred[i])) / sum(np.logical_or(y_true[i], y_pred[i]))
        return temp / y_true.shape[0]
    
    def read_csv_files(self):
        df_claim_cpc_test = pd.read_csv(self.test_csv_path, encoding='ISO-8859-1')
        df_claim_cpc_train = pd.read_csv(self.train_csv_path, encoding='ISO-8859-1')
        return df_claim_cpc_test, df_claim_cpc_train

    def patent_classification_knn(self):
        stored_patent_test_embeddings_id, test_embeddings, stored_patent_train_embeddings_id, claim_embeddings = self.read_embeddings()

        df_claim_cpc_test, df_claim_cpc_train = self.read_csv_files()

        claims = list(df_claim_cpc_train.text)
        patent_id = list(df_claim_cpc_train.id)
        
        listofpredictdfs = []
        
        start = time.time()
        df=pd.DataFrame()
        for i in range(len(df_claim_cpc_test[:self.num_test])):
            get_top_n_similar_patents_df_predict = self.get_top_n_similar_patents_df(np.array(test_embeddings[i]).reshape(1,-1), claim_embeddings, stored_patent_train_embeddings_id)
            result = pd.merge(get_top_n_similar_patents_df_predict, df_claim_cpc_train, left_on='top_claim_ids',right_on='id',how='left',suffixes=('_left','_right'))
            # df = df.append(result,ignore_index=True)
            globals()["predict_n"+str(i)] = result.copy()
            listofpredictdfs.append("predict_n"+str(i))
        df = pd.concat(map(lambda x: eval(x), listofpredictdfs),keys= listofpredictdfs ,axis=0)
       
        top_k = 10
        for k in range(top_k):
            top_n = k 
            predict = pd.DataFrame(columns= df_claim_cpc_test.columns[6:])
            for item in range(len(listofpredictdfs)):
                k_similar_patents = df.xs(listofpredictdfs[item]).nlargest(top_n, ['cosine_similarity'])
                result_k_similar_patents = pd.DataFrame(0, index=np.arange(1),columns= k_similar_patents.columns[8:])
                for i in range(top_n):
                    result_k_similar_patents  = result_k_similar_patents + k_similar_patents.iloc[i, 8:].values
            #     result_k_similar_patents_r = result_k_similar_patents.reshape(1,600)
                result_k_similar_patents_df = pd.DataFrame(result_k_similar_patents, columns= k_similar_patents.columns[8:])
        #     patent_id_input_res = pd.concat([input_patrnt_id_df, result_k_similar_patents], ignore_index=True)
                result_k_similar_patents_df.insert(0, "input_aptent_id", df_claim_cpc_test.id.iloc[item], True)
                locals()["predict"+str(item)] = result_k_similar_patents_df.copy()
                predict = pd.concat([predict, locals()["predict"+str(item)]], ignore_index=True)
                result_k_similar_patents_df = result_k_similar_patents_df[0:0]
        # predict.to_csv(r'/home/ubuntu/deeppatentsimilarity/output/new_predict_result.csv'+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), index = False)
        # creating tensor from targets_df
        #     predict = pd.read_csv('/home/ubuntu/deeppatentsimilarity/output/Multilabel17000.csv', encoding='ISO-8859-1')
            data = torch.tensor((predict.to_numpy()).astype(float), dtype=torch.float32)
        # printing out result
        # print(torch_tensor)
            m = nn.Sigmoid()
            
        # input = torch.randn(2)
            output = m(data)
            output = (output>0.9).float()
            output_df = pd.DataFrame(output, columns=predict.columns).astype(float)
            
            y_pred = output_df.iloc[:, :-1].to_numpy()
            y_true = df_claim_cpc_test.iloc[:self.num_test, 6:].to_numpy()
            results = pd.concat([output_df, df_claim_cpc_test], axis=1, ignore_index=True)
        #     result.to_csv(r'/home/ubuntu/storage_data/output/new_predict_result'+str(k)+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.csv', index = False)


            
            
            self.F1Measure_list.append(self.F1Measure(results, y_true,y_pred))
            self.Recall_list.append(self.Recall(y_true,y_pred))
            self.Accuracy_list.append(self.Accuracy(y_true, y_pred))
            self.Precision_list.append(self.Precision(y_true,y_pred))
            self.Hamming_Loss_list.append(self.Hamming_Loss(y_true, y_pred))
            
            end = time.time()
            # print(f"Runtime of the program is {end - start}")
            # print("F1Measure: ", self.F1Measure_list[top_n])
            # print("Recall: ", self.Recall_list[top_n])
            # print("Accuracy: ", self.Accuracy_list[top_n])
            # print("Precision: ", self.Precision_list[top_n])
            # print("Hamming_Loss: ", self.Hamming_Loss_list[top_n])
            output_d_metrics = {'F1Measure':self.F1Measure_list,'Recall_list':self.Recall_list, 'Accuracy_list':self.Accuracy_list,'Precision_list':self.Precision_list,'Hamming_Loss_list':self.Hamming_Loss_list}
            output_df_metrics = pd.DataFrame(output_d_metrics)

        return output_df_metrics
            
# output_df_metrics.to_csv(r'/home/ubuntu/storage_data_new/output/221121/section_df_all_metrics'+'-'+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+'.csv', index = False)