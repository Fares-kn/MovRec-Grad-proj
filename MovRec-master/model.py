import torch
import sys
import psycopg2
from sortedcontainers import SortedList
connection_sting= "postgres://postgres:postgres@localhost:5432/movrec"
device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
title=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\title.pt', map_location=torch.device('cpu'))
title=title.to(device=device)
cast=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\cast.pt', map_location=torch.device('cpu'))
cast=cast.to(device=device)
director=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\director.pt', map_location=torch.device('cpu'))
director=director.to(device=device)
genre=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\genre.pt', map_location=torch.device('cpu'))
genre=genre.to(device=device)
overrview=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\overrview.pt', map_location=torch.device('cpu'))
overrview=overrview.to(device=device)
numeric_movie_data=torch.load(r'E:\MovRec-Initial\MovRec\MovRec\toknized_tensor\numeric_movie_data.pt', map_location=torch.device('cpu'))
numeric_movie_data=numeric_movie_data.to(device=device)
production_countries=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\production_countries.pt', map_location=torch.device('cpu'))
production_countries=production_countries.to(device=device)
production_compaines=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\production_compaines.pt', map_location=torch.device('cpu')    )
production_compaines=production_compaines.to(device=device)
class FinalModel(torch.nn.Module):
    def __init__(self,in_out_list:list,activation):
        super().__init__()
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,20)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,20)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,8)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,10)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,15)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,10)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,10)
        self.layers=torch.nn.ModuleList() 
        in_f=100
        for idx,out_f in enumerate(in_out_list):
            self.layers.append(torch.nn.Linear(in_f,out_f))
            if (idx+1)%3==0:
                self.layers.append(torch.batch_norm())
            self.layers.append(activation)
            in_f=out_f
        self.output=torch.nn.Linear(in_out_list[-1],1)
        self.model=torch.nn.Sequential(*self.layers)
    def forward(self,user,movie_ids):
        movie_ids=movie_ids-1 
        tit=self.title_emb(title[movie_ids])
        ovrv=self.overreview_emb(overrview[movie_ids])
        dire=self.director_emb(director[movie_ids])
        ct=self.cast_emb(cast[movie_ids])
        gn=self.genre_emb(genre[movie_ids])
        pd_cmp=self.prod_comp_emb(production_compaines[movie_ids])
        pd_count=self.prod_count_emb(production_countries[movie_ids])
        ovrv_vec=ovrv.mean(dim=0)
        ct_vec=ct.mean(dim=0)
        gn_vec=gn.mean(dim=0)
        pd_cmp_vec=pd_cmp.mean(dim=0)
        pd_count_vec=pd_count.mean(dim=0) 
        num_data=numeric_movie_data[movie_ids]
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        result=movie*user
        x=self.model(result)
        x=self.output(x)
        return x.squeeze()
model=FinalModel([256,128],torch.nn.ReLU())
path=r'E:\MovRec-Initial\MovRec\MovRec\AiModel\model.pth'
model.load_state_dict(torch.load(path))
model=model.to(device=device)
user_id=int(sys.argv[1])
with torch.inference_mode():
    with psycopg2.connect(connection_sting) as connect:
        cursor=connect.cursor()
        query='''SELECT * FROM model.user_latent_attributes WHERE user_id=%s;'''
        cursor.execute(query,(user_id,))
        user=torch.tensor(cursor.fetchall()[0][1:],dtype=torch.float32,device=device)
        query='''SELECT movie_id FROM movies WHERE movie_id not in(SELECT movie_id FROM watch_events  WHERE user_id=%s UNION SELECT movie_id FROM model.user_recommendation WHERE user_id=%s )'''
        cursor.execute(query,(user_id,user_id))
        movie_ids = [row[0] for row in cursor.fetchall()]
        movie_list=SortedList()
        for i in movie_ids:
            result=model(user,i)
            if result >=3.0:
                movie_list.add((float(result),i))
        i=len(movie_list)-1
        if i+1>35:
            query='''DELETE FROM  model.model_recommendation WHERE user_id=%s'''
            cursor.execute(query,(user_id,))
    
        stop=i-150
        while i>stop and i>=0:
            try:
                query='''insert into model.model_recommendation VALUES(%s,%s,%s)'''
                cursor.execute(query,(user_id,movie_list[i][1],movie_list[i][0]))
            except IndexError as e:
                print(i,e)
                break
            i-=1

            