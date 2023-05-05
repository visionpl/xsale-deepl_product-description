import connector_db
import pandas as pd 
import requests
import json

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

def translate_deepl