from fastapi import FastAPI
from pydantic import BaseModel
from logic import run_query_with_full_validation

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"message": "Chinook AI API Running 🚀"}

@app.post("/ask")
def ask(request: QueryRequest):
    response = run_query_with_full_validation(request.query)
    return {"response": response}


# ✅ Add Customer API
class Customer(BaseModel):
    first_name: str
    last_name: str

@app.post("/add_customer")
def add_customer(data: Customer):
    from step2b_connect_db import db

    db.run(f"""
        INSERT INTO Customer (FirstName, LastName)
        VALUES ('{data.first_name}', '{data.last_name}')
    """)

    return {"message": "Customer added"}