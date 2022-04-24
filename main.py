from typing import List
from bs4 import BeautifulSoup, element
import pandas as pd
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def make_soup() -> BeautifulSoup:
    with open("index.html", 'r', encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup


def clean_html(soup: BeautifulSoup) -> pd.DataFrame:
    """
    Book Id - POPULATE (data resource id)
    Title - POPULATE
    Author	- POPULATE
    Author l-f - POPULATE
    Additional Authors - POPULATE
    ISBN - POPULATE
    ISBN13 - POPULATE
    My Rating
    Average Rating - POPULATE
    Publisher - POPULATE
    Binding 
    Number of Pages - POPULATE
    Year Published - POPULATE
    Original Publication Year - POPULATE
    Date Read - POPULATE (SELECT ONLY IF >=2015)
    Date Added - POPULATE
    Bookshelves 
    Bookshelves with positions
    Exclusive Shelf - DEFAULT 'read'
    My Review
    Spoiler	Private Notes
    Read Count - POPULATE
    Recommended For
    Recommended By
    Owned Copies
    Original Purchase Date
    Original Purchase Location
    Condition
    Condition Description
    BCID

checkbox
position
cover
title
author
isbn
isbn13
asin
num_pages
avg_rating
num_ratings
date_pub
date_pub_edition
rating
shelves
review
notes
recommender
comments
votes
read_count
date_started
date_read
date_added
date_purchased
owned
purchase_location
condition
format
actions

    """
    books: element.Tag = soup('tr')
    col_titles: List[str] = ["Book Id", "Title", "Author", "Author l-f", "Additional Authors",
                             "ISBN", "ISBN13", "My Rating", "Average Rating", "Publisher", "Binding", "Number of Pages",
                             "Year Published", "Original Publication Year", "Date Read", "Date Added", "Bookshelves",
                             "Bookshelves with positions", "Exclusive Shelf", "My Review", "Spoiler", "Private Notes",
                             "Read Count", "Recommended For", "Recommended By", "Owned Copies", "Original Purchase Date",
                             "Original Purchase Location", "Condition", "Condition Description", "BCID"]
    formatted_books: List[List[str]] = []

    for book in books:
        # doing all for some reason?
        if before_2015(book):
            row: List[str] = create_row(book)
            formatted_books.append(row)
    df: pd.DataFrame = pd.DataFrame(data=formatted_books, columns=col_titles)
    return df


def export_df(df: pd.DataFrame):
    df.to_csv('my_csv_3.csv', index=False)

def create_row(book: element.Tag) -> List[str]:
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

def before_2015(book: element.Tag):
    # semi-verified
    # edge case to fix: book read multiple times, one of which is pre-2015
    date = book.find('td', class_='date_added').find('span').text.strip()
    print(int(date[-2:]))
    if int(date[-2:]) < 15:
        return False
    else:
        return True


def get_book_id(book: element.Tag) -> str:
    # verified
    div = book.find_next(lambda tag: tag.has_attr('data-resource-id'))
    return div['data-resource-id']

def get_title(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field title')
    title = subtag.find('a').text.strip()
    return title.split("\n")[0]


def get_author(book):
    # semi validated
    # potential edge case: multiple authors
    author_lf = get_author_lf(book)
    names = reversed(author_lf.split(", "))
    return " ".join(names)
#    do list-reverse fucky wucky and then return joined with ", "


def get_author_lf(book):
    # semi-validated
    # potential edge case: multiple authors
    subtag: element.Tag = book.find('td', class_='field author')
    return subtag.find('a').text



def get_additional_authors(book):
    pass


def get_isbn(book):
    # semi-validated
    # sometimes empty, but returns empty string so should be ok
    subtag: element.Tag = book.find('td', class_='field isbn')
    return subtag.find('div', class_="value").text.strip()


def get_isbn_13(book):
    # validated
    subtag: element.Tag = book.find('td', class_='field isbn13')
    return subtag.find('div', class_="value").text.strip()


def get_avg_rating(book):
    # validated
    subtag: element.Tag = book.find('td', class_='field avg_rating')
    return subtag.find('div', class_="value").text.strip()


def get_num_pages(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field num_pages')
    try:
        pages = subtag.find('nobr').text.strip()
        return pages.split("\n")[0]
    except AttributeError:
        return ""


def get_yr_published(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field date_pub_edition')
    return subtag.find('div', class_="value").text.strip()[-4:]


def get_orig_published(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field date_pub')
    return subtag.find('div', class_="value").text.strip()[-4:]


def get_date_read(book):
    # td class = "field date_read"
    # span class = "date_read_value".text
    # uhhh return string I guess?
    info: element.Tag = book.find('span', class_='date_read_value')
    try:
        writtenDate: str = info.text
        elems: List[str] = writtenDate.split(" ")
        if (len(elems) != 3):
            raise AttributeError("wrong date format")
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

def get_date_added(book):
    # verified
    # edit to be format mm/dd/yyyy
    info: element.Tag =book.find('td', class_='date_added').find('span')
    try:
        writtenDate: str = info.text.strip()
        elems: List[str] = writtenDate.split(" ")
        month: str = processMonth(elems[0])
        day: str = elems[1].replace(",", "")
        return f"{month}/{day}/{elems[2]}"
    except AttributeError:
        return ""


def get_read_count(book):
    # verified
    subtag: element.Tag = book.find('td', class_='field read_count')
    return subtag.find('div', class_="value").text.strip()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    my_soup = make_soup()
    df_cleaned = clean_html(my_soup)
    export_df(df_cleaned)


"""
<tr id="review_391002311" class="bookalike review">
      <td class="field checkbox" style="display: none">
        <label>checkbox</label>
        <div class="value">
            <input type="checkbox" name="reviews[391002311]" id="checkbox_review_391002311" value="391002311">
        </div>
      </td> 
      
      <td class="field position" style="display: none">
        <label>position</label>
        <div class="value"></div>
      </td>
      
      <td class="field cover">
        <label>cover</label>
        <div class="value">
            <div class="js-tooltipTrigger tooltipTrigger" data-resource-type="Book" data-resource-id="9673436">
                <a href="/book/show/9673436-the-invention-of-hugo-cabret"><img alt="The Invention of Hugo Cabret" id="cover_review_391002311" src="https://i.gr-assets.com/images/S/compressed.photo.goodreads.com/books/1422312376l/9673436._SY75_.jpg"></a>
            </div>
        </div>
      </td>
      
      <td class="field title">
        <label>title</label>
        <div class="value">
            <a title="The Invention of Hugo Cabret" href="/book/show/9673436-the-invention-of-hugo-cabret">
                The Invention of Hugo Cabret
            </a>
        </div>
      </td>
      
      <td class="field author">
        <label>author</label>
        <div class="value">
              <a href="/author/show/38120.Brian_Selznick">Selznick, Brian</a>
        </div>
      </td>
      
      <td class="field isbn" style="display: none">
        <label>isbn</label>
        <div class="value"> </div>
      </td>
      
      <td class="field isbn13" style="display: none">
        <label>isbn13</label>
        <div class="value">
            9780439813765
        </div>
      </td>
    
      <td class="field asin" style="display: none">
        <label>asin</label>
        <div class="value"></div>
      </td>
    
      <td class="field num_pages" style="display: none">
        <label>num pages</label>
        <div class="value">
            <nobr>
              534
              <span class="greyText">pp</span>
            </nobr>
        </div>
      </td>
      
      <td class="field avg_rating">
        <label>avg rating</label>
        <div class="value">
            4.21
        </div>
      </td>
    
      <td class="field num_ratings" style="display: none">
        <label>num ratings</label>
        <div class="value">
            174,869
        </div>
      </td>
      
      <td class="field date_pub" style="display: none">
        <label>date pub</label>
        <div class="value">
              Mar 2007
        </div>
      </td>
     
     <td class="field date_pub_edition" style="display: none">
        <label>date pub edition</label>
        <div class="value">
              Mar 2007
        </div>
     </td>    
    
    <td class="field rating">
        <label>my rating</label>
        <div class="value">
            <div class="stars" data-resource-id="9673436" data-user-id="11838413" data-submit-url="/review/rate/9673436?stars_click=false" data-rating="5">
                <a class="star on" title="did not like it" href="#" ref="">
                    1 of 5 stars
                </a>
                <a class="star on" title="it was ok" href="#" ref="">
                    2 of 5 stars
                </a>
                <a class="star on" title="liked it" href="#" ref="">
                    3 of 5 stars
                </a>
                <a class="star on" title="really liked it" href="#" ref="">
                    4 of 5 stars
                </a>
                <a class="star on" title="it was amazing" href="#" ref="">
                    [ 5 of 5 stars ]
                </a>
            </div>
            <span id="reviewMessage9673436_11838413"></span>
            <span id="successMessage9673436_11838413"></span>
        </div>
    </td>
    
    <td class="field shelves">
        <label>shelves</label>
        <div class="value">
            <span id="shelfList11838413_9673436">
                <a class="shelfLink" title="View all books in Anna Schneiderman's read shelf." href="https://www.goodreads.com/review/list/11838413?shelf=read">
                    read
                </a>,
                <span id="shelf_685768488">
                    <a class="shelfLink" title="View all books in Anna Schneiderman's need-to-reread shelf." href="https://www.goodreads.com/review/list/11838413?shelf=need-to-reread">
                        need-to-reread
                    </a>
                </span>
            </span>
            <br>
                <a class="shelfChooserLink smallText" href="#" onclick="window.shelfChooser.summon(event, {bookId: 9673436, chosen: [&quot;need-to-reread&quot;]}); return false;">
                    [edit]
                </a>
        </div>
    </td>
    
    <td class="field review">
        <label>review</label>
        <div class="value">
            <a href="/review/edit/9673436?report_event=true">Write a review</a>
            <div class="clear"></div>
        </div>
    </td>
    
    <td class="field notes" style="display: none">
        <label>notes</label>
        <div class="value">
            <span class="greyText">None</span>
            <a class="floatingBoxLink smallText" href="#" onclick="reviewEditor.summon(this, 9673436, 'notes', {value: null}); return false;">
                [edit]
            </a>
        </div>
    </td>
    
    <td class="field recommender" style="display: none">
        <label>recommender</label>
        <div class="value">
            <span class="greyText">none</span>
        </div>
    </td>
    
    <td class="field comments" style="display: none">
        <label>comments</label>
        <div class="value">
            <a href="/review/show/391002311">0</a>
        </div>
    </td>
    
    <td class="field votes" style="display: none"><label>votes</label>
        <div class="value">
            <a href="/rating/voters/391002311?resource_type=Review">0</a>
        </div>
    </td>
    
    <td class="field read_count" style="display: none">
        <label># times read</label>
        <div class="value">
            1
        </div>
    </td>
    
    <td class="field date_started" style="display: none">
        <label>date started</label>
        <div class="value">
            <div class="date_row">
                <div class="editable_date date_started_bec45b307b67423db55f1900d776344d">
                    <span class="greyText">not set</span>
                    <a class="floatingBoxLink smallText" href="#" onclick="reviewEditor.summon(this, 9673436, 'started_at', {value: {}, reading_session_id: &quot;bec45b30-7b67-423d-b55f-1900d776344d&quot;}); return false;">
                        [edit]
                    </a>
                </div>
            </div>
        </div>
    </td>
    
    <td class="field date_read">
        <label>date read</label>
        <div class="value">
            <div class="date_row">
                <div class="editable_date date_read_bec45b307b67423db55f1900d776344d">
                    <span class="greyText">not set</span>
                    <a class="floatingBoxLink smallText" href="#" onclick="reviewEditor.summon(this, 9673436, 'read_at', {value: {}, reading_session_id: &quot;bec45b30-7b67-423d-b55f-1900d776344d&quot;}); return false;">
                        [edit]
                    </a>
                </div>
            </div>
        </div>
    </td>
    
    <td class="field date_added">
        <label>date added</label>
        <div class="value">
            <span title="August 13, 2012">
                Aug 13, 2012
            </span>
        </div>
    </td>
    
    <td class="field date_purchased" style="display: none">
        <label>date purchased</label>
        <div class="value">
            <a id="add_for_date_purchased" class="smallText" href="#" onclick="new Ajax.Request('/review/update/9673436?format=json', {asynchronous:true, evalScripts:true, onFailure:function(request){Element.hide('loading_anim_423923');$('add_for_date_purchased').innerHTML = '<span class=&quot;error&quot;>ERROR</span>try again';$('add_for_date_purchased').show();;Element.hide('loading_anim_423923');}, onLoading:function(request){;Element.show('loading_anim_423923');Element.hide('add_for_date_purchased')}, onSuccess:function(request){Element.hide('loading_anim_423923');Element.show('add_for_date_purchased');var json = eval('(' + request.responseText + ')');$('review_391002311').replace(json.html);if (typeof(toggleFieldsToMatchHeader) == 'function') {toggleFieldsToMatchHeader();}}, parameters:'owned_book[book_id]=9673436&amp;partial=bookalike&amp;view=table' + '&amp;authenticity_token=' + encodeURIComponent('KFhpn4kSoX1EbWK9vR1TOugRw7kf0wX/v3JWwc/L8J2QHn8tZ/YPGAKZIPtiNLQ+7xb2qkNJm+GQV+d3B6Wq7Q==')}); return false;">(add)</a>
            <img style="display:none" id="loading_anim_423923" class="loading" src="https://s.gr-assets.com/assets/loading-trans-ced157046184c3bc7c180ffbfc6825a4.gif" alt="Loading trans">
        </div>
    </td>
    
    <td class="field owned" style="display: none">
        <label>owned</label>
        <div class="value"></div>
    </td>
    
    <td class="field purchase_location" style="display: none">
        <label>purchase location</label>
        <div class="value">
            <a id="add_for_purchase_location" class="smallText" href="#" onclick="new Ajax.Request('/review/update/9673436?format=json', {asynchronous:true, evalScripts:true, onFailure:function(request){Element.hide('loading_anim_262952');$('add_for_purchase_location').innerHTML = '<span class=&quot;error&quot;>ERROR</span>try again';$('add_for_purchase_location').show();;Element.hide('loading_anim_262952');}, onLoading:function(request){;Element.show('loading_anim_262952');Element.hide('add_for_purchase_location')}, onSuccess:function(request){Element.hide('loading_anim_262952');Element.show('add_for_purchase_location');var json = eval('(' + request.responseText + ')');$('review_391002311').replace(json.html);if (typeof(toggleFieldsToMatchHeader) == 'function') {toggleFieldsToMatchHeader();}}, parameters:'owned_book[book_id]=9673436&amp;partial=bookalike&amp;view=table' + '&amp;authenticity_token=' + encodeURIComponent('0W9jfztOBI/73LHaBQ8dlI+ZdbTcqE2MlVsc8YiZz5dpKXXN1aqq6r0o85zaJvqQiJ5Ap4Ay05K6fq1HQPeV5w==')}); return false;">(add)</a>
            <img style="display:none" id="loading_anim_262952" class="loading" src="https://s.gr-assets.com/assets/loading-trans-ced157046184c3bc7c180ffbfc6825a4.gif" alt="Loading trans">
        </div>
    </td>
    
    <td class="field condition" style="display: none">
        <label>condition</label>
        <div class="value">
            <a id="add_for_condition" class="smallText" href="#" onclick="new Ajax.Request('/review/update/9673436?format=json', {asynchronous:true, evalScripts:true, onFailure:function(request){Element.hide('loading_anim_449839');$('add_for_condition').innerHTML = '<span class=&quot;error&quot;>ERROR</span>try again';$('add_for_condition').show();;Element.hide('loading_anim_449839');}, onLoading:function(request){;Element.show('loading_anim_449839');Element.hide('add_for_condition')}, onSuccess:function(request){Element.hide('loading_anim_449839');Element.show('add_for_condition');var json = eval('(' + request.responseText + ')');$('review_391002311').replace(json.html);if (typeof(toggleFieldsToMatchHeader) == 'function') {toggleFieldsToMatchHeader();}}, parameters:'owned_book[book_id]=9673436&amp;partial=bookalike&amp;view=table' + '&amp;authenticity_token=' + encodeURIComponent('57aDw8+hb9OuT0MwqUX41/OisUMt3fwbkkbAALnhERxf8JVxIUXBtui7AXZ2bB/T9KWEUHFHYgW9Y3G2cY9LbA==')}); return false;">(add)</a>
            <img style="display:none" id="loading_anim_449839" class="loading" src="https://s.gr-assets.com/assets/loading-trans-ced157046184c3bc7c180ffbfc6825a4.gif" alt="Loading trans">
        </div>
    </td>
    
    <td class="field format" style="display: none">
        <label>format</label>
        <div class="value">
            Hardcover
            <a class="smallText" href="/work/editions/527941">
                [edit]
            </a>
        </div>
    </td>
    
    <td class="field actions">
        <label>actions</label>
        <div class="value">
            <div class="actionsWrapper greyText smallText">
                <div class="editLinkWrapper">
                    <a id="loading_link_71532" class="actionLinkLite editLink" href="#" onclick="new Ajax.Request('/review/edit/9673436', {asynchronous:true, evalScripts:true, onFailure:function(request){Element.hide('loading_anim_71532');$('loading_link_71532').innerHTML = '<span class=&quot;error&quot;>ERROR</span>try again';$('loading_link_71532').show();;Element.hide('loading_anim_71532');}, onLoading:function(request){;Element.show('loading_anim_71532');Element.hide('loading_link_71532')}, onSuccess:function(request){Element.hide('loading_anim_71532');Element.show('loading_link_71532');}, parameters:'authenticity_token=' + encodeURIComponent('VaLsMzLcqSiazA03Tx/6FyBAX4Bg11unt2eKhlSdj0nt5PqB3DgHTdw4T3GQNh0TJ0dqkzxNxbmYQjswnPPVOQ==')}); return false;">edit</a>
                    <img style="display:none" id="loading_anim_71532" class="loading" src="https://s.gr-assets.com/assets/loading-trans-ced157046184c3bc7c180ffbfc6825a4.gif" alt="Loading trans">
                </div>
                <div class="viewLinkWrapper">
                    <a class="actionLinkLite viewLink nobreak" href="/review/show/391002311">view »</a>
                </div>
                <a class="actionLinkLite smallText deleteLink" data-confirm="Are you sure you want to remove The Invention of Hugo Cabret from your books? This will permanently remove this book from your shelves, including any review, rating, tags, or notes you have added. To change the shelf this book appears on please edit the shelves." rel="nofollow" data-method="post" href="/review/destroy/9673436?return_url=https%3A%2F%2Fwww.goodreads.com%2Freview%2Flist%2F11838413-anna%3Futf8%3D%25E2%259C%2593%26ref%3Dnav_mybooks%26shelf%3Dread%26title%3Danna%26per_page%3Dinfinite">
                    <img alt="Remove from my books" title="Remove from my books" src="https://s.gr-assets.com/assets/layout/delete-a9a86f59648bf17079954ea50a673dbc.png">
                    <span class="label">remove book</span>
                </a>
            </div>
        </div>
    </td>
</tr>

"""
"""
  "Book Id", "Title", "Author", "Author l-f", "Additional Authors", "ISBN", "ISBN13", "My Rating", "Average Rating","Publisher","Binding","Number of Pages","Year Published","Original Publication Year","Date Read","Date Added","Bookshelves","Bookshelves with positions","Exclusive Shelf","My Review","Spoiler","Private Notes","Read Count","Recommended For","Recommended By","Owned Copies","Original Purchase Date","Original Purchase Location","Condition","Condition Description","BCID"
"""
