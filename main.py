from argparse import ArgumentParser
from requests import get
from re import search
from json import loads
from urllib3 import disable_warnings
from base64 import b64decode
from tqdm import tqdm

def main(args):
    disable_warnings()

    page_url = f"https://vimm.net/vault/{args.gameid}"
    print(f"Parsing page \x1b[35m{page_url}\x1b[0m...")

    page_contents = get(page_url, verify=False).text

    all_media = loads(search(r"const allMedia=(.+);document", page_contents).group(1))

    for i, media in enumerate(all_media):
        print(f"{i + 1} - \x1b[32m{b64decode(media['GoodTitle']).decode()}\x1b[0m - Serial: \x1b[36m{media['Serial']}\x1b[0m")
    
    index = int(input("\x1b[35mSelect a file: \x1b[0m")) - 1

    media = all_media[index]
    title = b64decode(media['GoodTitle']).decode()

    print(f"Downloading \x1b[32m{title}\x1b[0m (\x1b[33m{media['ZippedText']}\x1b[0m)...")

    game_url = search(r"EJS_gameUrl='(.+)'", get(f"https://vimm.net/vault/?p=play&mediaId={media['ID']}", verify=False).text).group(1)
    print(f"Found download location: \x1b[35m{game_url}\x1b[0m")

    dl = get(game_url, stream=True, headers={"Referer": "https://vimm.net"})
    print(dl.status_code)

    with tqdm(total=int(dl.headers['Content-Length']), unit="B") as prog:
        with open(f"{title}.7z", "wb") as fp:
            for block in dl.iter_content(8192):
                prog.update(len(block))
                fp.write(block)


if __name__ == "__main__":
    parser = ArgumentParser("vimmhoard", description="downloads vimm.net games blocked by stinky copyright lovers")

    parser.add_argument("gameid", help="the game id in vimm.net")

    main(parser.parse_args())