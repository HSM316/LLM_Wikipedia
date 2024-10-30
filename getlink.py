import requests
from bs4 import BeautifulSoup


def get_external_links_and_images(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        external_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki'):
                external_links.append("https://en.wikipedia.org"+href)

        image_links = []
        for img_tag in soup.find_all('img'):
            img_src = img_tag.get('src')
            if img_src:
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = 'https://en.wikipedia.org' + img_src
                image_links.append(img_src)

        return {
            'external_links': external_links,
            'image_links': image_links
        }

    except Exception as e:
        print(f"Error processing page: {e}")
        return None


page_url = "https://en.wikipedia.org/wiki/Valladolid"
resources = get_external_links_and_images(page_url)

if resources:
    print("External Links:")
    for link in resources['external_links']:
        print(link)

    print("\nImage Links:")
    for img in resources['image_links']:
        print(img)
