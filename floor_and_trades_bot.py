import requests
import time
import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed

t = int(time.time() * 1000)
#t -= 60*60*1000*24  # Rewind time

collection = ''   # <--- INSERT THE COLLECTION ID HERE
webhook_url = ''  # <--- INSERT THE DISCORD CHANNEL WEBHOOK HERE

current_floor = 0*1000000  # Initial floor price to ignore

# COLLECTION NAME
col = '?'

r3 = requests.get(
    'https://soonaverse.com/api/getById?collection=collection&uid=' + collection)

j3 = r3.json()

if j3.get('name') is not None:

    col = j3['name']

# Options
once = False  # If true, do not wait for new updates but exit

webhook = DiscordWebhook(url=webhook_url)


do_floor_update = True

locks = {}

while True:

    print("tick", t)
    time.sleep(2)

    # LATEST UPDATES
    r = requests.get(
        'https://soonaverse.com/api/getUpdatedAfter?collection=nft&updatedAfter=' + str(t))

    j = r.json()

    if len(j) == 0:

        if do_floor_update:

            do_floor_update = False

            print('Computing new floor...')

            # FLOOR
            id = ''
            floor = 0
            f = None

            while True:

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

                            if (x['availablePrice'] < floor or floor == 0):
                                floor = x['availablePrice']
                                f = x

                if id == "" and f is not None and floor != current_floor:

                    current_floor = floor

                    # NETWORK TYPE
                    pair = 'Mi'

                    if f.get('mintingData') is not None:

                        if f['mintingData']['network'] == 'smr':
                            pair = 'SMR'

                    # OWNER NAME
                    owner = '?'

                    if f.get('owner') is not None:
                        r2 = requests.get(
                            'https://soonaverse.com/api/getById?collection=member&uid=' + f['owner'])

                        j2 = r2.json()

                        if j2.get('name') is not None:
                            owner = j2['name']

                    # POST FLOOR PRICE
                    embed = DiscordEmbed(title=f['name'],
                                         description=col,
                                         color='03b2f8',
                                         url='https://soonaverse.com/nft/' + f['id'])
                    embed.set_thumbnail(f['media'])
                    embed.add_embed_field(name='Price', value=str(
                        f['availablePrice'] / 1000000) + ' ' + pair)
                    embed.add_embed_field(name='Owner', value=owner)
                    embed.set_timestamp()

                    embed.set_footer(text='Floor price update')

                    # add embed object to webhook
                    webhook.add_embed(embed)
                    response = webhook.execute()
                    webhook.remove_embeds()

                    dt = datetime.datetime.now().strftime("%H:%M")

                    print(dt + ' [FLOOR] ' + f['name'] + ': ' +
                          str(f['availablePrice'] / 1000000) + ' ' + pair + ' by ' + owner)

                if id == "":
                    break

        if once:
            break
        else:
            time.sleep(60)
            continue

    for k in j:

        # NETWORK TYPE
        pair = 'Mi'

        if k.get('mintingData') is not None:

            if k['mintingData']['network'] == 'smr':
                pair = 'SMR'

        m = k['updatedOn']['_seconds'] * 1000 + \
            k['updatedOn']['_nanoseconds'] / 1000000

        dt = datetime.datetime.fromtimestamp(m/1000).strftime("%H:%M")
        t = int(m) + 1

        if k['collection'] != collection:
            continue

        do_floor_update = True

        # OWNER NAME
        owner = '?'

        if k.get('owner') is not None:
            r2 = requests.get(
                'https://soonaverse.com/api/getById?collection=member&uid=' + k['owner'])

            j2 = r2.json()

            if j2.get('name') is not None:
                owner = j2['name']

        # IGNORE 1Mi/SMR LISTINGS
        if k['availablePrice'] is not None and k['availablePrice'] == 1000000:
            print("LOCK", owner)
            locks[k['id']] = True
        elif k['availablePrice'] is not None and k['availablePrice'] > 1000000:
            print("NO LOCK", owner)
            locks[k['id']] = False

        # TRADES
        if k['price'] > 0 and k['sold'] == True and (locks.get(k['id']) == None or locks[k['id']] == False):

            sold = k['soldOn']['_seconds'] * 1000 + \
                k['soldOn']['_nanoseconds'] / 1000000
            d = abs(sold - m)

            if d < 60*1000 and k['price'] > 0:
                print(dt + ' [TRADE] ' + k['name'] + ': ' +
                      str(k['price'] / 1000000) + ' ' + pair + ' by ' + owner)

                # create embed object for webhook
                # you can set the color as a decimal (color=242424) or hex (color='03b2f8') number
                embed = DiscordEmbed(title=k['name'],
                                     description=col,
                                     color='03b2f8',
                                     url='https://soonaverse.com/nft/' + k['id'])
                embed.set_thumbnail(k['media'])
                embed.add_embed_field(name='Price', value=str(
                    k['price'] / 1000000) + ' ' + pair)
                embed.add_embed_field(name='Owner', value=owner)
                embed.set_timestamp(sold/1000)

                embed.set_footer(text='New trade')

                # add embed object to webhook
                webhook.add_embed(embed)

                response = webhook.execute()

                webhook.remove_embeds()

print('done')
