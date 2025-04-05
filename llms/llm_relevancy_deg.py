import os
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

def requete_is_relevant(query):
    chat_history = [
        SystemMessage(content="""INPUT: un post Reddit.\n OUPUT: un float entre 0 et 1 \nANALYSE la polarisation entrainée par un post selon les débats sociétaux. Plus le score d'un élevé, plus les commentaires engendrés par ce poste seront polémiques. L'opinion exprimée n'importe pas, seulement le sujet. \nREPOND PAR UN FLOAT ENTRE 0 OU 1 ABSOLUMENT SANS AUTRE CARACTERE."""),
        UserMessage(content=query),
    ]

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        temperature=0
    )

    return chat_response.choices[0].message.content

print(requete_is_relevant("one minute of eye-spiced twerking"))
print(requete_is_relevant("La Terre est plate et la NASA cache la vérité."))
print(requete_is_relevant("Le changement climatique est un mythe inventé par les scientifiques."))
print(requete_is_relevant("le uno c'est vraiment un jeu de merde"))
print(requete_is_relevant("trump augment les impots"))
print(requete_is_relevant("gaza: attaque de l'armée israélienne"))