import os
import sys
import time
import urllib3
import requests
from bs4 import BeautifulSoup


def banner():
    # App banner
    banner_ascii = """
  /$$$$$$            /$$                         /$$   /$$
 /$$__  $$          |__/                        | $$  / $$
| $$  \ $$ /$$$$$$$  /$$ /$$$$$$/$$$$   /$$$$$$ |  $$/ $$/
| $$$$$$$$| $$__  $$| $$| $$_  $$_  $$ /$$__  $$ \  $$$$/
| $$__  $$| $$  \ $$| $$| $$ \ $$ \ $$| $$$$$$$$  >$$  $$
| $$  | $$| $$  | $$| $$| $$ | $$ | $$| $$_____/ /$$/\  $$
| $$  | $$| $$  | $$| $$| $$ | $$ | $$|  $$$$$$$| $$  \ $$
|__/  |__/|__/  |__/|__/|__/ |__/ |__/ \_______/|__/  |__/
"""

    return banner_ascii


class BadLinkException(Exception):
    def __init__(self, ok):
        self.ok = ok


def name_parser(name):
    new_name = ("]".join(name.split("]")[1:2]) + "]").strip()
    if new_name in ["[RapidBot]", "[]"]:
        new_name = os.path.basename(name)
    return new_name


def get_search_result(search_item):
    # search for a given anime using WP Rest API since cloudflare recaptcha can be a hassle
    search_url = "https://www.animeout.xyz/wp-json/wp/v2/posts"

    # set to firefox client
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # search parameter
    params = {
        "search": search_item
    }

    # array of contexts searched from api
    search_result = []
    r = requests.get(search_url, params=params, headers=headers).json()

    # loop through (& functions)  each post found in json
    for post in r:
        post_title = post['title']['rendered']
        # condition for a more relevant result. as per WP API response can be ambiguous
        if search_item.split(' ', 1)[0].lower() in post_title.lower():
            print(post_title)
            search_result.append({
                'name': post_title,
                'raw-content': post['content']['rendered']
            })

    return search_result


def get_anime_episodes(anime_content):
    # parse the anime content to html
    anime_result = BeautifulSoup(anime_content, "html.parser")

    episodes = []
    for i in anime_result.findAll("a"):
        try:
            if i["href"][-3:] in ["mkv", "mp4]"]:
                episodes.append(i["href"])
        except:
            pass
    return episodes


def get_download_url(anime_url):
    # get the video download URL
    r = requests.get(anime_url)
    pre_download_page = BeautifulSoup(r.text, "html.parser")

    pre_download_url = pre_download_page.find("a", {"class": "btn"})["href"]

    r = requests.get(pre_download_url)
    download_page = BeautifulSoup(r.text, "html.parser")

    # using a try catch because .text returned empty on some OS
    try:
        download_url = download_page.find(
            "script", {"src": None}).text.split('"')[1]
    except:
        download_url = download_page.find(
            "script", {"src": None}).contents[0].split('"')[1]

    return download_url


def download_episode(anime_name, download_url, i=1):
    # using urllib3 rather wget as wget seems quite redundant for mkv file download
    http = urllib3.PoolManager()

    # prevent eyesoring error printout
    urllib3.disable_warnings()

    # download anime and store in the folder the same name
    # don't download files that exist and clear tmp files after download
    filename = os.path.basename(download_url)
    download_path = os.path.join(anime_name, filename)
    if not os.path.exists(download_path):
        # Due to the existence of multiple streams of download
        # we prepare a download url with i as subdomain index variant
        _url = download_url.replace(" ", "%20")
        _url = "https://pub" + str(i) + ".animeout.com" + \
            _url[_url.find('/series'):]
        print("\nTrying " + _url + " ...")

        try:
            # send a download request with current url
            r = http.request('GET', _url, preload_content=False)

            if r.status == 404:
                raise BadLinkException('bad link')

            print('Gotten Verified Download link!')
            print("Downloading", name_parser(filename))

            # download if response of download url request is ok
            with open(download_path, 'wb') as out:
                while True:
                    data = r.read()
                    if not data:
                        break
                    out.write(data)

            r.release_conn()
            clear_tmp(anime_name)
        except BadLinkException as e:
            print(e)
            n = i + 1
            download_episode(anime_name, download_url, n)


def make_directory(anime_name):
    # create folder to store anime
    if not os.path.exists(anime_name):
        os.mkdir(anime_name)


def clear_tmp(directory):
    # clear tmp files
    for i in os.listdir(directory):
        if i[-3:] == "tmp":
            os.remove(os.path.join(directory, i))


def check_update():
    # check if there's a higher version of the app
    commit_count = 44
    repo_commit_count = len(requests.get(
        "https://api.github.com/repos/LordGhostX/animeX-v2/commits?per_page=100").json())
    if commit_count != repo_commit_count:
        print("\nYou are using an outdated version of animeX. Please update from "
              "https://github.com/LordGhostX/animeX-v2\n")
    else:
        print("\nYou're ready to go :)\n")

def get_user_choice(cap):
    LIST_OF_ALLOWED_DIGITS = [d for d in "0123456789"]
    choice = input("\nWhich one? Enter the number of your choice ::: ")

    # ensure choice is not empty
    if len(choice) == 0:
        return get_user_choice(cap)

    # separate each digit of the choice string
    digits = [c for c in choice]

    # look for any element that isn't a digit
    for digit in digits:
        if digit not in LIST_OF_ALLOWED_DIGITS:
            print("Your input is invalid! pick another number")
            return get_user_choice(cap)
    
    if int(choice) > cap or int(choice) == 0:
        print("Your input is invalid! pick another number")
        return get_user_choice(cap)
    
    return abs(int(
        choice))

if __name__ == "__main__":
    print(banner())
    print("\nAll anime are gotten from www.animeout.xyz/")
    check_update()

    if len(sys.argv) == 2:
        anime_name = sys.argv[1]
    else:
        anime_name = input("\nWhat anime do you wanna download today ::: ")

    search_result = get_search_result(anime_name)
    if len(search_result) == 0:
        print(
            "We couldn't find the anime you searched for, check the spelling and try again")
        exit()

    print("\nSearch results for", anime_name)
    for i, j in enumerate(search_result):
        print(i + 1, " - " + j["name"])
    
    choice = get_user_choice( len(search_result) )

    anime = search_result[choice - 1]
    anime["name"] = "".join(
        [i if i.isalnum() or i in [")", "(", " "] else "-" for i in anime["name"]])

    # using the raw anime content rather than url since it contains all that is needed
    episodes = get_anime_episodes(anime["raw-content"])
    getall = input(
        "\nanimeX found {} episodes for the requested anime\nDo you want to get all episodes? ::: (Y/N) ".format(len(episodes))).lower()
    make_directory(anime["name"])
    print("\nPress CTRL + C to cancel your download at any time")

    splice_download = False
    if getall in ['n', 'no']:
        try:
            options = int(input(
                "\nWhat kind of action would you like to perform: \n1) Get latest episode \n2) See other download Options\nChoose an option ::: "))
        except ValueError:
            print("Invalid Entry, enter in '1' or '2'")
            options = int(input(
                "\nWhat kind of action would you like to perform: \n1) Get latest episode \n2) See other download Options\nChoose an option ::: "))
        if options == 1:
            print(
                "Aye aye captain, downloading latest episode, hit CTRL + C to cancel anytime")
            latest = episodes[-1]
            download_url = get_download_url(latest)
            download_episode(anime["name"], download_url)
        elif options == 2:
            for i, j in enumerate(episodes, 1):
                print(i, name_parser(j))
            episode_no = input(
                "\nYou can choose an episode from the list above or specify a range of anime to download in the format start:end e.g 10:20 or a list seperated by comma e.g 1,5,7,10\nChoose episode number::: ")
            if len(episode_no.split(":")) == 1:
                if len(episode_no.split(",")) == 1:
                    download_url = get_download_url(
                        episodes[int(episode_no.split(":")[0]) - 1])
                    start = time.perf_counter()
                    download_episode(anime["name"], download_url)
                    end = time.perf_counter()
                    print(f'\ncompleted download in {int(end-start)} seconds')
                else:
                    episode_list = [int(i) - 1 for i in episode_no.split(",")]
                    episodes = [j for i, j in enumerate(
                        episodes) if i in episode_list]
                    splice_download = True
            else:
                start_ep, end_ep = [int(i) for i in episode_no.split(":")[:2]]
                episodes = episodes[start_ep - 1:end_ep]
                splice_download = True
        else:
            print("Invalid Entry, enter in '1' or '2'")
            options = int(input(
                "\nWhat kind of action would you like to perform:\n1) Get latest episode\n2) See other Options\nChoose an option ::: "))
    if getall in ['yes', 'y'] or splice_download:
        start = time.perf_counter()
        for i in episodes:
            download_url = get_download_url(i)
            download_episode(anime["name"], download_url)
        end = time.perf_counter()
        print(f'\ncompleted download in {int(end-start)} seconds')
    print("\nFinished downloading all episodes of", anime["name"])
