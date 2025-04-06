#Agent defined on Mistral, agent id ag:b01ddf1b:20250405:untitled-agent:fee26ae0
#Cannot be imported! Local definition below (less extensive than the one on Mistral)

systematic_prompt = """INPUT: un post Reddit.
OUPUT: un float entre 0 et 1.
  
ANALYSE la polarisation entrainée par un post selon les débats sociétaux. 
Plus le score d'un élevé, plus les commentaires engendrés par ce poste seront polémiques. 
L'opinion exprimée n'importe pas, SEULEMENT LE SUJET.

Exemple:En direct, guerre à Gaza : une vidéo consultée par l’Agence France-Presse contredit les déclarations israéliennes sur les secouristes tués près de Rafah
Résultat: 0.3

Exemple: La Terre est plate et la NASA cache la vérité.
Résultat: 0.95

Exemple:The size of pollock fishnet
Résultat:0.05

UN RESULTAT SUPERIEUR A 0.5 SIGNIFIE QUE LE POSTE EST TRES POLEMIQUE
REPOND PAR UN FLOAT ENTRE 0 OU 1 ABSOLUMENT SANS AUTRE CARACTERE."""

model_name = "open-mistral-nemo"

temperature = 0