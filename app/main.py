from fastapi import FastAPI, HTTPException, status
from .schemas import Client, ClientPublic, ClientList
from bson import ObjectId
from .database import db

app = FastAPI()

client_collection = db['clients'] 

def str_object_id(obj):
    if isinstance(obj,ObjectId):
        return str(obj)
    return obj

def get_next_id():
    last_client = client_collection.find_one(sort=[("id", -1)])
    return (last_client['id'] + 1) if last_client else 0

@app.post('/clients', status_code=status.HTTP_201_CREATED, response_model=ClientPublic)
def create_client(client: Client):
    result = client_collection.insert_one(client.model_dump())
    client_data = client.model_dump()    
    client_data['id'] = str_object_id(result.inserted_id)
    return client_data

@app.get('/clients', response_model=ClientList)    
def read_client():
    client_cursor = client_collection.find()
    clients = []

    for client in client_cursor:
        client_data = client
        client_data['id'] = str_object_id(client['_id'])
        clients.append(client_data)

    return {'clients': clients}


@app.get('/clients/{client_id}', response_model=ClientPublic)
def get_client(client_id: str):
    try:
        object_id = ObjectId(client_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid client_id format'
        )
    client = client_collection.find_one({'_id': object_id})

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Client with id {client_id} not found'
        )

    client['id'] = str(client.pop('_id'))
    return client



@app.put('/clients/{client_id}', response_model=ClientPublic)
def update_client(client_id: str, client: Client):
    try:
       object_id = ObjectId(client_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'invalid Client format: {client_id}'
        )
    
    existing_client = client_collection.find_one({'_id': object_id})

    if not existing_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )

    updated_client_data = client.model_dump(exclude_unset=True)

    client_collection.update_one(
        {'_id': object_id},
        {'$set': updated_client_data}
    )

    updated_client = client_collection.find_one({'_id': object_id})
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to retrieve the updated client'
        )
    
    updated_client['id'] = str(updated_client.pop('_id'))

    return updated_client


@app.delete('/clients/{client_id}', status_code=status.HTTP_200_OK)
def delete_client(client_id: str):
    try:
        object_id = ObjectId(client_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid client id format'
        )
    
    result = client_collection.delete_one({'_id': object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Client with id {client_id} not found'
        )
    
    return {"detail": "Client deleted successfully"}
    