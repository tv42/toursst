from twisted.trial import unittest
from twisted.web import microdom
from TouRSSt import toursst, fetch

class RSSParseKnownInputs(unittest.TestCase):
    knownValues=[ # input, expected_result
	('''
<?xml version="1.0"?>

<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN"
"http://my.netscape.com/publish/formats/rss-0.91.dtd">

<rss version="0.91">
 <channel>
  <title>Main title</title>
  <description>Main description</description>
  <link>http://url.invalid/main</link>
  <language>en-us</language>
  <image>
   <title>Image title</title>
   <url>http://url.invalid/image</url>
   <link>http://url.invalid/imagelink</link>
  </image>

  <item>
   <title>Item 1</title>
   <link>http://url.invalid/item1</link>
   <description>Description for item 1.</description>
  </item>

  <item>
   <title>Item 2</title>
   <link>http://url.invalid/item2</link>
   <description>Description for item 2.</description>
  </item>
 </channel>
</rss>
''',
         { 'title': 'Main title',
           'description': 'Main description',
           'link': 'http://url.invalid/main',
           #'language': 'en-us',
           #'image': { 'title': 'Image title',
           #           'url': 'http://url.invalid/image',
           #           'link': 'http://url.invalid/imagelink',
           #           },
           'updatePeriod': 3600,
           'items': [ { 'title': 'Item 1',
                        'link': 'http://url.invalid/item1',
                        'description': 'Description for item 1.',
                        'hash': '467501e35213c263ea3802597cb7a084955762dd',
                        },
                      { 'title': 'Item 2',
                        'link': 'http://url.invalid/item2',
                        'description': 'Description for item 2.',
                        'hash': 'a069fd42ea8e50ea0baad66a2adaf85cc5437c11',
                        },
                      ],
           }
         ),


        ('''
<?xml version="1.0" encoding="ISO-8859-1"?>

<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:syn="http://purl.org/rss/1.0/modules/syndication/"
>

<channel rdf:about="http://newsforge.com/">
<title>Main title</title>
<link>http://url.invalid/main</link>
<description>Main description</description>
<dc:language>en-us</dc:language>
<dc:rights>Copyright &#169; 2002, SomeCopyrighter</dc:rights>
<dc:date>2003-06-20T12:42:01+00:00</dc:date>
<dc:publisher>SomePublisher</dc:publisher>
<dc:creator>MainCreator</dc:creator>
<dc:subject>Technology</dc:subject>
<syn:updatePeriod>hourly</syn:updatePeriod>
<syn:updateFrequency>1</syn:updateFrequency>
<syn:updateBase>1970-01-01T00:00+00:00</syn:updateBase>
<items>
 <rdf:Seq>
  <rdf:li rdf:resource="http://url.invalid/item1" />
  <rdf:li rdf:resource="http://url.invalid/item2" />
 </rdf:Seq>
</items>
<image rdf:resource="http://url.invalid/image" />
<textinput rdf:resource="http://url.invalid/textinput-e.g.-search" />
</channel>

<image rdf:about="http://url.invalid/image">
<title>Image title</title>
<url>http://url.invalid/image</url>
<link>http://url.invalid/imagelink</link>
</image>

<item rdf:about="http://url.invalid/item1">
<title>Item 1</title>
<link>http://url.invalid/item1</link>
<description>Another description for item 1.</description>
<dc:creator>CreatorOfItem1</dc:creator>
<dc:subject>SubjectOfItem1</dc:subject>
<dc:date>2003-06-19T08:53:59+00:00</dc:date>
</item>

<item rdf:about="http://url.invalid/item2">
<title>Item 2</title>
<link>http://url.invalid/item2</link>
<description>Another description for item 2.</description>
<dc:creator>CreatorOfItem2</dc:creator>
<dc:subject>SubjectOfItem2</dc:subject>
<dc:date>2003-06-18T12:19:20+00:00</dc:date>
</item>

<textinput rdf:about="http://url.invalid/textinput-e.g.-search">
<title>Search title</title>
<description>Search description</description>
<name>query</name>
<link>http://url.invalid/searchlink</link>
</textinput>

</rdf:RDF>
''',
         { 'title': 'Main title',
           'description': 'Main description',
           'link': 'http://url.invalid/main',
           #'language': 'en-us',
           #'image': { 'title': 'Image title',
           #           'url': 'http://url.invalid/image',
           #           'link': 'http://url.invalid/imagelink',
           #           },
           'updatePeriod': 3600,
           'items': [ { 'title': 'Item 1',
                        'link': 'http://url.invalid/item1',
                        'description': 'Another description for item 1.',
                        'hash': '467501e35213c263ea3802597cb7a084955762dd',
                        },
                      { 'title': 'Item 2',
                        'link': 'http://url.invalid/item2',
                        'description': 'Another description for item 2.',
                        'hash': 'a069fd42ea8e50ea0baad66a2adaf85cc5437c11',
                        },
                      ],
           }
         ),
	]

    def testParse(self):
	"""Parsing known input gives expected results."""
        for input, result in self.knownValues:
            dom = microdom.parseString(input)
            rss = fetch.RSSParser(dom, 0)
            self.assertEquals(result['title'], rss.getTitle())
            self.assertEquals(result['description'], rss.getDescription())
            self.assertEquals(result['link'], rss.getURL())
            self.assertEquals(result['updatePeriod'], rss.get_update_period())

            gotItems = rss.getItems()
            wantedItems = list(result['items'])
            self.assertEquals(len(wantedItems), len(gotItems))

            for got, wanted in zip(gotItems, wantedItems):
                self.assertEquals(wanted['title'], got.getTitle())
                self.assertEquals(wanted['link'], got.getURL())
                self.assertEquals(wanted['description'], got.getDescription())
                self.assertEquals(wanted['hash'], got.hash())
