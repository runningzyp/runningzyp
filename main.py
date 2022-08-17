"""
WakaTime progress visualizer
"""

import os
import base64
import datetime
from github import Github
import github
import requests

GIST_MAX_ROW_LENGTH = 50
GRAPH_LENGTH = 25
TEXT_LENGTH = 16

gist = "a98736910e9336e2c13700caa3c0a6f3"
waka_key = os.getenv("WAKATIME_API_KEY") or ""
ghtoken = (
    os.getenv("GH_TOKEN") or ""
)  # gist only
show_title = False
commit_message = "update gists"
blocks = "░▒▓█"
show_time = True


def this_week() -> str:
    """Returns a week streak"""
    week_end = datetime.datetime.today() - datetime.timedelta(days=1)
    week_start = week_end - datetime.timedelta(days=6)
    return f"📊Code-Life : {week_start.strftime('%d %B')} - {week_end.strftime('%d %B')}"


def make_graph(percent: float, blocks: str, length: int = GRAPH_LENGTH) -> str:
    divs = len(blocks) - 1
    graph = blocks[-1] * int(percent / 100 * length + 0.5 / divs)
    remainder_block = int((percent / 100 * length - len(graph)) * divs + 0.5)
    if remainder_block > 0:
        graph += blocks[remainder_block]
    graph += blocks[0] * (length - len(graph))
    return graph


def get_stats() -> str:
    encoded_key: str = str(base64.b64encode(waka_key.encode("utf-8")), "utf-8")
    data = requests.get(
        "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        headers={"Authorization": f"Basic {encoded_key}"},
    ).json()
    lang_data = data["data"]["languages"]
    ln_graph = GRAPH_LENGTH
    data_list = []

    try:
        pad = max([len(l["name"]) for l in lang_data[:5]])
    except ValueError:
        return "No Activity tracked this Week\n"

    for lang in lang_data[:5]:
        name = lang["name"].ljust(8, " ") if pad < 8 else lang["name"].ljust(10, " ")

        hours = lang["hours"]  # 时长
        minutes = lang["minutes"]

        if not hours and not minutes:
            continue
        if show_time:
            hour_str = f"{hours}h," if hours else ""
            minute_str = f"{minutes}m" if minutes else ""
            code_time = f"{hour_str}{minute_str}".rjust(7, " ")
        else:
            code_time = ""

        percent = lang["percent"]  # 百分比
        fmt_percent = f"{percent:.2f}%".rjust(6, "0")

        text = (
            f"{name} {make_graph(percent, blocks, ln_graph)}  {code_time} {fmt_percent}"
        )

        data_list.append(text)

    print("Graph Generated")
    data = "\n".join(data_list)
    if show_title:
        return this_week() + data + "\n"
    else:
        if not data:
            return "No Activity tracked this Week\n"
        return data + "\n"


if __name__ == "__main__":
    print("GH_TOKEN: " + ghtoken)
    print("WAKATIME_API_KEY: " + waka_key)
    g = Github(ghtoken)
    g = g.get_gist(gist)
    files = g.files
    waka_stats = get_stats()
    print(waka_stats)
    g.edit(
        description=this_week(),
        files={"📊Code-Life": github.InputFileContent(content=waka_stats)},
    )
