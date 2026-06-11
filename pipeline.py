from agents import writer_chain , critic_chain
from tools import web_search, scrape_url
import re

def run_research_pipeline(topic : str) -> dict:

    state = {}

    #search agent working 
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    state["search_results"] = web_search.invoke({"query": topic})
    print("\n search result ",state['search_results'])

    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    urls = re.findall(r'https?://[^\s]+', state["search_results"])
    print("\nURLs found:", urls)
    scraped_contents = []
    for url in urls:
        if "youtube.com" in url:
            continue
        try:
            content = scrape_url.invoke({"url": url})
            if (
                "Could not scrape" not in content
                and "403" not in content
            ):
                scraped_contents.append(content)
        except Exception as e:
            print(f"Skipping {url}: {e}")
    state["scraped_content"] = "\n\n".join(scraped_contents)
    if not state["scraped_content"]:
        state["scraped_content"] = "No successful scraping results."
    print("\nscraped content:\n", state["scraped_content"])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
