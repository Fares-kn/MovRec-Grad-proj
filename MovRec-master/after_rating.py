import torch 
import psycopg2 
import sys
print("Script started - Loading tensors...")
device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_user=151967+1
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
numeric_movie_data=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\numeric_movie_data.pt', map_location=torch.device('cpu'))
numeric_movie_data=numeric_movie_data.to(device=device)
production_countries=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\production_countries.pt', map_location=torch.device('cpu'))
production_countries=production_countries.to(device=device)
production_compaines=torch.load(r'E:\graduation-project\MovRec\data_preprocessing\toknized_tensor\production_compaines.pt', map_location=torch.device('cpu')    )
production_compaines=production_compaines.to(device=device)
connection_sting= "postgres://postgres:postgres@localhost:5432/movrec"
class Model(torch.nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.title_emb=torch.nn.Embedding(torch.max(title)+1,20)
        self.overreview_emb=torch.nn.Embedding(torch.max(overrview)+1,20)
        self.director_emb=torch.nn.Embedding(torch.max(director)+1,8)
        self.cast_emb=torch.nn.Embedding(torch.max(cast)+1,10)
        self.genre_emb=torch.nn.Embedding(torch.max(genre)+1,15)
        self.prod_comp_emb=torch.nn.Embedding(torch.max(production_compaines)+1,10)
        self.prod_count_emb=torch.nn.Embedding(torch.max(production_countries)+1,10)
        self.dropout=torch.nn.Dropout(0.2)
    def forward(self,  movie_ids):
        #because index of tokenized data start from 0 not one 
        movie_ids=movie_ids-1 
        tit=self.title_emb(title[movie_ids])
        ovrv=self.overreview_emb(overrview[movie_ids])
        dire=self.director_emb(director[movie_ids])
        ct=self.cast_emb(cast[movie_ids])
        gn=self.genre_emb(genre[movie_ids])
        pd_cmp=self.prod_comp_emb(production_compaines[movie_ids])
        pd_count=self.prod_count_emb(production_countries[movie_ids])
        num_data=numeric_movie_data[movie_ids]
        #because the diff of sequence  we must reduce the dim without lossing of data
        ovrv_vec=ovrv.mean(dim=0)
        ct_vec=ct.mean(dim=0)
        gn_vec=gn.mean(dim=0)
        pd_cmp_vec=pd_cmp.mean(dim=0)
        pd_count_vec=pd_count.mean(dim=0)
        movie=torch.cat((tit,ovrv_vec,dire,ct_vec,gn_vec,pd_cmp_vec,pd_count_vec,num_data),dim=-1)
        return movie.clone().detach().requires_grad_(True)
model=Model()
path=r"E:\graduation-project\MovRec\MovRec-master\AiModel\base_model.pth"
model.load_state_dict(torch.load(path))
model=model.to(device=device)
user_id=int(sys.argv[1])
movie_id=int(sys.argv[2])
rating=float(sys.argv[3])
with  psycopg2.connect(connection_sting) as connect:
    cursor=connect.cursor()
    query='''SELECT * FROM model.user_latent_attributes WHERE user_id=%s;'''
    cursor.execute(query,(user_id,))
    user=torch.tensor(cursor.fetchall()[0][1:],dtype=torch.float32,device=device,requires_grad=True)
    output=model(movie_id)
    result=torch.abs(torch.dot(user,output)-rating)
    result.backward()
    user_af=(user-1e-3*user.grad).tolist()
    user_af.insert(0,user_id)
    placeholders = ", ".join(["%s"] * 101)
    user=user.tolist()
    user.insert(0,user_id)
    user.insert(1,movie_id)
    cursor.execute("DELETE FROM model.user_latent_attributes_backups WHERE user_id = %s;",(user_id,))
    cursor.execute("DELETE FROM model.user_latent_attributes WHERE user_id = %s;",(user_id,) )     
    cursor.execute(f"INSERT INTO model.user_latent_attributes VALUES ({placeholders});",user_af )
    cursor.execute( f"INSERT INTO model.user_latent_attributes_backups VALUES ({placeholders+', %s'});",user)
    connect.commit()
    print("Database update completed successfully")
    print("Script finished execution")
    