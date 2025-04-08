from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class PaperQualification(BaseModel):
    is_relevant: bool = Field(description="Whether the paper is relevant to consumer behavior and persuasion")
    topics_found: List[str] = Field(description="List of relevant topics found in the paper")
    confidence: float = Field(description="Confidence score between 0 and 1")
    reasoning: str = Field(description="Brief explanation of why the paper is or isn't relevant")

def qualify_paper(text: str, llm: ChatOpenAI) -> bool:
    """Qualify a paper by checking if it deals with topics of consumer behavior and persuasion.
    
    Args:
        text (str): The text content of the paper
        llm (ChatOpenAI): The language model to use for analysis
        
    Returns:
        bool: True if the paper is relevant, False otherwise
    """
    # Create parser for structured output
    parser = PydanticOutputParser(pydantic_object=PaperQualification)
    
    # Create prompt template
    prompt = f"""Analyze the following academic paper text and determine if it's relevant to consumer behavior and persuasion.
Focus on topics like:
- Consumer decision making
- Persuasion techniques
- Marketing influence
- Social media influence
- Behavioral economics
- Consumer psychology

Text of the paper:
{text[:2000]}...

{parser.get_format_instructions()}
"""
    
    # Get structured response from LLM
    result = llm.invoke(prompt)
    try:
        qualification = parser.parse(result.content)
        # Consider it relevant if confidence is high enough and it's marked as relevant
        return qualification.is_relevant and qualification.confidence >= 0.7
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        # Default to False if we can't parse the response
        return False    