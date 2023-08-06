import requests
import json
import aiohttp

__methods__=[
    'get',
    'get_sort',
    'insert_one',
    'insert_many',
    'create_data',
    'delete_data',
    'database'
]

class kiroEror(Exception):
    def __init__(self,message):
        super().__init__(message)
        
class Connect():
    def __init__(self,token,cluster):
        self.token=token
        self.cluster=cluster
        self.server = f"https://kirodb.herokuapp.com/auth/{self.token}"
        data={'method':'get'}
        clusters = requests.post(self.server, data=json.dumps(data)).json()['clust']
        clustdata=[]
        for clust in clusters:
            clustdata.append(str(clusters[clust]))
            
        if str(self.cluster) in clustdata:
            pass
        else:
            raise kiroEror('Cluster not found')
            return
    
    async def get(self,key='none'):
        respond={
            "method": "look",
            "argument": "get",
            "data": {
                "key": key
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
        
    async def get_sort(self,key='none',reverse=True):
        if reverse==True:
            reverse='1'
        elif reverse==False:
            reverse='0'
        respond={
            "method": "look",
            "argument": "get_sort",
            "data": {
                "key": key,
                "reverse": reverse
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
        
    async def insert_one(self,id='none',key='none',data='none',method='r'):
        respond={
            "method": "change",
            "argument": "insert_one",
            "data": {
                "id": id,
                "key": key,
                "data": data,
                "method": method
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
    
    async def insert_many(self,id='none',data='none'):
        respond={
            "method": "change",
            "argument": "insert_many",
            "data": {
                "id": id,
                "data": data
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
    
    async def create_data(self,id='none',data='none'):
        respond={
            "method": "change",
            "argument": "create_data",
            "data": {
                "id": id,
                "data": data
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
    
    async def delete_data(self,id='none'):
        respond={
            "method": "change",
            "argument": "delete_data",
            "data": {
                "id": id
            },
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
    
    async def cluster_info(self):
        respond={
            "method": "look",
            "argument": "cluster_info",
            "clust": self.cluster,
            "token": self.token
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.server,
                        data=json.dumps(respond)) as resp:
                return await resp.json()
                
