from mistralai import Mistral
from mistralai.models import  UserMessage, SystemMessage
from mistralai.models import TextChunk, ReferenceChunk
import os
import wikipedia
import json
from datetime import datetime
import json
from mistralai import ToolMessage

## Step 1: Initialize the Mistral client

client = Mistral(
    api_key="OZSyUAoFi2DmsjJz5Cuqg8vWeFzG9grq",
)

def post_to_grade(post,date):
    '''
    Returns a reliability grade to a given post that was posted at a given date
    '''
    #build the query for the Mistral Agent 
    query = "Date : "+ date + "\n Post : " + post
    
    #Add the user message to the chat_history
    chat_history = [
        SystemMessage(content="The input is a post (from a social media : could be Facebook or Reddit etc) and the time and date it was posted at, and the aim is to verify its reliability. You formulate one or multiple facts that you want to know and that can be searched on wikipedia to find information that should help determine the veracity and reliability of the post. The facts you ask for should be independent of the data you already have access to and independent of the post in the sense that the questions will be web searches. The list of facts you want should be given without explanation or context in the form of a wikipedia search (not any sentence except the facts themselves, so no sentence at all before those facts) and should be in a format that can be read by python. Use the least facts possible necessary to check the information correctly without missing any important point (given the date at which the post was written) There should be a semicolon between every fact that you want to check, and there should be no quotation marks"),
        UserMessage(content=query),
    ]

    chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=chat_history,
            temperature = 0.05
        )

    #complete with the result of the wikipedia searches
    search = chat_response.choices[0].message.content
    facts = [fact.strip() for fact in search.split(";") if fact.strip()]

    additional_info = "\n Additional information : "
    
    for f in facts : 
        additional_info += wiki_search(f) + " "

    #final ask to a Mistral agent for a reliability grade 

    final_query = query + "\n" + additional_info
    print(final_query)

    chat_history = [
        SystemMessage(content="The input is a reddit post, poster by a user, at a given time, and some additional relevant information related to the content of the post. Identify the event or fact talked about in the post, and the time and date it was posted at, then use the additional information given - that is about the same subject at a similar time and date - to verify whether the information is true at the given date and time, or at least the probability for it to be true. The output you give is a grade between 0 and 100 (and only a grades ince the output will then be used as an int) and represents the reliability of the post (and only the post, not the additional information that should be considered true without fact checking needed) that was given as an input - 0 is not reliable at all (so the information is false) and 100 is very reliable (so a true information), in between are the information vague with a certain probability to be true. The output is the score and only the score without any sentence (no string) you can ask a maximum of 3 different searches, no more than that"),
        UserMessage(content=final_query),
    ]

    answer = client.chat.complete(
            model="mistral-large-latest",
            messages=chat_history,
            temperature = 0.05
        )

    final = answer.choices[0].message.content
    return int(final)

def wiki_search(query):

    # Step 1: Initialize the Mistral client
    chat_history = [
        SystemMessage(content="You are a helpful assistant that can search the web for information. Use context to answer the question. You MUST use the web_search tool to answer the following query, do NOT try to guess the answer yourself. Use only useful information that is relevant and related to the topic given by the input, your answer must be composed by a maximum of 50 words"),
        UserMessage(content=query),
    ]

    # Step 2 : Define the function calling tool to search Wikipedia
    web_search_tool = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for a query for which you do not know the answer",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search the web in keyword form.",
                    }
                },
                "required": ["query"],
            },
        },
    }



    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        tools=[web_search_tool],
        temperature = 0.05
    )


    if hasattr(chat_response.choices[0].message, 'tool_calls'):
        tool_call = chat_response.choices[0].message.tool_calls[0]
        chat_history.append(chat_response.choices[0].message)
    else:
        print("No tool call found in the response")

    #Step 3: Define Method to Search Wikipedia Associated with the Tool

    def get_wikipedia_search(query: str) -> str:
        """
        Search Wikipedia for a query and return the results in a specific format.
        """
        result = wikipedia.search(query, results = 5)
        data={}
        for i, res in enumerate(result):
            pg= wikipedia.page(res, auto_suggest=False)
            data[i]={
                "url": pg.url,
                "title": pg.title,
                "snippets": [pg.summary.split('.')],
                "description": None,
                "date": datetime.now().isoformat(),
                "source": "wikipedia"
            }
        return json.dumps(data, indent=2)

    # Step 4: Perform the Tool Call and Search Wikipedia

    query = json.loads(tool_call.function.arguments)["query"]
    wb_result = get_wikipedia_search(query)

    tool_call_result = ToolMessage(
        content=wb_result,
        tool_call_id=tool_call.id,
        name=tool_call.function.name,
    )


    # Append the tool call message to the chat_history
    chat_history.append(tool_call_result)

    # Step 5: Call Mistral with the Tool Call Result

    def format_response(chat_response: list, wb_result:dict):
        refs_used = []
        
        # Print the main response
        for chunk in chat_response.choices[0].message.content:
            if isinstance(chunk, TextChunk):
                None
            elif isinstance(chunk, ReferenceChunk):
                refs_used += chunk.reference_ids
                

    # Use the formatter
    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=chat_history,
        tools=[web_search_tool],
    )
    format_response(chat_response, wb_result)

    # Step 6 : Streaming completion with references

    stream_response = client.chat.stream(
        model="mistral-large-2411",
        messages=chat_history,
        tools=[web_search_tool],
    )

    last_reference_index = 0
    info = ""
    if stream_response is not None:
        for event in stream_response:
            chunk = event.data.choices[0]
            if chunk.delta.content:
                if isinstance(chunk.delta.content, list):
                        # Check if TYPE of chunk is a reference
                        references_ids = [
                            ref_id
                            for chunk_elem in chunk.delta.content
                            if isinstance(chunk_elem, ReferenceChunk)
                            for ref_id in chunk_elem.reference_ids
                        ]
                        last_reference_index += len(references_ids)

                        # Map the references ids to the references data stored in the chat history
                        references_data = [json.loads(wb_result)[str(ref_id)] for ref_id in references_ids]
                        urls = " " + ", ".join(
                            [
                                f"[{i}]({reference['url']})"
                                for i, reference in enumerate(
                                    references_data,
                                    start=last_reference_index - len(references_ids) + 1,
                                )
                            ]
                        )
                        info += urls + " "
                else:
                    info += chunk.delta.content + " "
    return info 

print(post_to_grade("Trump is the president of the united states.","2025-04-01T10:00:00Z"))