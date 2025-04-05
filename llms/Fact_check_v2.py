from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage
import os
import wikipedia
import json
from datetime import datetime
import concurrent.futures  # ⬅️ Ajout pour paralléliser

# Initialize the Mistral client
client = Mistral(
    api_key="OZSyUAoFi2DmsjJz5Cuqg8vWeFzG9grq",
)

def search_wikipedia(query):
    try:
        # Rechercher sur Wikipedia en fonction du texte de la requête
        search_results = wikipedia.search(query, results=5)  # Retourne les 5 premiers résultats
        return search_results
    except wikipedia.exceptions.DisambiguationError as e:
        # Si plusieurs articles existent, on récupère la liste d'articles possibles
        return e.options
    except wikipedia.exceptions.HTTPTimeoutError:
        return ["Timeout error, please try again later."]
    except Exception as e:
        return str(e)


def post_to_grade(title, post, date):
    '''
    Returns a reliability grade to a given post that was posted at a given date
    '''
    query = "Date : " + date + "\n Title :" + title + "\n Post : " + post

    chat_history = [
        SystemMessage(content="You are given a social media post and the date it was published. Your task is to generate 1 to 4 Wikipedia search terms of which the results  would help verify the reliability of the post. Those seaerch terms must be relevant given the content of the social media post and follow these rules : 1.Each term must be directly related to key elements of the post: people, events, locations, organizations, or claims mentioned. 2.Do not include generic topics  unless they are tightly linked to the post subject. 3.Each term must make sense as a standalone Wikipedia search. 4.Use a maximum of 4 words per term. Output only the search terms, separated by semicolons (;), with no quotes or extra text. Example (input): "Trump hit a woman in the streets" Correct output: Donald Trump; Trump legal issues; Trump assault claims Incorrect output: Domestic Violence; Violence Against Women"),
        UserMessage(content=query),
    ]

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        temperature=0
    )

    search = chat_response.choices[0].message.content
    #print(search)
    facts = [search_wikipedia(fact.strip()) for fact in search.split(";") if fact.strip()]
    facts = facts[:3]  # Limiter à 3 pour cohérence avec prompt

    # Paralléliser les recherches avec ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        summaries = list(executor.map(wiki_search, facts))

    additional_info = "\n Additional information : " + " ".join(summaries)

    final_query = query + "\n" + additional_info
    #print(final_query)

    chat_history = [
        SystemMessage(content="The input is a reddit post, poster by a user, at a given time, and some additional relevant information related to the content of the post. Identify the event or fact talked about in the post, and the time and date it was posted at, then use the additional information given - that is about the same subject at a similar time and date - to verify whether the information is true at the given date and time, or at least the probability for it to be true. The output you give is a grade between 0 and 100 (and only a grades ince the output will then be used as an int) and represents the reliability of the post (and only the post, not the additional information that should be considered true without fact checking needed) that was given as an input - 0 is not reliable at all (so the information is false) and 100 is very reliable (so a true information), in between are the information vague with a certain probability to be true. The output is the score and only the score without any sentence (no string) you can ask a maximum of 3 different searches, no more than that"),
        UserMessage(content=final_query),
    ]

    answer = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        temperature=0
    )

    final = answer.choices[0].message.content
    final_cleaned = ''.join(c for c in final if c.isdigit())
    return int(final_cleaned) if final_cleaned else 0


# Nouvelle version simplifiée de wiki_search()
def wiki_search(query):
    try:
        result = wikipedia.search(query, results=1)
        if not result:
            return ""
        page = wikipedia.page(result[0], auto_suggest=False)
        return page.summary[:500]
    except:
        return ""
