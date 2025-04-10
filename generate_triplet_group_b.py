from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class OneTripletB(BaseModel):
    subject: str = Field(description="Subject of the triplet")
    predicate: str = Field(description="Predicate of the triplet")
    object: str = Field(description="Object of the triplet")
    frequency: str = Field(description="Frequency of the triplet")
    context: str = Field(description="Context of the triplet")

class ListTripletsB(BaseModel):
    triplets: List[OneTripletB] = Field(description="List of triplets found in the paper")

def generate_triplet_group_b(text: str, llm: ChatOpenAI) -> bool:
    """Generate a triplet group B for a given paper.
    
    Args:
        text (str): The text content of the paper
        llm (ChatOpenAI): The language model to use for analysis
        
    Returns:
        bool: True if the paper is relevant, False otherwise
    """
    # Create parser for structured output
    parser = PydanticOutputParser(pydantic_object=ListTripletsB)
    
    # Create prompt template
    prompt = f"""
You are a research assistant helping build a knowledge graph about consumer behavior in teens and young adults.
Your job is to extract triples from scientific text using the following controlled vocabulary:
Marketing Cues (Stimuli): Countdown Timer, Flash Sale Banner, Scarcity Message, Product Rating, Urgency Tone, Social Proof Message
Customer Traits / Susceptibilities: Impulsivity, FOMO, Cognitive Load, Low Self-Regulation, Trust in Authority, Anxiety
Behavioral Outcomes (related to purchases): Impulsive Purchase, Cart Abandonment, Satisfaction, Regret, Return Behavior

For each valid statement in the text, extract a triple like this:
 Subject → Predicate → Object [in Teens or Young Adults]
Use only the vocabulary above. You can repeat the same type of triple if it appears multiple times.

Also output:
Frequency: How many times the relationship appears in the text
Context: If available (e.g., mobile app, discount season)

For example, if the text says: 
"Scarcity messages like 'Only 3 left!' have been shown to increase impulsive buying behavior, particularly in adolescents with high fear of missing out (FOMO)."


The triplets would be:
      "subject": "Scarcity Message",
      "predicate": "triggers",
      "object": "FOMO"
      "frequency": "1"
      "context": "Mobile e-commerce, back-to-school season"

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