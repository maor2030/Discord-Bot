import discord
from discord.ext import commands
import aiohttp
import asyncio
import requests
import random
import copy
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
last_check=[]
false_link=[]
newItem=[]
loop=0
start_flag=True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    global loop
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself

    if message.content.lower() == 'hello':
        await message.channel.send(f"Hello! {loop} loops")  # Respond to the message with 'Hello!'

    await bot.process_commands(message)  # Process bot commands\


class shoe:
    title = 'blank'
    price = 0
    site='blank'
    url='blank'
    link='blank'
    sizes=[]
 
    # parameterized constructor
    def __init__(self, t, p,s,u,l,size):
        self.title = t
        self.price = p 
        self.site=s
        self.url=u
        self.link=l
        self.sizes=size


async def check_jd_website():
    global false_link
    global last_check
    url = []
    ulist=['https://www.jdsports.co.il/search?sort_by=relevance&q=Air+jordan&type=product&options%5Bprefix%5D=last&options%5Bunavailable_products%5D=last&filter.p.m.custom.gender=%D7%92%D7%91%D7%A8%D7%99%D7%9D&filter.p.m.custom.gender=%D7%A0%D7%A9%D7%99%D7%9D&filter.p.m.custom.gender=%D7%A0%D7%95%D7%A2%D7%A8&filter.p.m.custom.product_type=%D7%A1%D7%A0%D7%99%D7%A7%D7%A8%D7%A1&filter.v.price.gte=&filter.v.price.lte=&page=',
           'https://www.jdsports.co.il/search?sort_by=relevance&q=dunk&type=product&options%5Bprefix%5D=last&options%5Bunavailable_products%5D=last&filter.p.m.custom.gender=%D7%92%D7%91%D7%A8%D7%99%D7%9D&filter.p.m.custom.gender=%D7%A0%D7%A9%D7%99%D7%9D&filter.p.m.custom.gender=%D7%A0%D7%95%D7%A2%D7%A8&filter.v.price.gte=&filter.v.price.lte=&page=']
    for k in range(2):
        u=ulist[k]
        i=0
        while(i!=3):
            i+=1
            ulist.append(u+str(i))
    ulist.pop(0)
    ulist.pop(0) #removing the links without pages
    url.append(ulist[0])
    url.append('https://sneakerboxtlv.com/product-category/newarrivals/?filter=1&pbrand=nike') 
    #url.append('https://sneakerboxtlv.com/') 
    url.append('https://sneakerboxtlv.com/product-category/newarrivals/brand/jordan/')
    url.append(ulist[2])
    url.append('https://www.nike.com/il/w/new-jordan-shoes-37eefz3n82yz3rauvz5e1x6znik1zy7ok')
    url.append('https://www.nike.com/il/w/new-dunk-shoes-3n82yz90aohzy7ok')
    url.append(ulist[1])
    url.append('https://www.terminalx.com/catalogsearch/result/?department_level=11220_11221_20741&p=2&q=dunk')
    url.append(ulist[3])
    url.append(ulist[5])
    url.append(ulist[4])
    items=[]
    for u in url:
        result = await url_enforcer(u)
        if result is not None:
            if result in false_link:
                false_link.remove(result) #making sure that problematic links wont be defined as new items
                last_check+=result
            items += result
        else:
            print('problem with '+u+' its none')
            false_link.append(u)
    return items

async def make_request(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=600)  # Set a timeout of 10 minutes
    while True:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    # Process the response
                    return await response.text()
            except (asyncio.TimeoutError, aiohttp.ClientError, aiohttp.ClientConnectionError, aiohttp.ClientConnectorError) as e:
                if '404' in f"An error occurred: {e}":
                    return 1
                print(f"An error occurred: {e}")
                await asyncio.sleep(600)  # Wait for 10 minutes before retrying

async def get_data(url):
    retry_delay = 600  # 10 minutes in seconds

    while True:
        try:
            data = requests.get(url)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(600)  # Wait for 10 minutes before retrying


async def url_enforcer(url):
    response= await make_request(url)
    if response is not None and response!=1:
        data=await get_data(url)
        soup = BeautifulSoup(data.content, 'html.parser') 
        general_size=[]
        shoe_size=[]
        if 'jdsports' in url:
            #finding the titles
            shoe_title =finding_attr(soup,'h2','product-item-meta__title')

            #finding prices
            shoe_price =soup.find_all('span', class_='price') 
            shoe_price=[shoe.text for shoe in shoe_price if not shoe.has_attr("class") or "price--compare" not in shoe["class"]]

            #finding img
            shoe_img =soup.find_all('img',class_='product-item__primary-image') 
            shoe_img = [img['src'] for img in shoe_img if '/products/' in img['src'] or '/files/' in img['src']]

            #finding site
            shoe_site='JD'

            #finding link
            shoe_link,shoe_size=await finding_link(soup,'a','product-item__aspect-ratio','JD')
            general_size=shoe_size


        elif 'nike' in url:
            #finding the titles
            shoe_title =finding_attr(soup,'a','product-card__link-overlay')

            #finding prices
            shoe_price =finding_attr(soup,'div', 'is--current-price') 

            #finding site
            shoe_site='nike'

            #finding link
            shoe_link,shoe_size=await finding_link(soup,'a','product-card__link-overlay','nike')
            general_size=shoe_size

            #img
            #shoe_img=finding_img(soup,'img','product-card__hero-image')
            shoe_img=shoe_title #trash

        elif 'sneakerbox' in url:
            #finding the titles
            shoe_title =finding_attr(soup,'div','title')
            shoe_title = [
            " ".join([word + " " * random.randint(0, 2) for word in sequence.split()]).strip()
            for sequence in shoe_title
            ]


            #finding prices
            shoe_price =finding_attr(soup,'bdi', None) 

            #img
            shoe_img =soup.find_all('div', class_='image bg first') 
            shoe_img=[img['style'].split('url(')[-1].split(')')[0] for img in shoe_img] 

            #finding site
            shoe_site='sneakerbox'

            # finding link
            shoe_link =soup.find_all('a') 
            shoe_link = [img['href'] for img in shoe_link if '/product/' in img['href']]
            for link in shoe_link:
                shoe_size=[1]
                general_size.append(shoe_size)
        
        elif 'terminal' in url:
            #finding the titles
            shoe_title =finding_attr(soup,'a','title_3ZxJ')

            #finding prices
            shoe_price =finding_attr(soup,'div', 'final-price_8CiX') 

            #finding site
            shoe_site='terminalx'

            #finding link
            shoe_link,shoe_size=await finding_link(soup,'a','title_3ZxJ','terminalx')
            general_size=shoe_size

            #img
            shoe_img =soup.find_all('img',class_='image_3k9y') 
            shoe_img = [img['src'] for img in shoe_img if '/product/' in img['src']]
            

        #merging
        products =[]
        for i in range(0,len(shoe_title)):
            products.append(shoe(shoe_title[i],shoe_price[i],shoe_site,shoe_img[i],shoe_link[i],general_size[i])) 
        return products


async def product_enforcer(url):
    response = await make_request(url)
    if response is not None and response!=1: # Check for any request errors
        data=await get_data(url)
        soup = BeautifulSoup(data.content, 'html.parser') 
        if 'jdsports' in url:
            div_elements = soup.find_all('div', class_=lambda value: value and 'block-swatch' in value)

            # Extract the text from the selected <div> elements
            shoe_size = [div.get_text().strip() for div in div_elements if div.get_text().strip()!='']
            if shoe_size:
                shoe_size.pop(0)
            shoe_size=[0]+shoe_size

            #finding stock
            stock=soup.find_all('span',class_='label label--subdued')
            if len(shoe_size)!=1 and not stock:
                shoe_size[0]=1
            else:
                shoe_size[0]=0
            

        elif 'nike' in url:
            #doesnt work
            shoe_size=[1]
            #shoe_size.pop(5) #!!!!

        elif 'sneakerbox' in url:
            #shoe_size=[shoe.find('label').text for shoe in shoe_size if not shoe.has_attr("class") or "is-disabled" not in shoe["class"]]
            shoe_elements=soup.find_all('div',class_='option enabled')
            shoe_size=[0]
            for shoe in shoe_elements:
                shoe_size.append(shoe.get('data-eu-size')) #checked is apllied only to the first shoe

            #finding stock
            if len(shoe_size)!=1:
                shoe_size[0]=1
        
        elif 'terminal' in url:
            # Find the <div> elements that don't have the class 'not-available'
            div_elements = soup.find_all('div', class_=lambda value: value and 'not-available' not in value,
                            attrs={'data-test-id': 'qa-size-item'})

            # Extract the text from the selected <div> elements
            shoe_size = [div.get_text() for div in div_elements]
            shoe_size=[0]+shoe_size

            #finding stock
            if len(shoe_size)!=1:
                shoe_size[0]=1
        
        return shoe_size
    return [1]


def has_class(element, class_name):
    return element.has_attr('class') and class_name in element['class']
    
def finding_attr(soup,div,clas):
    shoe_title =soup.find_all(div, class_=clas) 
    shoe_title=[shoe.text for shoe in shoe_title]
    return shoe_title

async def finding_link(soup,div,clas,site):
    shoe_size=[]
    shoe_link =soup.find_all(div, class_=clas) 
    shoe_link=[link['href'] for link in shoe_link]
    for link in shoe_link:
        if site=='JD':
            shoe_size.append(await product_enforcer('https://www.jdsports.co.il'+link)) # maybe a missing slash
        elif site=='terminalx':
            shoe_size.append(await product_enforcer('https://www.terminalx.com'+link))
        else:
            shoe_size.append(await product_enforcer(link))
    return shoe_link,shoe_size

async def monitor_jd_website():
    global last_check
    global loop
    global newItem
    DunkChannelJD = 1109142652772958300  # multiple channels
    AirJChannelJD= 1109143024405057536
    DunkChannelNike= 1110256953780879392
    AirJChannelNike= 1110257012564033606
    sneakerbox=1110270926798462996
    terminalx=1110593319534334022

    while True:
        shoe_elements = await check_jd_website()
        new_items = []
        if(last_check):
            for s in shoe_elements:
                exists = False
                #checking if its new on the site or restocked
                for shoe in last_check:
                    if 'launch' in s.link or s.site!='nike' :
                        if (
                            shoe.link == s.link and
                            shoe.price == s.price and
                            len(s.sizes)<=len(shoe.sizes) and
                            (s.sizes[0]==shoe.sizes[0] or
                             (s.sizes[0]==0 and shoe.sizes[0]==1)) #new for jd restock
                            ):
                            exists = True
                            break
                    else:
                        if (
                            (shoe.link.split('/')[-2]== s.link.split('/')[-2] and
                            shoe.price == s.price and
                            len(s.sizes)<=len(shoe.sizes))):
                            exists = True
                            break

                if not exists:
                    new_items.append(s)

            #checking if its been uploaded on the last update
            for s in new_items.copy():
                exists=False
                for shoe in newItem:
                    if 'launch' in s.link or s.site!='nike':
                        if (
                            shoe.link == s.link and
                            shoe.price == s.price):
                            exists = True
                            break
                    else:
                        if (shoe.link.split('/')[-2]== s.link.split('/')[-2] and shoe.price == s.price):
                            exists = True
                            break
                if exists:
                    new_items.remove(s)
                    
            
            #sending messages
            if new_items:
                newItem=new_items.copy()
                for item in new_items:
                    if "Dunk" in item.title and item.site=='JD':
                        await send_msg(DunkChannelJD,item)
                    elif "Jordan" in item.title and item.site=='JD':
                        await send_msg(AirJChannelJD,item)

                    elif "Dunk" in item.title and item.site=='nike':
                        await send_msg(DunkChannelNike,item)
                    elif "Jordan" in item.title and item.site=='nike':
                        await send_msg(AirJChannelNike,item)

                    elif "Dunk" in item.title and item.site=='sneakerbox':
                        await send_msg(sneakerbox,item)
                    elif "Jordan" in item.title and item.site=='sneakerbox':
                        await send_msg(sneakerbox,item)
                    elif "Air Max 1" in item.title and item.site=='sneakerbox':
                        await send_msg(sneakerbox,item)
                    elif "Dunk" in item.title and item.site=='terminalx':
                        await send_msg(terminalx,item)
                
                last_check = shoe_elements
        else:
            last_check=copy.deepcopy(shoe_elements)
            #here create a demo
            
            
        
        loop=loop+1
        await asyncio.sleep(random.randint(147,201))  # Wait before checking again 3 random.randint(60,120)

async def send_msg(shoe_channel,item):
    if item.sizes[0]==1 and not any(1<float(item) < 35.5 for item in item.sizes):
        channel = bot.get_channel(shoe_channel) 
        embed=discord.Embed(title="new shoe dropped to "+item.site+"!",color=0x109319)

        # Add author, thumbnail, fields, and footer to the embed

        if item.site!='nike':
            if 'https' in item.url:
                embed.set_thumbnail(url=item.url)
            else:
                embed.set_thumbnail(url='https:'+item.url)

        embed.add_field(name='Product name', value=item.title, inline=False)
        embed.add_field(name='Price',value=item.price, inline=False)
        if item.sizes[0]==1 and item.site!='nike' and item.site!='sneakerbox':
            embed.add_field(name='Stock',value='In stock!', inline=False)
            array_string = ', '.join(str(element) for element in item.sizes[1:])
            embed.add_field(name='Sizes',value=array_string, inline=False)


        if item.site=='terminalx':
            embed.add_field(name='Link', value='https://www.terminalx.com'+item.link, inline=False)

        elif item.site=='JD':
            embed.add_field(name='Link', value='https://www.jdsports.co.il'+item.link, inline=False)

        else:
            embed.add_field(name='Link', value=item.link, inline=False)

        embed.set_footer(text="Have a great day :)")
        await channel.send(embed=embed)

def run_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start('Your-Private-Key'))  # Replace YOUR_BOT_TOKEN with the actual bot token
    loop.create_task(monitor_jd_website())
    loop.run_forever()

def start():
    global start_flag
    if(start_flag):
        start_flag=False
        run_bot()

start()