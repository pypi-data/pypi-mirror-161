import boto3
import time

client = boto3.client('translate')

def translate (text, slang = 'ko', tlang = 'en'):
    def translate_chunck (buf):
        p = {
            "Text": "\n".join (buf),
            "SourceLanguageCode": slang,
            "TargetLanguageCode": tlang
        }
        response = client.translate_text (**p)
        return response ["TranslatedText"]

    lines = text.split ("\n")
    buf = []
    buflen = 0
    results = []
    while lines:
        llen = len (lines [0].encode ('utf8')) + 1
        if buflen + llen < 5000:
            buf.append (lines.pop (0))
            buflen += llen
        else:
            results.append (translate_chunck (buf))
            buf = []
            buflen = 0
            time.sleep (0.5) # prevent ThrottlingException

    if buf:
        results.append (translate_chunck (buf))
    return '\n'.join (results)
