import connector_db
import pandas as pd 
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

XSALE_ORGANIZATION = connector_db.XSALE_ORGANIZATION
RAPORT_PATH = 'raport.xlsx'
LANGUAGE_ID = 9     # MarketplacePL

def get_description_and_title(id, language_id):
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
        if data[i]['LanguageId'] == language_id:
            return {
                "title": data[i]['Name'],
                "description": data[i]['Description']
                }
        else:
            return {}

def save_description_and_title_from_api():
    df = pd.read_excel(RAPORT_PATH)

    df["title"] = ""
    df["description"] = ""

    for index, row in df.iterrows():
        df.loc[df['xSale_ID'] == df.loc[index]['xSale_ID'], "title"] = get_description_and_title(df.loc[index]['xSale_ID'], LANGUAGE_ID)['title'] 
        df.loc[df['xSale_ID'] == df.loc[index]['xSale_ID'], "description"] = get_description_and_title(df.loc[index]['xSale_ID'], LANGUAGE_ID)['description']

    df.to_excel(f"{RAPORT_PATH}", index=False)

def translate_deepl(text, source_lang, target_lang):    
    url = "https://api-free.deepl.com/v2/translate"
    payload = {'text': text.encode('utf-8'), 'target_lang': target_lang, 'tag_handling': 'html', 'ignore_tags': 'img', 'source_lang': source_lang}
    headers = {
    'Authorization': f'DeepL-Auth-Key {os.environ.get("DEEPL_KEY")}',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)

    return data["translations"][0]["text"]

def translate_from_xlsx():
    
    df = pd.read_excel(RAPORT_PATH)

    source_lang = 'PL'
    target_lang = 'EN'

    df[f"title_{target_lang}"] = ""
    df[f"description_{target_lang}"] = ""

    for index, row in df.iterrows():
        df.loc[df['title'] == df.loc[index]['title'], f"title_{target_lang}"] = translate_deepl(df.loc[index]['title'], source_lang, target_lang)
        df.loc[df['description'] == df.loc[index]['description'], f"description_{target_lang}"] = translate_deepl(df.loc[index]['description'], source_lang, target_lang)

    df.to_excel(f"{RAPORT_PATH}", index=False)
    print("done")



