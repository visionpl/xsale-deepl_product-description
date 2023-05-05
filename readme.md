# xSale & DeepL integration for translate atricles



## User manual
1. Connect with API xSale & save DeepL API KEY to .env
2. Prepare the item id and save it in the raport.xlsx file in the xSale_ID column
3. Set required variables:
    1. `LANGUAGE_ID` - the identifier of the translation from xSale from which we will download the description and title
    2. `TARGET_LANGUAGE_ID` - the identifier of the translation from xSale which we will save new translation
    3. `SOURCE_LANG` e.g. 'PL'
    4. `TARGET_LANG` e.g. 'EN'  (more information about language codes is [here](https://www.deepl.com/pl/docs-api/translate-text/translate-text/))
4. Run `save_description_and_title_from_api()` for download description and title from xSale and save to raport.xlsx
5. Run `translate_from_xlsx()` for translate title and description from source language to target language and save into raport.xlsx
6. Run `update_translation_from_xlsx()` for update target language id (translate in xSale) via xSale API and save reponse code into raport.xlsx