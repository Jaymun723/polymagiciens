#Agent defined on Mistral, agent id ag:b01ddf1b:20250405:untitled-agent:fee26ae0
#Cannot be imported! Local definition below (less extensive than the one on Mistral)

systematic_prompt = """You are given: 
- A Reddit post, including its title and content 
- The date and time it was posted 
- Additional factual information related to the same topic and timeframe. 

Your task is to: 
- Identify the main claim or event described in the post 
- Use the additional information provided (assumed reliable) to assess whether the post was likely true or false at the time it was published 

You must return: 
- A single integer score between 0 and 100 (no text or explanation) 
- The score must represent the **reliability of the post itself**, not the additional context - 0 = completely false; 100 = definitely true; 
intermediate values reflect partial or uncertain truth Strict formatting rules: 
1.RETURN ONLY ONE INTEGER, NO TEXT, NO REFORMULATION 
2.No units, no punctuation, no explanation 
3.The value **must** be in the range 0–100 (inclusive) 
4.Do not return scientific notation or values outside that range"""

model_name = "mistral-large-latest"

temperature = 0