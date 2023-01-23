import requests
import time
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

t = int(time.time() * 1000)
# t -= 60*60*1000*24*7  # Rewind time

soonanaut = '0xcbe28532602d67eec7c937c0037509d426f38223'
artifact = '0xdb47fa3d6cdc14910933d0074fba36a396771bfa'
alien = '0x1fae1a8558b57591c3de2aacc0d3df1802eff2ab'

# SETTINGS
webhook_url = ''  # <--- INSERT DISCORD CHANNEL WEBHOOK HERE

current_floor = 0*1000000  # Initial floor price to ignore


# Options
once = False  # If true, do not wait for new updates but exit

webhook = DiscordWebhook(url=webhook_url)

update_artifact = True
update_soonanaut = True
update_alien = True

locks = {}

d_alien = None
d_artifact = None
d_soonanaut = None


def getOwner(owner_id):
    owner = '?'

    if owner_id is not None:
        r2 = requests.get(
            'https://soonaverse.com/api/getById?collection=member&uid=' + owner_id)

        j2 = r2.json()

        if j2.get('name') is not None:
            owner = j2['name']
    return owner


def getData(collection):

    data = []

    id = ""
    while True:

        time.sleep(1)

        if id != "":
            r = requests.get(
                'https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection + '&startAfter=' + id)
        else:
            r = requests.get(
                'https://soonaverse.com/api/getMany?collection=nft&fieldName=collection&fieldValue=' + collection)

        id = ""

        for x in r.json():

            id = x['id']

            if (x.get('availablePrice') is not None and x['availablePrice'] is not None):
                # More than 1 Mi/SMR to prevent accidental listings
                if (x['availablePrice'] > 1000000 and (x.get('saleAccessMembers') is None or len(x['saleAccessMembers']) == 0)):
                    num = x['name'].split('#')[1]
                    data.append([num, x['availablePrice'],
                                x['id'], x['name'], x['owner'],  x['media']])
                    # print(x['name'])

        if id == "":
            break

    return sorted(data)


while True:

    print("tick", t)

    # LATEST UPDATES
    r = requests.get(
        'https://soonaverse.com/api/getUpdatedAfter?collection=nft&updatedAfter=' + str(t))

    j = r.json()

    if len(j) == 0:

        update_floor = False

        if update_alien:
            print("update alien")
            update_floor = True
            update_alien = False
            d_alien = getData(alien)
        if update_artifact:
            print("update artifact")
            update_floor = True
            update_artifact = False
            d_artifact = getData(artifact)
        if update_soonanaut:
            print("update soonanaut")
            update_floor = True
            update_soonanaut = False
            d_soonanaut = getData(soonanaut)

        if update_floor:

            sets = []

            for a in d_soonanaut:
                for b in d_artifact:
                    if a[0] == b[0]:
                        for c in d_alien:
                            if a[0] == b[0] and b[0] == c[0]:
                                total = a[1] + b[1] + c[1]
                                sets.append([total, a, b, c])

            sets.sort()

            print(len(d_alien), len(d_artifact), len(d_soonanaut), len(sets))

            if (len(sets) > 0):

                s = sets[0]

                if s[0] != current_floor:
                    current_floor = s[0]

                    txt = s[1][3] + ': https://soonaverse.com/nft/' + s[1][2] + '\n'
                    txt += s[2][3] + ': https://soonaverse.com/nft/' + s[2][2] + '\n'
                    txt += s[3][3] + ': https://soonaverse.com/nft/' + s[3][2]

                    # POST FLOOR PRICE
                    embed = DiscordEmbed(title='NF3 Ultra #' + s[1][0] + ': ' + str(
                        + s[0] / 1000000) + ' smr',

                                        description=txt,
                                        color='03b2f8')
                    embed.set_thumbnail(str(s[1][5]))
                 
                    embed.add_embed_field(
                        name='Soonanaut', value= 'by: ' + getOwner(s[1][4]) + '\n' + \
                        str(s[1][1] / 1000000) + ' smr')
                    embed.add_embed_field(
                        name='Artifact', value='by: ' + getOwner(s[2][4]) + '\n' + \
                        str(s[2][1] / 1000000) + ' smr')
                    embed.add_embed_field(
                        name='Alien', value='by: ' + getOwner(s[3][4]) + '\n' + \
                        str(s[3][1] / 1000000) + ' smr')
                    embed.set_timestamp()

                    embed.set_footer(text='Floor price update')

                    # add embed object to webhook
                    webhook.add_embed(embed)
                    response = webhook.execute()
                    webhook.remove_embeds()

        if once:
            break
        else:
            time.sleep(60*5)
            continue

    for k in j:

        m = k['updatedOn']['_seconds'] * 1000 + \
            k['updatedOn']['_nanoseconds'] / 1000000

        t = int(m) + 1

        if k['collection'] == soonanaut:
            update_soonanaut = True
        if k['collection'] == alien:
            update_alien = True
        if k['collection'] == artifact:
            update_artifact = True


print('done')
