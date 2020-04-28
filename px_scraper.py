import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import re


def send_request(url):
    result, r_post = '', ''
    s = requests.Session()
    r_get = s.get(url).text
    __VIEWSTATE, argument_list = parse_html(bs(r_get, 'html5lib'))
    if not argument_list:
        return r_get
    index = -1
    while True:
        index += 1
        if len(argument_list) == index:
            result = r_post
            break
        position_list = [m.start() for m in re.finditer(r'(?=\\)', argument_list[index])]
        if position_list:
            __EVENTARGUMENT = argument_list[index][:position_list[0]] + '\\' + argument_list[index][position_list[-1]+1:]
        else:
            __EVENTARGUMENT = argument_list[index]
        print('Folder Index: ', index, ', Total Folders: ', len(argument_list), ', Current Folder: ', __EVENTARGUMENT)
        payload = {'__EVENTTARGET': 'ctl00$ContentPlaceHolderMain$TableOfContent1$TableOfContent1$MenuNavigationTree',
                   '__VIEWSTATE': __VIEWSTATE,
                   '__EVENTARGUMENT': __EVENTARGUMENT
                   }
        r_post = s.post(url=url, data=payload).text
        __VIEWSTATE, tree_argument = parse_html(bs(r_post, 'html5lib'))
        for argument in tree_argument:
            if argument not in argument_list:
                argument_list.append(argument)
    return result


def parse_html(soup):
    __VIEWSTATE = soup.find(id='__VIEWSTATE')['value']
    trees = soup.find_all(attrs={'class': 'AspNet-TreeView-Expand'})
    tree_argument = []
    for tree in trees:
        tree_argument.append(re.search(r"','(.*)'", tree['onclick']).group(0)[3:-1])
    return __VIEWSTATE, tree_argument


def main(url):
    final_result = []
    if '.px' in url:
        px_page = requests.get(url=url).text
        final_result.append({
            url: px_page
        })
        return final_result
    res = send_request(url)
    main_soup = bs(res, 'html5lib')
    leaves = main_soup.find_all(attrs={'class': 'AspNet-TreeView-Leaf'})
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    for leaf in leaves:
        link = '{}{}'.format(domain, leaf.a['href'][1:])
        print(link)
        # link_page = requests.get(url=link).text
        link_page = ''
        final_result.append({
            link: link_page
        })
    return final_result


def rotate():
    initial_url = 'https://www.tilastokeskus.fi/tup/tilastotietokannat/index_en.html'
    initial_soup = bs(requests.get(url=initial_url).content, 'html5lib')
    rows = initial_soup.find(id='content').find('table').find_all('tr')
    for row in rows:
        if row.find_all('a'):
            url = row.find_all('a')[-1]['href']
            print('Started to work on {}'.format(url))
            object = main(url=url)
            print(len(object), object)
            print('Ended to work on {}'.format(url))

if __name__ == '__main__':
    print('---------------------- Start -----------------------')
    url = 'http://pxnet2.stat.fi/PXWeb/pxweb/en/StatFin/'
    object = main(url=url)
    print(len(object), object)
    print('---------------------- The End ----------------------')





