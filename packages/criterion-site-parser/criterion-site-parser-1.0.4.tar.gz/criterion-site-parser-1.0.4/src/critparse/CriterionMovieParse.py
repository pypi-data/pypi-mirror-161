import json

import requests
from bs4 import BeautifulSoup
import argparse


def extract_title_length(table):
    for item in table.findAll('div', attrs={'class': 'contain margin-top-large column small-16'}):
        return item.h1.text.strip(), item.h5.text.strip()


def extract_info(table):
    info = []
    for item in table.findAll('div', attrs={'class': 'site-font-secondary-color'}):
        for string in item.stripped_strings:
            info.append(string)
    return info


def extract_series_title_feature(soup):
    ret = []
    table = soup.find('li', attrs={'class': 'js-collection-item'})
    for item in table.findAll('div', attrs={'class': 'grid-item-padding'}):
        movie = [item.a.text.strip(), item.a['href']]
        ret.append(movie)
    return ret


class MovieParse:
    def __init__(self, url, timeSupplied=None):
        self.url = url
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        self.table = soup.find('div', attrs={'class': 'column small-16 medium-8 large-10'})
        cmsp_length = None
        if not self.table:
            # desperate attempt to salvage the effort
            cmsp = extract_series_title_feature(soup)
            cmsp_length = cmsp[0][0]
            r = requests.get(cmsp[0][1])
            soup = BeautifulSoup(r.content, 'html5lib')
            self.table = soup.find('div', attrs={'class': 'column small-16 medium-8 large-10'})
        diryrcnty, stars, descr, director, year, country = '', '', '', '', '', ''
        title, length = extract_title_length(self.table)
        info = extract_info(self.table)
        if len(info) == 4:
            # hack around episode names for some 'features' and sometimes alternate titles
            if info[0].find('“') >= 0 or info[0].find('(') >= 0:
                diryrcnty = info[1]
                stars = info[2]
                descr = info[3]
                ex_descr = info[0]
            else:
                diryrcnty, stars, descr, ex_descr = info
            director, year, country = diryrcnty.split('•')
            director = director.replace("Directed by ", "")
            stars = stars.replace("Starring ", "")
            stars = stars.replace(',', ';')
            descr = descr + '\n\n' + ex_descr
        if len(info) == 3:
            # sometimes you are hear but have no stars listed in the movie.
            # i.e., you have diryrcnty descr1 and descr2. Look for this case
            diryrcnty, stars, descr = info
            if "Starring" not in stars:
                descr = stars + "\n\n" + descr
                stars = ""
            splits = diryrcnty.split('•')
            if len(splits) == 3:
                director, year, country = splits
            if len(splits) == 2:
                year, country = splits
            if director:
                director = director.replace("Directed by ", "")
            stars = stars.replace("Starring ", "")
            stars = stars.replace(',', ';')
            if country:
                country = country.replace(',', ';')

        if len(info) == 2:
            diryrcnty, descr = info
            if '•' in diryrcnty:
                splits = diryrcnty.split('•')
                if len(splits) == 3:
                    director, year, country = splits
                if len(splits) == 2:
                    year, country = splits
                if director:
                    director = director.replace("Directed by ", "")
            else:
                descr = diryrcnty + '\n\n' + descr
        if len(info) == 1:
            descr = info[0]

        if title[0:4] == "The ":
            title = title[4:] + ", " + title[0:3]

        if title[0:2] == "A ":
            title = title[2:] + ", " + title[0:1]
        self.just_title = title
        if year:
            title = title + " (" + year.strip() + ")"
        else:
            title = title + " (NONE)"

        if '•' in length:
            length = length.split('•')[1].strip()

        if director:
            director = director.replace(" and ", ",")
            director = director.replace(",", ";")
            director = director.replace(";;", ";")

        if country:
            country = country.replace(',', ';')

        self.length = length
        if cmsp_length:
            self.length = cmsp_length
        if timeSupplied:
            self.length = timeSupplied
        self.title = title
        self.director = director
        self.country = country.strip()
        self.stars = stars
        self.descr = descr
        self.year = year.strip()

    def get_parsed_info(self):
        return [self.just_title, self.year, self.title, self.director, self.country, self.stars,
                self.descr, self.length, self.url]

    def print_info(self, supplied_length=None):

        print(self.url)
        if not supplied_length:
            print(self.length)
        print(self.title)
        print('##' + self.title + ' Watched')
        if self.director:
            print(self.director)
        else:
            print("NONE")

        if self.country:
            print(self.country)
        else:
            print("NONE")

        if self.stars:
            print(self.stars)
        else:
            print("NONE")
        print()
        if self.descr:
            print(self.descr)
        else:
            print("NONE")

    def addViaApi(self, supplied_length=None, collection=None):
        put_uri = "http://localhost:8080/rest/movie"
        movie_dto = {"title": self.just_title,
                     "year": self.year,
                     "actors": self.stars,
                     "directors": self.director,
                     "countries": self.country,
                     "collections": collection,
                     "description": self.descr}
        movie_length = self.length
        if supplied_length:
            movie_length = supplied_length
        movie_dto["duration"] = movie_length

        # print the json instead of calling api
        print(json.dumps(movie_dto))
        # response = requests.put(put_uri, json=movie_dto)
        # if response.status_code != 200:
        #     print("Error")


def main():
    usage_desc = "This is how you use this thing"
    parser = argparse.ArgumentParser(description=usage_desc)
    parser.add_argument("url", help="URL to parse")
    args = parser.parse_args()
    if args.url:
        url = args.url
    movie_parser = MovieParse(url)
    print('='*54)
    movie_parser.print_info()
    print('='*54)
    print()
    print()


if __name__ == "__main__":
    main()
