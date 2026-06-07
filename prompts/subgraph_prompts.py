# prompts/subgraph_prompts.py

DOC_GRADER_PROMPT = """You are an elite QA Engineer evaluating the direct relevance of a retrieved document chunk to a user's technical query.

User Query: {query}
Retrieved Code/Document Chunk: {document}

Grading Metric:
- If the document contains any technical concepts, context, configuration parameters, or specifications directly useful for answering the user's query, grade it as 'yes'.
- If it is completely detached from the user's intent or unrelated code noise, grade it as 'no'.

Your output must be a single structured decision block without conversational text.
"""

HALLUCINATION_PROMPT = """You are a rigorous code verification assistant assessing whether an LLM generation is strictly supported by the provided source context blocks.

Retrieved Ground Truth Assets:
{context}

Generated Assistant Response:
{generation}

Grading Metric:
- If every statement, requirement, and technical specification in the Generated Response is directly supported by the Ground Truth Assets, grade it as 'yes'.
- If the response introduces unverified external assertions, assumptions, or hallucinations not present in the context, grade it as 'no'.

Your output must be a single structured decision block without conversational text.
"""