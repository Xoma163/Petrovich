import boto3


class AmazonTranslateAPI:
    AMAZON_REGION = "eu-north-1"

    def get_translate(self, text, target_lang='ru', source_lang='en'):
        if target_lang != 'ru':
            source_lang = 'ru'
        translate = boto3.client(service_name='translate', region_name=self.AMAZON_REGION, use_ssl=True)

        result = translate.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )
        return result.get('TranslatedText')
