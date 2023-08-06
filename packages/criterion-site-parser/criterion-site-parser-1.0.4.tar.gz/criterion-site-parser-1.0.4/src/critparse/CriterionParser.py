import requests
from bs4 import BeautifulSoup
import argparse
from critparse import CriterionParser, CriterionMovieParse, OutText

# https:\\www.criterionchannel.com

class CriterionParser:
    """Main Class for the collection of movie data from the Criterion Channel
    (www.criterionchannel.com)

    Two different 'views' are currently implemented to display the collected
    data. One is a test representation of the data, the other is a Json
    representation of the data. The former is what I've been using for a couple
    of years to manage my movie viewing. The latter is interfacing with a rest
    interface of a database of my movies.

    Usage:
        parser = CriterionParser(url)      // instantiate the class
        parser.gather_all_info()           // gather the data
        TextOut.movie_info_to_text(parser) // present the data
    """
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, 'html5lib')
        self.url_type = CriterionParser.determine_url_type(self.soup)
        self.series_name = ''
        self.all_movie_parsed_data = []
        self.time = None
        self.extracted_episode_info = None
        self.description = None

    def gather_all_info(self):
        """
        Main driver method and entry point into data gathering.

        :return: None
        """
        if self.url_type == 'movie':
            self.__gather_movie_list_info([['', self.url]])
        elif self.url_type == 'collection':
            self.series_name, self.extracted_episode_info = CriterionParser.get_collection_info(self.soup)
            self.__gather_movie_list_info(self.extracted_episode_info)
        elif self.url_type == 'edition':
            self.series_name, self.extracted_episode_info = CriterionParser.get_edition_info(self.soup)
            self.__gather_movie_list_info(self.extracted_episode_info)
        else:
            self.series_name, self.description, self.extracted_episode_info = CriterionParser.get_series_info(self.soup)
            self.__gather_movie_list_info(self.extracted_episode_info)

    def __gather_movie_list_info(self, movies_list):
        """
        This gathers one or more movies' data from the list of movies provided as an argument.

        :param movies_list: List of individual movie information. List required
            to be a minimum of len(2)

        :return: None
        """
        for movie in movies_list:
            time, url = movie[0], movie[1]
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html5lib')
            url_type = CriterionParser.determine_url_type(soup)
            if url_type == 'collection':
                time, url = CriterionParser.extract_title_feature_from_collection(soup)[0]
                if time == '0:00':
                    continue
            movie_parser = CriterionMovieParse.MovieParse(url, time)
            self.all_movie_parsed_data.append(movie_parser.get_parsed_info())

    def collect_information_for_api(self):
        if self.url_type == 'movie':
            print('Examined ' + self.url)
            CriterionParser.call_api([['', self.url, "NoTitle"]], self.series_name)
        elif self.url_type == 'collection':
            self.series_name, self.extracted_episode_info = CriterionParser.get_collection_info(self.soup)
            print('Examined ' + self.url)
            CriterionParser.call_api(self.extracted_episode_info, self.series_name)
        elif self.url_type == 'edition':
            self.series_name, self.extracted_episode_info = CriterionParser.get_edition_info(self.soup)
            print('Examined ' + self.url)
            CriterionParser.call_api(self.extracted_episode_info, self.series_name)
        else:
            self.series_name, self.description, self.extracted_episode_info = CriterionParser.get_series_info(self.soup)
            print('Examined ' + self.url)
            print('+' * 54)
            print(self.series_name)
            print(self.description)
            print('+' * 54)
            print()
            print()
            # self.print_movies_list(self.extracted_episode_info)
            CriterionParser.call_api(self.extracted_episode_info, self.series_name)

    @staticmethod
    def get_collection_info(soup):
        """
        Parses and extracts the collection information. By collection I mean a loose coupling for
        a movie or a list of movies. More and more single movies tend to have a 'front door' page
        where you can read the full description without the movie starting.

        :param soup: instance to search/parse

        :return: tuple containing series_name and episode_info (a list of lists)
        """
        series_name, series = CriterionParser.get_edition_info(soup)
        # Is this what I want??
        series_name = "Collection:" + series_name
        return series_name, series

    @staticmethod
    def get_edition_info(soup):
        """
        Parses and extracts the edition information. By edition I mean what you might in the
        "Criterion Editions" section of the site. I've found that Criterion has a couple of
        different ways to represent editions. If the code has identified the url as being an
        edition, it will have a subtitle like "Criterion Collection Edition #982". Other editions
        lack this 'tell' and will be processed like a collection.

        :param soup: instance to search/parse

        :return: tuple containing series_name and episode_info (a list of lists)
        """
        series_name, not_used = CriterionParser.extract_collection_name_and_description(soup)
        series = CriterionParser.extract_title_feature_from_collection(soup)
        series += CriterionParser.extract_episode_time_and_url(soup)
        return series_name, series

    @staticmethod
    def get_series_info(soup):
        """
        Parses and extracts the series information. By series I mean what you might find listed
        in the main marquee of the web page. Also those listed in the "Featured Collections" section.
        Terminology is a bit messed up.

        :param soup: instance to search/parse

        :return: tuple containing series_name, series_description and episode_info (a list of lists)
        """
        series_name, description = CriterionParser.extract_collection_name_and_description(soup)
        series_name = "Criterion:" + series_name
        series = CriterionParser.extract_episode_time_and_url(soup)
        next_url = CriterionParser.extract_next_url(soup)
        while next_url:
            r = requests.get(next_url)
            soup = BeautifulSoup(r.content, 'html5lib')
            next_url = CriterionParser.extract_next_url(soup)
            series += CriterionParser.extract_episode_time_and_url(soup)
        return series_name, description, series

    @staticmethod
    def call_api(movies_list, series_name):
        episode = 0
        for movie in movies_list:
            episode += 1
            time, url, title = movie
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html5lib')
            url_type = CriterionParser.determine_url_type(soup)
            if url_type == 'collection':
                time, url = CriterionParser.extract_title_feature_from_collection(soup)[0]
            movie_parser = CriterionMovieParse.MovieParse(url)
            movie_parser.addViaApi(time, series_name)

    @staticmethod
    def extract_next_url(soup):
        """
        criterionchannel.com uses paging in their web presentation. This method
        is the programatic way to click the "load more" link on the page.

        :param soup: instance to search/parse

        :return: url for the next page of movies in the series
        """
        ret_str = None
        table = soup.find('div', attrs={'class': 'row loadmore'})
        if table:
            for item in table.findAll('a', attrs={'class': 'js-load-more-link'}):
                ret_str = "https://www.criterionchannel.com" + item['href']
        return ret_str

    @staticmethod
    def determine_url_type(soup):
        """
        Determines the type of url of the soup instance.

        :param soup: instance to search/parse

        :return:
            "" represents a series or movie list.
            "movie" represents a movie link.
            "collection" represents a cover page to one movie.
            "edition" is a Criterion Edition set of movies.
        """
        match_star = 'Starring '
        match_edition = 'Criterion Collection Edition '
        url_type = None
        one, two = CriterionParser.url_type_helper(soup)
        if one == 'NoName' and two == 'NoDescription':
            url_type = 'movie'
        elif url_type is None and two[:len(match_star)] == match_star:
            url_type = 'collection'
        elif url_type is None and one[:len(match_edition)] == match_edition:
            url_type = 'edition'
        return url_type

    @staticmethod
    def extract_collection_name_and_description(soup):
        """
        Obtains the name and description of a movie collection.

        :param soup: instance to parse/search

        :return: tuple of name and description found
        """
        match = 'Criterion Collection Edition '
        ret_str = ['NoName', 'NoAddition', 'NoDescription']
        table = soup.find('div', attrs={'class': 'collection-details grid-padding-left'})
        if table:
            ret_str = []
            for string in table.stripped_strings:
                ret_str.append(string)
            if ret_str[1][:len(match)] == match:
                ret_str[0] = ret_str[1]
        return ret_str[0], ret_str[2]

    @staticmethod
    def url_type_helper(soup):
        """
        A wrapper for extract_series_name_and_description. Helps make the code more self documenting?/maintainable?

        :param soup: instance to parse/search

        :return: tuple of name and description found
        """
        return CriterionParser.extract_collection_name_and_description(soup)

    @staticmethod
    def extract_title_feature_from_collection(soup):
        """
        Parses the web information and extracts a list of datam for each movie in the movie collection.

        :param soup: html5 parser instance (BeautifulSoup instance)

        :return: List of lists containing three items representing [time, featureUrl, title]
            for the title feature (movie) in a collection or edition collection
        """
        ret = []
        table = soup.find('li', attrs={'class': 'js-collection-item'})
        if table:
            for item in table.findAll('div', attrs={'class': 'grid-item-padding'}):
                movie = [item.a.text.strip(), item.a['href'], "NoTitle"]
                ret.append(movie)
        if len(ret) == 0:
            empty = ['0:00', 'NoLinkToFeature', 'NoTitle']
            ret.append(empty)
        return ret

    @staticmethod
    def extract_episode_time_and_url(soup):
        """
        Parses the web information and extracts a list of datam for each movie in the movie collection.
        Interestingly, the series or collection listing will contain a HH:MM:SS duration whereas the
        movie will not.

        :param soup: html5 parser instance (BeautifulSoup instance)

        :return: List of lists containing three items representing [time, featureUrl, title]
            for the title feature (movie) in a collection or edition collection
        """
        ret = []
        table = soup.find('ul', attrs={'class': 'js-load-more-items-container'})
        if table:
            for item in table.findAll('div', attrs={'class': 'grid-item-padding'}):
                movie = [item.a.text.strip(), item.a['href'], item.img['alt']]
                ret.append(movie)
        return ret


def main():
    args = process_args()
    if args.url:
        parser = CriterionParser(args.url)
        if args.api:
            parser.collect_information_for_api()
        else:
            parser.gather_all_info()
            OutText.movie_info_to_text()


def process_args():
    usage_desc = "This is how you use this thing"
    parser = argparse.ArgumentParser(description=usage_desc)
    parser.add_argument("url", help="URL to parse")
    parser.add_argument("-a", "--api", help="Add movie via REST api", action='store_true')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
