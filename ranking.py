import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

id = ""

collection = ''  # <--- INSERT COLLECTION ID HERE
nfts = []

nfts_final = []

occurance = {}

def computeRarity(properties):
    r = 0.0
    for prop in properties:
        r = r + 1.0 / occurance[prop][properties[prop]['value']]
    return r


def computeRarities(nfts):
    properties = {};

    for n in nfts:
        for prop in n['properties']:
            if properties.get(prop) == None:
                properties[prop] =[n['properties'][prop]['value']]
                #print(properties)
            else:
                properties[prop].append(n['properties'][prop]['value'])
    
    #  Compute rarity based on property occurance
    for key in properties:

        occurance[key] = {}
        counts = {}

        for num in properties[key]:
            if counts.get(num) == None:
                counts[num] = 1
            else:
                counts[num] = counts[num] + 1
        
        for num in counts:
            occurance[key][num] = counts[num] / len(properties[key])


while True:

    if id != "":
        r = requests.get('https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection + '&startAfter=' + id)
    else:
        r = requests.get('https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection)

    id = ""

    for x in r.json():
        id = x['id']

        nfts.append({'name': x['name'], 'properties': x['properties'], 'link': 'https://soonaverse.com/nft/' + x['id']})

    if id=="":
        break


computeRarities(nfts)

#print(len(nfts))

for n in nfts:
    r = computeRarity(n['properties'])

    #print(r, n['num'], n['link'])
    nfts_final.append([r, n['name'], n['link']])

nfts_final.sort(reverse=True)

#print(nfts_final)

c = 0
for f in nfts_final:
    c = c + 1
    print(str(c) + '/' + str(len(nfts_final)) + ', ' + f[1] + ', ' + str(f[0]) + ', ' + f[2])

