#%%
# Third Party
import arxiv

# Library
from mongodb_api.models.models import Paper

#%%

search = arxiv.Search(
  query = "image generation",
  max_results = 1,
  sort_by = arxiv.SortCriterion.Relevance
)

for result in arxiv.Client().results(search):
    print(result)
# %%

# %%
paper = Paper(result)
# %%
paper=Paper(
    _id=result.entry_id,
    title=result.title,
    summary=result.summary,
    published=result.published,
    updated=result.updated,
   # authors=result.authors,
   # primary_category=result.primary_category,
   # categories=result.categories,
    doi=result.doi,
   # links=result.links,
    pdf_url=result.pdf_url,
    comment=result.comment,
    download_path=None,
  #  journal_ref=result.journal_ref,
  #  arxiv_comment=result.arxiv_comment,
   # primary_arxiv_category=result.primary_arxiv_category,
  #  arxiv_categories=result.arxiv_categories,
)
# %%


data = paper.model_dump_serialized(json_dump=False)
# Make the POST request to create a new paper
response = requests.post(url, json=data)
response
# Standard Library
# %%
import datetime

paper = Paper(
    entry_id="http://example.com/paper1",
    title="Sample Paper",
    summary="This is a summary of the sample paper.",
    published=datetime.datetime.now(),
    updated=datetime.datetime.now(),
    pdf_url="http://example.com/paper1.pdf"
)

# Serialize to dictionary
paper_dict = paper.model_dump()
print(paper_dict)

# Serialize to JSON string
paper_json = paper.model_dump_json()
print(paper_json)
# %%
response = requests.post(url, data=paper_dict)
# %%
response = requests.get(url, data="http://arxiv.org/abs/2210.06998v2")
# %%
response = requests.delete(url, data="http://arxiv.org/abs/2210.06998v2")
print(response)
print(response.text)
# Standard Library
import json

# Third Party
# %%
import requests

# API endpoint for creating a paper
url = "http://localhost:8000/paper/"  # Replace with your actual API URL

response = requests.get(url)
print(response)
print(response.text)
# %%

response = requests.delete(url, data="http://arxiv.org/abs/2210.06998v2")
print(response)
print(response.text)
# %%
