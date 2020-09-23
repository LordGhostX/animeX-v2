import requests
import wget
import os
import sys
import time
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


def name_parser(name):
    return ("]".join(name.split("]")[1:2]) + "]").strip()


def get_search_result(search_item):
    # search for a given anime
    search_url = "https://www.animeout.xyz/"
    params = {
        "s": search_item
    }
    r = requests.get(search_url, params=params)
    search_result_html = BeautifulSoup(r.text, "html.parser")

    search_result = []
    for i in search_result_html.findAll("h3", {"class": "post-title"}):
        search_result.append({
            "name": i.text,
            "url": i.find("a")["href"]
        })
    return search_result


def get_anime_episodes(anime_url):
    # get the episodes in the anime by parsing all links that are videos
    r = requests.get(anime_url)
    anime_result = BeautifulSoup(r.text, "html.parser")

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


def download_episode(anime_name, download_url):
    # download anime and store in the folder the same name
    # don't download files that exist and clear tmp files after download
    filename = os.path.basename(download_url)
    download_path = os.path.join(anime_name, filename)
    if not os.path.exists(download_path):
        print("\nDownloading", filename)
        wget.download(download_url, download_path)
        clear_tmp(anime_name)


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
    commit_count = 19
    repo_commit_count = len(requests.get(
        "https://api.github.com/repos/LordGhostX/animeX-v2/commits").json())
    if commit_count != repo_commit_count:
        print("\nYou are using an outdated version of animeX. Please update from "
              "https://github.com/LordGhostX/animeX-v2")
    else:
        print("\nYou're ready to go :)")


if __name__ == "__main__":
    print(banner())
    print("\nAll anime are gotten from www.animeout.xyz/")
    check_update()

    if len(sys.argv) == 2:
        anime_name = sys.argv[1]
    else:
        anime_name = input("\nWhat anime do you wanna download today::: ")

    search_result = get_search_result(anime_name)
    if len(search_result) == 0:
        print(
            "We couldn't find the anime you searched for, check the spelling and try again")
        exit()

    print("\nSearch results for", anime_name)
    for i, j in enumerate(search_result, 1):
        print(i, " - " + j["name"])
    try:
        choice = int(input("\nWhich one? Enter the number of your choice::: "))
    except ValueError:
        print("Invalid Entry! please enter a number that corresponds to an option listed.")
        choice = int(input("\nWhich one? Enter the number of your choice::: "))

    anime = search_result[choice - 1]
    anime["name"] = "".join(
        [i if i.isalnum() or i in [")", "(", " "] else "-" for i in anime["name"]])

    episodes = get_anime_episodes(anime["url"])
    getall = input(
        "\nanimeX found {} episodes for the requested anime\nDo you want to get all episodes?::: (Y/N)  ".format(len(episodes))).lower()
    make_directory(anime["name"])
    print("\nPress CTRL + C to cancel your download at any time")

    splice_download = False
    if getall in ['n', 'no']:
        for i, j in enumerate(episodes, 1):
            print(i, name_parser(j))
        episode_no = input(
            "\nYou can specify a range of anime to download in the format ep-start:ep-end e.g 10:20\nChoose episode number::: ")
        if len(episode_no.split(":")) == 1:
            download_url = get_download_url(
                episodes[int(episode_no.split(":")[0]) - 1])
            start = time.perf_counter()
            download_episode(anime["name"], download_url)
            end = time.perf_counter()
            print(f'completed download in {end-start} minutes(s)')
        else:
            start_ep, end_ep = [int(i) for i in episode_no.split(":")[:2]]
            episodes = episodes[start_ep - 1:end_ep]
            splice_download = True
    if (getall in ['yes', 'y']) or splice_download:
        start = time.perf_counter()
        for i in episodes:
            download_url = get_download_url(i)
            download_episode(anime["name"], download_url)
        end = time.perf_counter()
        print(f'completed download in {end-start} minutes(s)')
    print("\nFinished downloading all episodes of", anime["name"])
