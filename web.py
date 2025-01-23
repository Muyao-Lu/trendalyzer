# from selenium import webdriver
import webbrowser
from math import ceil

import pyautogui
import glob, os, time
import pandas as pd

from pyscreeze import Box

targets = []
names = []
name_map = {}
download_location: str = "Downloads"
last_query = ""
begin_search = False
date = None
country = ""
search_type = ""
search_category = ""

total_downloads: int = 0

def setup(targets_list: list, start_date: str, end_date: str, search_data: dict) -> None:
    global targets, names, name_map, last_query, total_downloads, date, search_type, search_category, country
    targets = targets_list
    names = [str(i) for i in range(ceil(len(targets)/5))]
    name_map = {}
    last_query = ""
    search_type = search_data["stype"]
    search_category = search_data["scat"]
    country = search_data["region"]

    date = start_date + "%20" + end_date

    total_downloads = 0


def find_download_button(region=None) -> Box | None:
    for i in range(100):
        try:
            if region is not None:
                pos = pyautogui.locateOnScreen("search_images\\download.png", grayscale=True, region=region)
            else:
                pos = pyautogui.locateOnScreen("search_images\\download.png", grayscale=True)
            return pos
        except pyautogui.ImageNotFoundException:
            pass
    else:
        raise RuntimeError

def click_download_button(download_button_pos: Box, delay: float|int) -> None:
    home = os.path.expanduser('~')
    dl = os.path.join(home, 'Downloads')
    path_a = dl + "\\*.csv"

    time.sleep(delay)
    pyautogui.click(download_button_pos)
    while True:
        try:
            file = max(glob.glob(path_a), key=os.path.getctime)
            if os.path.basename(file)[:13] == "multiTimeline":
                break
            else:
                raise ValueError
        except ValueError:
            pyautogui.click(download_button_pos)
    time.sleep(delay)
    pyautogui.hotkey("esc")
    time.sleep(delay)
    pyautogui.hotkey("ctrl", "w")


def rename_downloads(name: str) -> None:
    global download_location, total_downloads

    home = os.path.expanduser('~')
    download_location = os.path.join(home, 'Downloads')

    path = download_location + "\\*.csv"
    list_of_files = glob.glob(path)

    list_of_files = glob.glob(path)
    latest_file = max(list_of_files, key=os.path.getctime)
    if os.path.basename(latest_file)[:13] == "multiTimeline":

        path = os.path.join(download_location, latest_file)
        try:
            os.rename(latest_file, str(name) + ".csv")
        except FileExistsError:
            os.remove(str(name) + ".csv")
            try:
                os.remove(str(name))
            except FileNotFoundError:
                pass
            os.rename(latest_file, str(name) + ".csv")


def list_to_str(l: list, start_index: int, end_index : int, iters: int) -> str:
    name_map[int(iters/5)] = l[start_index:end_index]
    string = ""
    for item in l[start_index:end_index]:
        string += item
        string += ","
    return string


def check_homogenous(list_to_check: list) -> bool:
    c = list_to_check[0]
    for item in list_to_check:
        if item != c:
            return False
    else:
        return True

def build_query(target: list[str]) -> list[str]:
    processed_query = []
    if len(target) > 5:
        for i in range(0, len(target), 5):
            if len(target) > i + 5:
                if not check_homogenous(target[i:i+5]):
                    processed_query.append(list_to_str(target, i, i+5, i))
                else:
                    pass
            else:
                if len(target[i:len(target)]) > 1:
                    if not check_homogenous(target[i:i+5]):
                        processed_query.append(list_to_str(target, i, len(target), i))
                    else:
                        pass
                else:
                    if not check_homogenous(target[i:i+5]):
                        processed_query.append(list_to_str(target, i-1, len(target), i))
                    else:
                        pass
    else:
        processed_query.append(list_to_str(target, 0, len(target), 0))

    return processed_query


def search(name_list: list[str], query_to_search: list[str]) -> None:
    global total_downloads, last_query, date
    pos = None
    for item in query_to_search:
        if len(search_category) != 0:
            webbrowser.open("https://trends.google.ca/trends/explore?cat=" + search_category + "&q=" + item + "&date=" + date + "&geo=" + country + "&gprop=" + search_type + "&hl=en", new=1)
        else:
            webbrowser.open("https://trends.google.ca/trends/explore?q=" + item + "&date=" + date + "&geo=" + country + "&gprop=" + search_type + "&hl=en", new=1)

        if pos is None:
            pos = find_download_button()
        else:
            pass
        find_download_button(region=pos)
        click_download_button(pos, 1)
        time.sleep(0.1)
        rename_downloads(name_list[total_downloads])
        total_downloads += 1
        last_query = item


def cleanup():
    list_of_files = glob.glob("*.csv")
    for file in list_of_files:
        if file != "results.csv":
            os.remove(file)


def find_max(items: list[str], name_list: list[str]) -> str:
    cols_dict = {}
    max_item = ""
    maxes_list = []
    for i in range(total_downloads):
        cols_dict = {}
        max_item = ""
        data = pd.read_csv(name_list[i] + ".csv", sep=",", header=1)
        data = pd.DataFrame(data, index=[i for i in range(len(data))])
        for j in range(len(data.iloc[0]) - 1):
            cols_dict[name_map[i][j]] = [item for item in data.iloc[:, j+1]]

        for item in list(cols_dict.keys()):
            if cols_dict[item].count(100) > 0:
                max_item = item
        maxes_list.append(max_item)
    if len(maxes_list) != 1:
        reset_downloads_metrics()
        processed_query = build_query(maxes_list)
        search(maxes_list, processed_query)
        return find_max(maxes_list, maxes_list)
    else:
        return maxes_list[0]


def reset_downloads_metrics():
    global total_downloads, name_map
    total_downloads = 0
    name_map = {}


def compile_final(files: int):
    cols = {}
    data = []
    for i in range(files):
        data = pd.read_csv("final" + str(i) + ".csv", sep=",", header=1)
        data = pd.DataFrame(data, index=[i for i in range(len(data))])
        for j in range(len(data.iloc[0])-1):
            cols[data.iloc[:, j+1].name] = [item for item in data.iloc[:, j+1]]
    cols = pd.DataFrame(cols, index=[item for item in data.iloc[:, 0]])
    cols.to_excel("results.xlsx")
    i = 0
    home_dir = os.path.expanduser('~')
    try:

        home_dir = os.path.expanduser('~')
        while os.path.isfile(home_dir + "\\trendalyzer_results\\results{i}.xlsx".format(i=i)):
            i += 1
            print(i)
        else:
            os.rename("results.xlsx", home_dir + "\\trendalyzer_results\\results{i}.xlsx".format(i=i))
    except FileNotFoundError:
        os.makedirs(os.path.expanduser('~') + "\\trendalyzer_results\\")
        while os.path.isfile(home_dir + "\\trendalyzer_results\\results{i}.xlsx".format(i=i)):
            i += 1
            print(i)
        else:
            os.rename("results.xlsx", home_dir + "\\trendalyzer_results\\results{i}.xlsx".format(i=i))
    return os.path.expanduser('~') + "\\trendalyzer_results"



def main() -> str:
    global names, targets, total_downloads
    compare = None
    cleanup()
    if len(targets) > 5:
        processed_query = build_query(targets)
        search(names, processed_query)
        compare = find_max(targets, names)
        targets.remove(compare)
    else:
        pass

    reset_downloads_metrics()

    shift = 0

    if compare is not None:
        for i in range(4, len(targets), 4):
            targets.insert(i+shift, compare)
            shift += 1
        else:
            targets.append(compare)
    else:
        pass

    processed_query = build_query(targets)
    names = ["final" + str(i) for i in range(len(processed_query))]
    search(names, processed_query)
    save_location = compile_final(total_downloads)
    cleanup()
    return save_location

