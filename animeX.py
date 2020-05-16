import os
import sys
import requests
import wget
from bs4 import BeautifulSoup


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
    anime_section = anime_result.find("div", {"class": "article-content"})

    episodes = []
    for i in anime_section.findAll("a"):
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
        #wget.download(download_url, download_path)
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


if __name__ == "__main__":
    print("Anime X v2.0\nAll anime are gotten from www.animeout.xyz/")
    if len(sys.argv) == 2:
        anime_name = sys.argv[1]
    else:
        anime_name = input("\nWhat anime do you wanna download today::: ")
    search_result = get_search_result(anime_name)

    print("\nSearch results for", anime_name)
    for i, j in enumerate(search_result):
        print(i + 1, " - " + j["name"])
    choice = int(input("\nWhich one? Enter the number of your choice::: "))

    anime = search_result[choice - 1]
    episodes = get_anime_episodes(anime["url"])

    make_directory(anime["name"])
    for i in episodes:
        download_url = get_download_url(i)
        download_episode(anime["name"], download_url)
