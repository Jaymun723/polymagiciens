import llms.agents_config.agent_is_relevant as agent1
from llms.request_to_agent import request_to_agent 


print(request_to_agent("one minute of eye-spiced twerking", agent1))
print(request_to_agent("La Terre est plate et la NASA cache la vérité.", agent1))
print(request_to_agent("Le changement climatique est un mythe inventé par les scientifiques.", agent1))
print(request_to_agent("le uno c'est vraiment un jeu de merde", agent1))
print(request_to_agent("trump augment les impots", agent1))
print(request_to_agent("gaza: attaque de l'armée israélienne", agent1))