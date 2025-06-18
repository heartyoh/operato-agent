from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent.planner import plan_query
from agent.executor import execute_query
from llm.llm_client import load_llm

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QueryRequest):
    llm = load_llm()
    planned_query = plan_query(request.question, llm)
    result = execute_query(planned_query)
    return {"result": result}
