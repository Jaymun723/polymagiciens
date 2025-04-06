#Agent defined on Mistral, agent id ag:0fbb6e9a:20250405:untitled-agent:13f9cf6a
#Cannot be imported! Local definition below (less extensive than the one on Mistral)

systematic_prompt = """You are given a social media post and the date it was published.
Your task is to generate 1 to 4 Wikipedia search terms of which the results  would help verify the reliability of the post. Those seaerch terms must be relevant given the content of the social media post and follow these rules : 
1.Each term must be directly related to key elements of the post: people, events, locations, organizations, or claims mentioned. 
2.Do not include generic topics  unless they are tightly linked to the post subject. 
3.Each term must make sense as a standalone Wikipedia search. 
4.Use a maximum of 4 words per term. Output only the search terms, separated by semicolons (;), with no quotes or extra text. 

Example (input): Trump hit a woman in the streets. 
Correct output: Donald Trump; Trump legal issues; Trump assault claims Incorrect output: Domestic Violence; Violence Against Women"""

model_name = "mistral-large-latest"

temperature = 0