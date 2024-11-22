from pydantic import BaseModel
from typing import List
  
class Client(BaseModel):
    first_name: str
    last_name: str
    password: str
    age: int 
    cpf: str
    origin_city: str

class ClientPublic(BaseModel):
    id: str
    first_name: str
    last_name: str
    age: int 
    cpf: str
    origin_city: str

class ClientList(BaseModel):
     clients: List[ClientPublic]
