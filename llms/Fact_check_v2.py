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

def post_to_grade(title, post, date):
    '''
    Returns a reliability grade to a given post that was posted at a given date
    '''
    query = "Date : " + date + "\n Title :" + title + "\n Post : " + post

    chat_history = [
        SystemMessage(content="The input is a post and its title (from a social media : could be Facebook or Reddit etc) and the time and date it was posted at..."),
        UserMessage(content=query),
    ]

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        temperature=0.05
    )

    search = chat_response.choices[0].message.content
    print(search)
    facts = [fact.strip() for fact in search.split(";") if fact.strip()]
    facts = facts[:3]  # ⬅️ Limiter à 3 pour cohérence avec prompt

    # ▶️ Paralléliser les recherches avec ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        summaries = list(executor.map(wiki_search, facts))

    additional_info = "\n Additional information : " + " ".join(summaries)

    final_query = query + "\n" + additional_info
    print(final_query)

    chat_history = [
        SystemMessage(content="The input is a reddit post, poster by a user..."),
        UserMessage(content=final_query),
    ]

    answer = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        temperature=0.05
    )

    final = answer.choices[0].message.content
    return int(final)

# 🔁 Nouvelle version simplifiée de wiki_search()
def wiki_search(query):
    try:
        page = wikipedia.page(query, auto_suggest=False)
        return page.summary[:500]  # ⬅️ Limite la taille pour aller vite
    except:
        return ""

print(post_to_grade("Trump is the president of the united states.","2025-04-01T10:00:00Z"))