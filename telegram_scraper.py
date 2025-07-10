from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Channel, Chat



TELE_API_ID = 22290045

api_id = TELE_API_ID
api_hash = '654a76ff691499f5904c8e32656f473c'
phone = '+972584091183'

client = TelegramClient('navi_daily_news_scraper', api_id, api_hash)


async def main():
    all_news = []
    group_names = []
    await client.start(phone)

    dialogs = await client.get_dialogs()
    print("Groups and Channels you're in:\n")

    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, (Channel, Chat)):
            print(f"{entity.title} — ID: {entity.id}")
            group_names.append(entity.title)

    for group in group_names:
        target = group
        entity = await client.get_entity(target)

        # Fetch the 100 most recent messages
        messages = await client(GetHistoryRequest(
            peer=entity,
            limit=100,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        for msg in messages.messages:
            all_news.append({"group": group, "date": msg.date, "title": msg.message})

    return all_news


def scrape_telegram():
    with client:
        scraped_news = client.loop.run_until_complete(main())

    return scraped_news
