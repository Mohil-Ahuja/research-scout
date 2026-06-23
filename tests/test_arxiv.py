from research_scout.arxiv import ArxivClient


def test_parse_arxiv_atom():
    xml = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
      <id>http://arxiv.org/abs/1234.5678v2</id><title> A paper\n title </title>
      <summary> A useful abstract. </summary><author><name>Ada</name></author>
      <category term="cs.AI"/><published>2026-01-01T00:00:00Z</published>
    </entry></feed>'''
    papers = ArxivClient._parse(xml)
    assert papers[0].arxiv_id == "1234.5678v2"
    assert papers[0].title == "A paper title"
    assert papers[0].authors == ["Ada"]

