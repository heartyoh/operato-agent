from rag.retriever import retrieve_relevant_dsl
from llm.query_generator import generate_graphql_query

def plan_query(user_input, llm):
    dsl_context = retrieve_relevant_dsl(user_input)
    return generate_graphql_query(dsl_context, llm)
