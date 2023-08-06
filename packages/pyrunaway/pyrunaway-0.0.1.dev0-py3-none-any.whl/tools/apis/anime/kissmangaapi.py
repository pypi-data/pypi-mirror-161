import aiohttp

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("'bs4' module not found")
    BeautifulSoup = None


class KissMangaApi:
    def __init__(self, query, mangaid, chapternum):
        self.query = query
        self.mangaid = mangaid
        self.chapternum = chapternum

    # returns list of tuples cotaining name of manga and its id [(name1, id1), (name2, id2)]
    async def get_search_results(query):
        try:
            url = f"http://kissmanga.nl/search?q={query}"
            async with aiohttp.ClientSession() as _client:
                response = await _client.get(url)
            response_html = await response.text()
            soup = BeautifulSoup(response_html, "lxml")
            mangas = soup.findAll("div", class_="media mainpage-manga")
            res_search_list = []
            for manga in mangas:
                manganame = manga.a["title"]
                link = manga.a["href"]
                split = link.split("/")
                split2 = split[-1].split("?")
                mangaid = split2[0]
                result = (manganame, mangaid)
                res_search_list.append(result)
            if res_search_list == []:
                return "Nothing Found"
            return res_search_list
        except aiohttp.ClientConnectorError:
            return "Check the host's network Connection"

    # returns list of [Name of manga, Display-image link, list of genres, latest chapter number]
    async def get_manga_details(mangaid):
        try:
            url = f"http://kissmanga.nl/manga/{mangaid}"
            async with aiohttp.ClientSession() as _client:
                response = await _client.get(url)
            response_html = await response.text()
            soup = BeautifulSoup(response_html, "lxml")
            manga_title = soup.find("h1", class_="title-manga")
            image = soup.find("div", class_="media-left cover-detail").img
            image_link = image["src"]
            genre_list = []
            genres = soup.find("p", class_="description-update").findAll("a")
            for genre in genres:
                genre_list.append(genre.text)
            latest_chap = soup.find("div", class_="total-chapter").find("a")
            latest_chapter = latest_chap.text
            latest_chapter_split = latest_chapter.split(" ")
            last_chapter = latest_chapter_split[-1]
            return [manga_title.text, image_link, genre_list[:-2], last_chapter]
        except AttributeError:
            return "Invalid Mangaid"
        except aiohttp.ClientConnectorError:
            return "Check the host's network Connection"

    # returns list of image links of pages of full chapter [imglink1, imglink2, full chapter]
    async def get_manga_chapter(mangaid, chapternum):
        try:
            url = f"http://kissmanga.nl/{mangaid}-chapter-{chapternum}"
            async with aiohttp.ClientSession() as _client:
                response = await _client.get(url)
            response_html = await response.text()
            soup = BeautifulSoup(response_html, "lxml")
            chapter_pages = soup.find("p", id="arraydata")
            pages = chapter_pages.text.split(",")
            return pages
        except AttributeError:
            return "Invalid Mangaid or chapter number"
        except aiohttp.ClientConnectorError:
            return "Check the host's network Connection"
