from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class OneTriplet(BaseModel):
    subject: str = Field(description="Subject of the triplet")
    predicate: str = Field(description="Predicate of the triplet")
    object: str = Field(description="Object of the triplet")

class ListTriplets(BaseModel):
    triplets: List[OneTriplet] = Field(description="List of triplets found in the paper")

def generate_triplet_group_a(text: str, llm: ChatOpenAI) -> bool:
    """Generate a triplet group A for a given paper.
    
    Args:
        text (str): The text content of the paper
        llm (ChatOpenAI): The language model to use for analysis
        
    Returns:
        bool: True if the paper is relevant, False otherwise
    """
    # Create parser for structured output
    parser = PydanticOutputParser(pydantic_object=ListTriplets)
    
    # Create prompt template
    prompt = f"""From the paragraph below, extract any cause-effect relationships involving marketing cues, psychological traits, and behaviors in teens or young adults. Format each as a triple:
 Cue → causes/influences → Trait or Behavior [in Teens/Young Adults]
 For example, if the text says: 
If the paragraph says:
"Scarcity messages like 'Only 3 left!' have been shown to increase impulsive buying behavior, particularly in adolescents with high fear of missing out (FOMO)."

The triplets would be:
      "subject": "Scarcity Message",
      "predicate": "triggers",
      "object": "FOMO"

Text of the paper:
{text[:50000]}...

{parser.get_format_instructions()}
"""
    
    # Get structured response from LLM
    result = llm.invoke(prompt)
    try:
        triplets = parser.parse(result.content)
        return triplets
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        # Default to empty list if we can't parse the response
        return []