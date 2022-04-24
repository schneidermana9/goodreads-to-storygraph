from typing import List

from bs4 import BeautifulSoup, element


def main():
    soup = make_soup()
    books: element.Tag = soup('tr')
    for book in books:
        print(get_date_read(book))

def get_book_id(book: element.Tag) -> str:
    div = book.find_next(lambda tag: tag.has_attr('data-resource-id'))
    return div['data-resource-id']

def get_title(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field title')
    title = subtag.find('a').text.strip()
    return title.split("\n")[0]

def make_soup() -> BeautifulSoup:
    with open("testerBook.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup

def before_2015(book: element.Tag):
    # ~line 400
    # td class = field date_read
    # if span class = "greyText", fail
    # then call get_date_read
    # if return before 2015, fail
    date = get_date_added(book)
    print(int(date[-2:]))
    if int(date[-2:]) < 15:
        return False
    else:
        return True

def get_date_added(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field date_added')
    return subtag.find('span').text.strip()

def before_2015_2(book:element.Tag):
    # semi-verified
    # edge case to fix: book read multiple times, one of which is pre-2015
    subtag: element.Tag = book.find('td', class_='field date_read')
    if (len(subtag.find_all('span', class_='greyText')) > 0):
        return False
    else:
        date = get_date_read(book)
        if int(date[-2:]) > 15:
            return False
        else:
            return True

def get_date_read(book):
    # td class = "field date_read"
    # span class = "date_read_value".text
    # uhhh return string I guess?
    info: element.Tag = book.find('span', class_='date_read_value')
    try:
        writtenDate: str = info.text
        elems: List[str] = writtenDate.split(" ")
        month: str = processMonth(elems[0])
        day: str = elems[1].replace(",", "")
        return f"{month}/{day}/{elems[2]}"
    except AttributeError:
        return ""

def processMonth(month: str):
    if month == "Jan":
        return "1"
    elif month == "Feb":
        return "2"
    elif month == "Mar":
        return "3"
    elif month == "Apr":
        return "4"
    elif month == "May":
        return "5"
    elif month == "Jun":
        return "6"
    elif month == "Jul":
        return "7"
    elif month == "Aug":
        return "8"
    elif month == "Sep":
        return "9"
    elif month == "Oct":
        return "10"
    elif month == "Nov":
        return "11"
    elif month == "Dec":
        return "12"





if __name__=="__main__":
    main()