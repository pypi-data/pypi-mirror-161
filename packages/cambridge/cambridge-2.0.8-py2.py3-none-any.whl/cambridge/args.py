import sqlite3
import logging
import argparse
import sys
import requests
from bs4 import BeautifulSoup

from .cache import (
    create_table,
    insert_into_table,
    get_cache,
    get_response_words,
    get_random_words,
    delete_word,
    check_table,
)
from .log import logger
from .dicts.cambridge import (
    parse_spellcheck,
    parse_dict_blocks,
    parse_dict_body,
    parse_dict_head,
    parse_dict_name,
    parse_response_word,
    DICT_BASE_URL,
    CAMBRIDGE_URL,
    SPELLCHECK_BASE_URL,
)
from .utils import get_request_url, get_requsest_url_spellcheck, parse_from_url
from .fetch import fetch


def parse_args():
    parser = argparse.ArgumentParser(
        description="Terminal Version of Cambridge Dictionary"
    )

    # Add sub-command capability that can identify different sub-command name
    sub_parsers = parser.add_subparsers(dest="subparser_name")

    # Add sub-command l
    parser_lw = sub_parsers.add_parser(
        "l",
        help="list all the words you've successfully searched in alphabetical order",
    )

    # Make sub-command l run default funtion of "list_words"
    parser_lw.set_defaults(func=list_words)

    # Add optional argument for deleting a word from word list
    parser_lw.add_argument(
        "-d",
        "--delete",
        nargs="+",
        help="delete a word or phrase from cache",
    )

    # Add optional argument for listing all words by time
    parser_lw.add_argument(
        "-t",
        "--time",
        action="store_true",
        help="list all the words you've successfully searched in reverse chronological order",
    )

    # Add optional argument for listing words randomly chosen
    parser_lw.add_argument(
        "-r",
        "--random",
        action="store_true",
        help="randomly list the words you've successfully searched",
    )

    # Add sub-command s
    parser_sw = sub_parsers.add_parser("s", help="search a word or phrase")

    # Make sub-command s run default function of "search_words"
    parser_sw.set_defaults(func=search_word)

    # Add positional arguments with n args
    parser_sw.add_argument(
        "words",
        nargs="+",
        help="A word or phrase you want to search",
    )
    # Add optional arguments
    parser_sw.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="search a word or phrase in verbose mode",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    elif sys.argv[1] != "l" and len(sys.argv) > 1:
        to_parse = []
        word = []
        for i in sys.argv[1:]:
            if i.startswith("-"):
                to_parse.append(i)
            else:
                word.append(i)
        to_search = " ".join(word)
        to_parse.append(to_search)
        args = parser_sw.parse_args(to_parse)

    else:
        args = parser.parse_args()

    return args


def list_words(args, con, cur):
    # The subparser i.e. the sub-command isn't in the namespace of args
    if args.delete:
        word = " ".join(args.delete)
        if delete_word(con, cur, word):
            print(f'"{word}" got deleted from cache successfully')
        else:
            logger.error(f'No such word "{word}" in cache')
    elif args.random:
        try:
            # data is something like [('hello',), ('good',), ('world',)]
            data = get_random_words(cur)
        except sqlite3.OperationalError:
            logger.error("You may haven't searched any word yet")
        else:
            for i in data:
                print(i[0])
    else:
        try:
            # data is something like [('hello',), ('good',), ('world',)]
            data = get_response_words(cur)
        except sqlite3.OperationalError:
            logger.error("You may haven't searched any word yet")
        else:
            if args.time:
                data.sort(reverse=True, key=lambda tup: tup[1])
            else:
                data.sort()
            for i in data:
                print(i[0])


def search_word(args, con, cur):
    # FIXME docstring not finished
    """
    The function triggered when a user searches a word or phrase on terminal.
    It checks the args, if "-v" or "--verbose" is in it, the debug mode will be turned on.
    """

    input_word = args.words[0]
    request_url = get_request_url(DICT_BASE_URL, input_word)

    if args.verbose:
        logging.getLogger(__package__).setLevel(logging.DEBUG)

    data = get_cache(cur, input_word, request_url)  # data is a tuple if any

    if data is None:
        logger.debug(f'Searching {CAMBRIDGE_URL} for "{input_word}"')

        result = request_and_print(request_url, input_word)
        found = result[0]

        if found:
            response_word, response_url, response_text, soup = result[1]
            try:
                logger.debug(f'Caching search result of "{input_word}"')
                insert_into_table(con, cur, input_word, response_word, response_url, response_text)
                # check_table(cur)
            except sqlite3.OperationalError: 
                create_table(con, cur)
            except sqlite3.IntegrityError:
                logger.debug(f'Cancel caching word of "{input_word}" because it already exists')
            else:
                logger.debug(f'Done caching search result of "{input_word}"')

        else:
            sys.exit()

    else:
        logger.debug(f'Already cached "{input_word}" before. Use cache')
        soup = BeautifulSoup(data[0], "lxml")
        print_dict(request_url, soup)


# ----------print dict ----------
def request_and_print(url, input_word):
    with requests.Session() as session:
        session.trust_env = False
        response = fetch(url, session)

        if response.url == DICT_BASE_URL:
            logger.debug(f'No "{input_word}" found in Cambridge')

            spellcheck_url = get_requsest_url_spellcheck(
                SPELLCHECK_BASE_URL, input_word
            )
            spellcheck_text = fetch(spellcheck_url, session).text

            soup = BeautifulSoup(spellcheck_text, "lxml")
            parse_spellcheck(input_word, soup)

            return False, None
        else:
            logger.debug(f'"{input_word}" found in Cambridge')

            response_url = parse_from_url(response.url)
            response_text = response.text

            soup = BeautifulSoup(response_text, "lxml")
            response_word = parse_response_word(soup)

            print_dict(url, soup)

            return True, (response_word, response_url, response_text, soup)


def print_dict(url, soup):
    blocks, first_dict = parse_dict_blocks(url, soup)
    for block in blocks:
        parse_dict_head(block)
        parse_dict_body(block)
    parse_dict_name(first_dict)
