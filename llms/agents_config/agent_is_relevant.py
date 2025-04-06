#Agent defined on Mistral, agent id ag:b01ddf1b:20250405:untitled-agent:fee26ae0
#Cannot be imported! Local definition below (less extensive than the one on Mistral)

systematic_prompt = """INPUT: un post Reddit.
OUPUT: un float entre 0 et 1.
  
ANALYSE la polarisation entrainée par un post selon les débats sociétaux. 
Plus le score d'un élevé, plus les commentaires engendrés par ce poste seront polémiques. 
L'opinion exprimée n'importe pas, SEULEMENT LE SUJET.

REPOND PAR UN FLOAT ENTRE 0 OU 1 ABSOLUMENT SANS AUTRE CARACTERE."""

model_name = "open-mistral-nemo"

temperature = 0