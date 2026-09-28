"""Read public SuccessFactors career tables with strict pagination checks."""
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode, urljoin, urlsplit

from .classify import eligible, plain
from .regional import record


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def has_class(self, name):
        return name in self.attrs.get('class', '').split()

    def find(self, predicate):
        if predicate(self):
            yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.find(predicate)

    def text(self):
        return ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in self.children).split())


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def nodes(root, **attrs):
    return list(root.find(lambda n: all(n.attrs.get(k) == v for k,v in attrs.items())))


def search_page(html):
    root = Document(html).root
    empty = nodes(root, id='noresults')
    if len(empty)==1 and 'There are currently no open positions matching' in empty[0].text():
        # SAP may append unrelated recent-job suggestions below this notice.
        return 0,0,0,[]
    rows = list(root.find(lambda n: n.tag == 'tr' and n.has_class('data-row')))
    ranges = set(re.findall(r'Results\s+(\d+)\s*[–-]\s*(\d+)\s+of\s+([\d,]+)', plain(html)))
    if len(ranges) != 1:
        raise ValueError('Missing or ambiguous SuccessFactors result count')
    start, end, total = [int(v.replace(',','')) for v in ranges.pop()]
    if len(rows) != end-start+1 or not (1 <= start <= end <= total):
        raise ValueError('SuccessFactors page count mismatch')
    parsed=[]
    for row in rows:
        links = {(n.attrs.get('href'),n.text()) for n in row.find(lambda n:n.tag=='a' and n.has_class('jobTitle-link'))}
        if len(links)!=1:
            raise ValueError('Missing or ambiguous job link')
        href,title=links.pop()
        identity=re.search(r'/job/[^/?]+/(\d+)/?$',href or '')
        location_nodes=list(row.find(lambda n:n.tag=='td' and n.has_class('colLocation')))
        departments=list(row.find(lambda n:n.tag=='td' and n.has_class('colDepartment')))
        if not identity or not title or len(location_nodes)!=1 or not location_nodes[0].text():
            raise ValueError('Missing job identity, title or location')
        parsed.append(dict(identifier=identity[1],title=title,path=href,
                           location=location_nodes[0].text(),department=departments[0].text() if len(departments)==1 else None))
    return start,end,total,parsed


def collect(company, snapshot, text):
    base=company['careers_url']
    offset, expected, seen = 0, None, set()
    for _ in range(100):
        url=base.rstrip('/')+'/search/?'+urlencode(dict(q='intern',locationsearch='Singapore',startrow=offset,
                                                      sortColumn='referencedate',sortDirection='desc'))
        start,end,total,page=search_page(text(url))
        if total==0 and offset==0:
            snapshot.complete=True
            return
        if start!=offset+1 or (expected is not None and total!=expected):
            raise ValueError('SuccessFactors pagination changed')
        expected=total
        for row in page:
            if row['identifier'] in seen:
                raise ValueError('Repeated SuccessFactors posting ID')
            seen.add(row['identifier'])
            if not re.search(r'\bintern(?:ships?)?\b',row['title'],re.I):
                continue
            if company.get('departments'):
                if not row['department']:
                    raise ValueError('Missing employer department on shared board')
                if row['department'] not in company['departments']:
                    continue
            # These career sites display the ISO country code in the location cell.
            country='SG' if re.search(r'(?:^|,)\s*SG(?:\s*,\s*\d{6})?\s*$',row['location']) else None
            job_url=urljoin(base,row['path'])
            if urlsplit(job_url).netloc != urlsplit(base).netloc:
                raise ValueError('Job link leaves official career host')
            job=record(company,row['identifier'],row['title'],row['location'],job_url,country=country)
            if eligible(job):
                root=Document(text(job_url)).root
                titles=nodes(root,itemprop='title')
                descriptions=list(root.find(lambda n:n.has_class('jobdescription')))
                if len(titles)!=1 or titles[0].text()!=row['title'] or len(descriptions)!=1 or not descriptions[0].text():
                    raise ValueError('Incomplete or mismatched SuccessFactors job detail')
                job['description']=descriptions[0].text()
                dates=nodes(root,itemprop='datePosted')
                if len(dates)==1 and dates[0].attrs.get('content'):
                    value=dates[0].attrs['content']
                    job['posted_at']=datetime.strptime(value,'%a %b %d %H:%M:%S UTC %Y').replace(tzinfo=timezone.utc).isoformat()
            snapshot.jobs.append(job)
        if end==total:
            if len(seen)!=total:
                raise ValueError('SuccessFactors total mismatch')
            snapshot.complete=True
            return
        offset=end
    raise ValueError('SuccessFactors pagination cap reached')
