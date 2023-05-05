import connector_db
import pandas as pd 
import requests
import json
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
XSALE_ORGANIZATION = connector_db.XSALE_ORGANIZATION


RAPORT_PATH = 'raport.xlsx'

LANGUAGE_ID = 9     # MarketplacePL
TARGET_LANGUAGE_ID = 2 # Angielski en-US

SOURCE_LANG = 'PL'
TARGET_LANG = 'EN'


def get_description_and_title(id):
    url = f" https://api.xsale.ai/{XSALE_ORGANIZATION}/articles/{id}/translations"
    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + connector_db.authorization,
        'x-id-token': connector_db.x_id_token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    for i in range(len(data)):
        if data[i]['LanguageId'] == LANGUAGE_ID:
            return {
                "title": data[i]['Name'],
                "description": data[i]['Description']
                }
        else:
            return {}

async def save_description_and_title_from_api():
    df = pd.read_excel(RAPORT_PATH)

    df["title"] = ""
    df["description"] = ""

    for index, row in df.iterrows():
        df.loc[df['xSale_ID'] == df.loc[index]['xSale_ID'], "title"] = get_description_and_title(df.loc[index]['xSale_ID'])['title'] 
        df.loc[df['xSale_ID'] == df.loc[index]['xSale_ID'], "description"] = get_description_and_title(df.loc[index]['xSale_ID'])['description']

    df.to_excel(f"{RAPORT_PATH}", index=False)

def translate_deepl(text):    
    url = "https://api-free.deepl.com/v2/translate"
    payload = {'text': text.encode('utf-8'), 'target_lang': TARGET_LANG, 'tag_handling': 'html', 'ignore_tags': 'img', 'source_lang': SOURCE_LANG}
    headers = {
    'Authorization': f'DeepL-Auth-Key {os.environ.get("DEEPL_KEY")}',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)

    return data["translations"][0]["text"]

async def translate_from_xlsx():    
    df = pd.read_excel(RAPORT_PATH)

    df[f"title_{TARGET_LANG}"] = ""
    df[f"description_{TARGET_LANG}"] = ""

    for index, row in df.iterrows():
        df.loc[df['title'] == df.loc[index]['title'], f"title_{TARGET_LANG}"] = translate_deepl(df.loc[index]['title'])
        df.loc[df['description'] == df.loc[index]['description'], f"description_{TARGET_LANG}"] = translate_deepl(df.loc[index]['description'])

    df.to_excel(f"{RAPORT_PATH}", index=False)
    print("The translation has been completed.")

def update_translation_in_xsale(id, name, description):
    url = f"https://api.xsale.ai/{XSALE_ORGANIZATION}/articles/{id}/translations"

    payload = {
    "LanguageId": TARGET_LANGUAGE_ID,
    "Name": name,
    "Description": description
    }

    # Encode payload to UTF-8
    encoded_payload = {}
    for k, v in payload.items():
        if isinstance(v, str):
            encoded_payload[k] = v.encode('utf-8').decode('utf-8')
        else:
            encoded_payload[k] = v

    # Convert dictionary to JSON string
    payload_str = json.dumps(encoded_payload)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + connector_db.authorization,
        'x-id-token': connector_db.x_id_token
    }

    response = requests.put(url, headers=headers, data=payload_str)
    # response = requests.put(url, headers=headers, data=payload)
    return response.status_code

async def update_translation_from_xlsx():
    df = pd.read_excel(RAPORT_PATH)
    df["Response_code"] = ""

    for index, row in df.iterrows():        
        df.loc[df['xSale_ID'] == df.loc[index]['xSale_ID'], "Response_code"] = update_translation_in_xsale(df.loc[index]['xSale_ID'], df.loc[index][f'title_{TARGET_LANG}'], df.loc[index][f'description_{TARGET_LANG}']) 

    df.to_excel(f"{RAPORT_PATH}", index=False)
    print("Writing to the API has been completed. The reply code has been written to an xlsx file.")


async def main():
    await save_description_and_title_from_api()
    await translate_from_xlsx()
    await update_translation_from_xlsx()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())    


