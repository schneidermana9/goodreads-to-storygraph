from typing import List
from bs4 import BeautifulSoup, element
import pandas as pd
import calendar

month_abv_to_num = {month: index for index, month in enumerate(calendar.month_abbr) if month}

def make_soup() -> BeautifulSoup:
    """Open BeautifulSoup with html of goodreads library for use in data cleaning"""
    with open("index.html", 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup


def clean_html(soup: BeautifulSoup) -> pd.DataFrame:
    """Create dataframe containing all cleaned information about books"""
    books: element.Tag = soup('tr')
    col_titles: List[str] = ["Book Id", "Title", "Author", "Author l-f", "Additional Authors",
                             "ISBN", "ISBN13", "My Rating", "Average Rating", "Publisher", "Binding", "Number of Pages",
                             "Year Published", "Original Publication Year", "Date Read", "Date Added", "Bookshelves",
                             "Bookshelves with positions", "Exclusive Shelf", "My Review", "Spoiler", "Private Notes",
                             "Read Count", "Recommended For", "Recommended By", "Owned Copies", "Original Purchase Date",
                             "Original Purchase Location", "Condition", "Condition Description", "BCID"]
    formatted_books: List[List[str]] = []

    for book in books:
        if after_2015(book):
            row: List[str] = create_row(book)
            formatted_books.append(row)
    df: pd.DataFrame = pd.DataFrame(data=formatted_books, columns=col_titles)
    return df


def export_df(df: pd.DataFrame) -> None:
    """Export pandas dataframe to csv for use in storygraph import"""
    df.to_csv('my_csv_3.csv', index=False)

def create_row(book: element.Tag) -> List[str]:
    """Creates list format of all information for one row of csv, containing information for one book
    Empty strings left for information under headers which are necessary for storygraph import format,
    but do not have information in goodreads library
    """
    book_id: str = get_book_id(book)
    title: str = get_title(book)
    author: str = get_author(book)
    author_lf: str = get_author_lf(book)
    additional_authors: str = ""
    isbn: str = get_isbn(book)
    isbn_13: str = get_isbn_13(book)
    avg_rating: str = get_avg_rating(book)
    num_pages: str = get_num_pages(book)
    yr_published: str = get_yr_published(book)
    orig_publication_date: str = get_orig_published(book)
    date_read: str = get_date_read(book)
    date_added: str = get_date_added(book)
    exclusive_position = 'read'
    read_count: str = get_read_count(book)
    row: List[str] = [book_id, title, author, author_lf, additional_authors, isbn, isbn_13,
                      "", avg_rating, "", "", num_pages, yr_published, orig_publication_date,
                      date_read, date_added, "", "", exclusive_position, "","","",read_count,
                      "", "", "", "", "", "", "", ""]
    return row

def after_2015(book: element.Tag) -> bool:
    """Returns boolean value of whether book was added to library after 2015.
     Done to reflect a more updated library when transferring to Storygraph"""
    # possible edge case to fix: book read multiple times, one of which is pre-2015
    date = book.find('td', class_='date_added').find('span').text.strip()
    print(int(date[-2:]))
    if int(date[-2:]) < 15:
        return False
    else:
        return True


def get_book_id(book: element.Tag) -> str:
    """Finds string value of goodread's id number for book"""
    div = book.find_next(lambda tag: tag.has_attr('data-resource-id'))
    return div['data-resource-id']

def get_title(book: element.Tag) -> str:
    """Finds title of book"""
    subtag: element.Tag = book.find('td', class_='field title')
    title = subtag.find('a').text.strip()
    return title.split("\n")[0]


def get_author(book: element.Tag) -> str:
    """Finds author of book's name in 'first_name last_name' format"""
    # potential edge case for future fix: multiple authors
    author_lf = get_author_lf(book)
    names = reversed(author_lf.split(", "))
    return " ".join(names)


def get_author_lf(book: element.Tag) -> str:
    """Finds author of book's name in 'last_name, first_name' format """
    subtag: element.Tag = book.find('td', class_='field author')
    return subtag.find('a').text



def get_additional_authors(book: element.Tag) -> str:
    # left as header for possible future improvement
    pass


def get_isbn(book: element.Tag) -> str:
    """Finds string value of book's isbn number"""
    subtag: element.Tag = book.find('td', class_='field isbn')
    return subtag.find('div', class_="value").text.strip()


def get_isbn_13(book: element.Tag) -> str:
    """Finds string value of book's isbn-13 number"""
    subtag: element.Tag = book.find('td', class_='field isbn13')
    return subtag.find('div', class_="value").text.strip()


def get_avg_rating(book: element.Tag) -> str:
    """Finds string value of average user ratings of book"""
    subtag: element.Tag = book.find('td', class_='field avg_rating')
    return subtag.find('div', class_="value").text.strip()


def get_num_pages(book: element.Tag) -> str:
    """Finds string value of number of pages in edition of the book marked as read. Returns an empty string if not found"""
    subtag: element.Tag = book.find('td', class_='field num_pages')
    try:
        pages = subtag.find('nobr').text.strip()
        return pages.split("\n")[0]
    except AttributeError:
        return ""


def get_yr_published(book: element.Tag) -> str:
    """Finds string value of year the edition of the book marked as read was published"""
    subtag: element.Tag = book.find('td', class_='field date_pub_edition')
    return subtag.find('div', class_="value").text.strip()[-4:]


def get_orig_published(book: element.Tag) -> str:
    """Finds string value of year book was originally published"""
    subtag: element.Tag = book.find('td', class_='field date_pub')
    return subtag.find('div', class_="value").text.strip()[-4:]


def get_date_read(book: element.Tag) -> str:
    """Finds string value of date book was marked as read in format MM/D/YYYY. Returns emtpy string if not present"""
    info: element.Tag = book.find('span', class_='date_read_value')
    try:
        writtenDate: str = info.text
        elems: List[str] = writtenDate.split(" ")
        if (len(elems) != 3):
            raise AttributeError("wrong date format")
        month: str = str(month_abv_to_num[elems[0]])
        day: str = elems[1].replace(",", "")
        return f"{month}/{day}/{elems[2]}"
    except AttributeError:
        return ""

def get_date_added(book: element.Tag) -> str:
    """Finds string value of date book was added to library in format MM/D/YYYY. Returns emtpy string if not present """
    info: element.Tag =book.find('td', class_='date_added').find('span')
    try:
        writtenDate: str = info.text.strip()
        elems: List[str] = writtenDate.split(" ")
        month: str = str(month_abv_to_num[elems[0]])
        day: str = elems[1].replace(",", "")
        return f"{month}/{day}/{elems[2]}"
    except AttributeError:
        return ""


def get_read_count(book: element.Tag) -> str:
    """Finds string value of number of times book as been read. Returns empty string if not present """
    subtag: element.Tag = book.find('td', class_='field read_count')
    return subtag.find('div', class_="value").text.strip()


# Run pipeline
if __name__ == '__main__':
    my_soup = make_soup()
    df_cleaned = clean_html(my_soup)
    export_df(df_cleaned)


