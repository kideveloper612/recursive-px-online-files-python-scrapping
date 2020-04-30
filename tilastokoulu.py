import requests
from bs4 import BeautifulSoup as BS
from requests.exceptions import ConnectionError, ConnectTimeout


def send_request(url):
    """
    Send request to tilastokoulu.stat.fi
    :param url: url for request
    :return: content of page
    """
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/80.0.3987.122 Safari/537.36'
    }
    try:
        res = requests.get(url=url, headers=header).content
        result.append({
            'url': url,
            'html': res
        })
        print('Count: {}, '.format(len(total_urls)), url)
        return res
    except (ConnectionError, ConnectTimeout) as e:
        raise Exception('Occurred in Request')


def check_exist(check_url):
    """
    Check if the url exist among the urls already were done
    :param check_url: url for checking
    :return: Boolean
    """
    return check_url in total_urls


def middle(middle_texts):
    """
    Loop sub urls on page including dropdown box.
    :param middle_texts: Anchor tags on origin part of side bar.
    :return:
    """
    for middle_text in middle_texts:
        if not middle_text.has_attr('href') or 'lesson_id' not in middle_text['href']:  # skip unnecessary urls
            continue
        middle_url = middle_text['href']
        if check_exist(middle_url) or 'http' in middle_url:  # skip if this url was already done
            continue
        if 'verkkokoulu_v2.xql' in middle_url:
            middle_url = landing_url + middle_url
            if check_exist(middle_url):  # skip if this url was already done
                continue
            total_urls.append(middle_url)
            middle_soup = BS(send_request(middle_url), 'html5lib')
            subject_options = middle_soup.find(id='subject_id').find_all('option')
            for subject_option in subject_options:
                if not subject_option.has_attr('value'):
                    continue
                subject_value = subject_option['value']
                if not subject_value:
                    subject_id = 0
                else:
                    subject_id = subject_value
                subject_url = middle_url + '&subject_id={}'.format(subject_id)
                if check_exist(subject_url):  # skip if this url was already done
                    continue
                total_urls.append(subject_url)
                # Request for leaf url
                send_request(subject_url)
        else:
            middle_url = landing_url + 'verkkokoulu_v2.xql' + middle_url
            if check_exist(middle_url):  # skip if this url was already done
                continue
            total_urls.append(middle_url)
            # Request for leaf url
            send_request(middle_url)


def origin_pages(origin_lis):
    """
    Loop urls on origin page
    :param origin_lis:
    :return:
    """
    for ori in origin_lis:
        ori_url = landing_url + ori['href']
        if check_exist(ori_url):
            continue
        total_urls.append(ori_url)
        ori_soup = BS(send_request(ori_url), 'html5lib')
        middle_texts = ori_soup.select('#middle #text a')
        middle(middle_texts=middle_texts)


def other_pages(other_lis):
    """
    Loop urls on other page
    :param other_lis:
    :return:
    """
    for oth in other_lis:
        oth_url = 'https://' + oth['href'][2:]
        if check_exist(oth_url):
            continue
        total_urls.append(oth_url)
        send_request(url=oth_url)


def main():
    """
    Main function of this script
    :return:
    """
    total_urls.append(landing_url)
    soup = BS(send_request(landing_url), 'html5lib')
    left_nav = soup.find(id='left-navigation').find_all('ul')
    origin_pages(left_nav[0].select('ul > li > a'))  # Call function for origin urls
    other_pages(left_nav[1].select('ul > li > a'))  # Call function for urls of other part


if __name__ == "__main__":
    print('------------- Started -------------')
    result = []  # Initialize variable for final object
    total_urls = []  # List of request urls
    landing_url = 'https://tilastokoulu.stat.fi/'
    main()
    for r in result:
        print(r)
    print('Result of {} urls finally'.format(len(total_urls)))
    print('------------- The End -------------')
