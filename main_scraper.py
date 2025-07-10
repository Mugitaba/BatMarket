import os.path
import time
from datetime import datetime, date
import requests
import xmltodict
import json
import google.generativeai as genai
from gtts import gTTS
from flask import Flask, url_for
from telegram_scraper import scrape_telegram
from my_secrets import API_KEY



YNET_URL = 'https://www.ynet.co.il/Integration/StoryRss1854.xml'
WALLA_URL = 'https://rss.walla.co.il/feed/22'
HAARETZ_URL = 'https://www.haaretz.co.il/srv/rss---feedly'
NYT_URL = 'https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml'
MAARIV_URL = 'https://www.maariv.co.il/Rss/RssFeedsMivzakiChadashot'

#############################   change before commit   #############################################
genai.configure(api_key=API_KEY)
#############################   change before commit   #############################################
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')


now = datetime.now()
today_date_time = now.strftime("%Y_%m_%d-%H")
audio_file_name = f"news{today_date_time}.mp3"
audio_file_path = f"static/{audio_file_name}"
text_file_path = f"static/en_news{today_date_time}.txt"
site_file_path = f"static/he_news{today_date_time}.txt"
json_file_path = f"static/{today_date_time}.json"

today_date = str(date.today())

news_only = False
rumors_only = True


LLM_HEADERS = {
    "Content-Type": "application/json"
}

os.makedirs("static", exist_ok=True)
print(f"Checking audio file: {os.path.abspath(audio_file_path)}")

need_to_generate_voice = (
    not os.path.exists(audio_file_path)
    or os.path.getsize(audio_file_path) == 0
)

need_to_generate_json = (
    not os.path.exists(json_file_path)
    or os.path.getsize(json_file_path) == 0
)

web_app = Flask(__name__)


class Source:
    def __init__(self, name, url, roots):
        self.name = name
        self.url = url
        self.roots = roots


ynet = Source('Ynet', YNET_URL, False)
walla = Source('Walla', WALLA_URL, False)
haaretz = Source('Haaretz', HAARETZ_URL, False)
nyt = Source('New York Times', NYT_URL, False)
maariv = Source('Maariv', MAARIV_URL, False)

sites_list = [ynet, walla, haaretz, nyt, maariv]
full_headlines = {}
for single_site in sites_list:
    full_headlines[single_site.name] = []

def get_rss_response(site):
    if not site.roots:
        rss_response = requests.get(site.url).text
        try:
            res = xmltodict.parse(rss_response)['rss']['channel']['item']
        except KeyError:
            print(rss_response)
            res = None
    else:
        res = None
    return res


def print_rss_reults(site):
    content = get_rss_response(site)

    if content:
        for item in content:
            full_headlines[site.name].append(f'title: {item["title"]}\npublished:{item["pubDate"]}\nlink:{item["link"]}\n\n')


def query_gemeni(prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text


def get_telegram():
    telegram_news = scrape_telegram()
    for item in telegram_news:
        if item["group"] in full_headlines.keys():
            full_headlines[item["group"]].append(f'title: {item["title"]}\npublished: {item["date"]}\nlink: "none"\n\n')
        else:
            full_headlines[item["group"]] = [f'title: {item["title"]}\npublished:{item["date"]}\nlink:"none"\n\n']



# RADIO_PROMPT = "You are a radio news editor assigned with phrasing a quick daily summary of the day's headlines in Israel that will be read by the newscaster."\
#               "Here are today's news and links. Please sum them all up to a cohesive narrative describing the day's events.\n"\
#               "**Important: only include the text, no comments, and do not add any information that is not mentioned in the original text. Take the publication time into account."\
#               "iclude information from any source type, regardless if it's a news site or a social media post. If there are any discrepancies between sources (excluding phrasing differences), mention which source says what"\
#               f"and how they contradict, please.\n At the end of the essay, please state all the sources you've actually used and which ones you excluded"

RADIO_PROMPT = """
I want you to act as a Broadcast Researcher for a news broadcast using information collected from multiple sources, including Telegram channels. 
These will include mainstream news outlets, independent journalists, activist groups, NGOs, and official government branches like the police or military.

Your task is to:
- First, translate all the information and the source names to English, ignore everything you know about the sources. 
- Ingest and summarize content *from all these sources equally* — there is no need to repeat information but do not exclude any source or prioritize official or mainstream media over others.
- Identify and highlight discrepancies or conflicting reports between sources.
- Note if some information appears less credible or biased and explain why (e.g. if a claim lacks evidence, contradicts other reports, or comes from a known propaganda source — but do not exclude it).
- Present the information in a way that can be used as a neutral, professional news broadcast script, but with clear disclosure of the different perspectives and their origins.
- Only include the actual text the news encore should read, DO NOT ADD ANY COMMENTS ABOUT THE TEXT! 
- Do not include any Hebrew text, if there is any Hebrew source, name or phrase translate or replace it with a phonetic English representation. Avoid underscores, Asterisks, at signs and the number sign.
- Do not rely on external sources or prior information you might have. 

Be especially careful not to filter out activist voices, independent channels, or unofficial reports. They must be included in the narrative and evaluated for their content like any other source.
"""


# TEXT_PROMPT = f" Please convert this text to a Hebrew news summary and "\
#                 "**important: Please only include the actual news don't add any explanations or other text"\
#                 "Please ensure you include all the relevant information in the original text:"


TEXT_PROMPT = """
I want you to act as a professional news website writer. Use information gathered from various Telegram channels, including mainstream news organizations, independent journalists, activist groups, NGOs, and official government entities such as the police and military.

Your task is to:
- Summarize and include content from **all** these sources equally — do **not** prioritize official or mainstream sources over grassroots, activist, or unofficial ones.
- Highlight discrepancies or conflicting accounts between sources, and specify which source each version came from.
- If a piece of information appears less credible or possibly biased, include it anyway, but mention **why** it may be unreliable (e.g., lacks supporting evidence, contradicts multiple sources, or comes from a known propaganda outlet).
- Present the output as a professional, clear, and concise **news summary in Hebrew**, in the style of a serious news website. Use informative section headers if relevant, and maintain a neutral tone.
- Mark headlines with an opening "**h**" and closing "**eh**" and paragraphs with an opening "**p**" and closing "**ep**" on both sides.
- **important: Please only include the actual news don't add any explanations or comments of your own. Also, do not rely on external sources or prior information you might have. 

Make sure to include **a range of perspectives**, including from unofficial or critical voices, and clearly indicate differences between them and official narratives.
e especially careful not to filter out activist voices, independent channels, or unofficial reports. They must be included in the narrative and evaluated for their content like any other source.
"""

if need_to_generate_json:
    if not news_only:
        get_telegram()
    if not rumors_only:
        for news_site in sites_list:
            print_rss_reults(news_site)
            full_headlines[news_site.name] = full_headlines[news_site.name][:10]
    rss_json = json.dumps(full_headlines, ensure_ascii=False, indent=2)
    with open(json_file_path, 'w') as jsonfile:
        jsonfile.write(rss_json)
else:
    with open(json_file_path, 'r') as jsonfile:
        rss_json = jsonfile.read()

if need_to_generate_voice:
    essay = model.generate_content(RADIO_PROMPT + "\n\n" + rss_json).text
    for _ in range(20):
        if not essay:
            time.sleep(3)
        else:
            break
    cleared_essay = essay.replace('*', '')
    print('generating sound file')
    tts = gTTS(text=cleared_essay, lang='en')
    tts.save(audio_file_path)
    with open(text_file_path, 'w') as textfile:
        textfile.write(essay)

    site_content = model.generate_content(f'{TEXT_PROMPT}: \n\n {rss_json}').text
    with open(site_file_path, 'w') as sitefile:
        sitefile.write(site_content)


else:
    with open(text_file_path, 'r') as textfile:
        essay = textfile.read()
    with open(site_file_path, 'r') as sitefile:
        site_content = sitefile.read()
    print(f'working directory: {os.getcwd()}')
    print(f'sound file in {audio_file_path} already exists')


@web_app.route('/')
def index():

    # audio_url = url_for('static', filename=f'{audio_file_name}')
    audio_url = f"/home/omer/.config/JetBrains/PyCharmEdu2022.2/scratches/static/{audio_file_name}"
    cleared_site_content = site_content.replace("**h**", "<h2>").replace("**eh**", "</h2>").replace("**ep**", "<p>").replace("**ep**", "</p>")

    return f'''
    <!DOCTYPE html>
        <html dir="rtl" lang="he">
            <head>
                <title>הנביא היומי! חדשות חמות מהינשוף</title>
            </head>
            <body>
                <main>
                    <h1>Today's news Summary{today_date}</h1>
                    <p>What follows is an AI summary of the day's news and rumors</p>
                </main>
                    <fieldset>
                        <legend>Text</legend>
                        {cleared_site_content}
                    </fieldset>
                    <fieldset>
                        <legend>Audio</legend>
                        <audio controls src="static/{audio_file_name}">
                    </fieldset>  
                </audio>
            </body>
        </html>
    
    '''


if __name__ == '__main__':
    web_app.run(debug=True)


## action_item: create a hirarchy of sources based on credibility.
## scrape images and add them to the site?
## add "loading" page
