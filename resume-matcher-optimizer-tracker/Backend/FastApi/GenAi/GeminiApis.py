import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from typing import List
import google.generativeai as genai
api_key = os.environ.get("GOOGLE_API_KEY")

# Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.3)

class aiResponse(BaseModel):
    aiFeedback: List[str] = Field(
        ..., 
        description="What changes need to be done in resume. Maximum 15 points."
    )
    score: int = Field(
        ..., 
        description="Score of resume and job description compatibility between 1 and 100"
    )
def getMatchedResponse(text: str, jd: str) -> dict:
    try:
        parser = PydanticOutputParser(pydantic_object=aiResponse)
        prompt = PromptTemplate(
            template="""
You are an expert resume reviewer. Compare the following resume with the job description.

Resume:
{text}

Job Description:
{jd}

Provide:
1. Up to 15 specific improvement suggestions as a JSON array of strings under "aiFeedback" without using ~ symbol anywhere.
2. A compatibility score between 1 and 100 under "score".

{format_instructions}
""",
            input_variables=["text", "jd"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        _input = prompt.format_prompt(text=text, jd=jd)
        output = llm.invoke(_input.to_messages())
        parsed = parser.parse(output.content)

        return parsed.dict()

    except Exception as error:
        print(f"Error in getMatchedResponse: {error}")
        return {
            "aiFeedback": ["something went wrong"],
            "score": -1
        }

genai.configure(api_key=api_key)
def getEmbedding(text: str):
    # Call Gemini's embedding model
    response = genai.embed_content(
        model="gemini-embedding-001",  # Gemini embedding model
        content=text
    )
    
    # Extract the embedding vector
    embedding = response["embedding"]
    return embedding

