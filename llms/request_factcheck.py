import wikipedia
import concurrent.futures  

import llms.agents_config.agent_to_wikipedia as agent1
import llms.agents_config.agent_from_wikipedia as agent2
from llms.request_to_agent import request_to_agent


def search_wikipedia(query):
    try:
        search_results = wikipedia.search(query, results=5) 
        return search_results
    except wikipedia.exceptions.DisambiguationError as e:
        return e.options
    except wikipedia.exceptions.HTTPTimeoutError:
        return ["Timeout error, please try again later."]
    except Exception as e:
        return str(e)


def wiki_search(query):
    try:
        result = wikipedia.search(query, results=1)
        if not result:
            return ""
        page = wikipedia.page(result[0], auto_suggest=False)
        return page.summary[:500]
    except:
        return ""


def reddit_factchecking(title, post, date):
    '''
    Returns a reliability grade to a given post that was posted at a given date
    '''
    query = "Date : " + date + "\n Title :" + title + "\n Post : " + post
    search = request_to_agent(query, agent1)

    facts = [search_wikipedia(fact.strip()) for fact in search.split(";") if fact.strip()]
    facts = facts[:3]  # Limiter à 3 pour cohérence avec prompt

    # Paralléliser les recherches avec ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        summaries = list(executor.map(wiki_search, facts))

    additional_info = "\n Additional information : " + " ".join(summaries)

    final_query = query + "\n" + additional_info

    final = request_to_agent(final_query, agent2)
    final_cleaned = ''.join(c for c in final if c.isdigit())
    return int(final_cleaned) if final_cleaned else 0



