"""Process raw_results.json into processed_results.json"""
import json

with open('raw_results.json', 'r') as f:
    raw = json.load(f)

# 小平市 had no election
# only two candidates ran and both were elected by default
raw = [district for district in raw if district['name'] != '小平市']

# Keep only raw vote numbers
for district in raw:
    for result in district['results']:
        result['num_votes'] = result['num_votes'].split('\n')[0]

# reshaped :: [(district_name, num_votes, party)]
reshaped = []
for district in raw:
    for result in district['results']:
        tup = (district['name'], result['num_votes'], result['party'])
        reshaped.append(tup)

with open('processed_results.json', 'w') as f:
    json.dump(reshaped, f, indent=2)
