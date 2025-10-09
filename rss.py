from datetime import datetime
import hashlib
import xml.etree.ElementTree as ET

# in seconds. we don't enforce rate limits, but this is the value we tell clients to respect (and most do)
TIME_TO_LIVE = 60 * 30

def make_rss_feed(headers):
    # https://www.rssboard.org/rss-specification
    # https://www.rssboard.org/rss-validator/

    root = ET.Element('rss')
    root.set('version', '2.0')
    channel = ET.SubElement(root, 'channel')

    ET.SubElement(channel, 'title').text       = 'CUII Liste - Gesperrte Domains'
    ET.SubElement(channel, 'link').text        = 'https://cuiiliste.de/domains'
    ET.SubElement(channel, 'description').text = 'Die CUII Liste zeigt dir, welche Domains von der CUII gesperrt sind'
    ET.SubElement(channel, 'language').text    = 'de'
    ET.SubElement(channel, 'generator').text   = 'https://github.com/lina-x64/cuiiliste/blob/master/rss.py'
    ET.SubElement(channel, 'docs').text        = 'https://www.rssboard.org/rss-specification'
    ET.SubElement(channel, 'ttl').text         = str(TIME_TO_LIVE // 60)


    xml = ET.tostring(root, encoding='unicode', xml_declaration=True, short_empty_elements=False)
    sha256 = hashlib.sha256(xml.encode()).hexdigest()
    # the extra quotes are required by spec
    etag = f'"{sha256}"'
    if 'If-None-Match' in headers.keys():
        if headers['If-None-Match'] == '*' or etag in headers['If-None-Match'].split(', '):
            return (
                '',
                304,
                { "ETag": etag }
            )
    return (
        xml,
        200,
        {
            "Content-Type": "application/xml",
            "ETag": etag
            # many servers implement ETag (and If-None-Match) as well as Last-Modified (and If-Modified-Since),
            # but either one is sufficient for almost any purpose, and parsing/formatting dates is way more
            # annoying than just hashing our deterministically-generated xml
        }
    )

if __name__ == '__main__':
    print(make_rss_feed({}))