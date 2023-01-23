import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

id = ""

collection = ''  # <-- INSERT COLLECTION ID HERE

data = []

print('NFT_ID;OWNER_ID;OWNER_NAME')

while True:

    if id != "":
        r = requests.get('https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection + '&startAfter=' + id)
    else:
        r = requests.get('https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection)

    id = ""


    for x in r.json():

        data.append(x)
        

    if id=="":
        break

for x in data:
    id = x['id']
    owner_id = x['owner']

    # OWNER NAME
    owner = '?'

    if owner_id is not None:
        r2 = requests.get(
            'https://soonaverse.com/api/getById?collection=member&uid=' + owner_id)

        j2 = r2.json()

        if j2.get('name') is not None:
            owner = j2['name']

    print(id + ';' + owner_id + ';' + owner)
