import click
import csv
import requests
import time
import traceback
from http.cookiejar import MozillaCookieJar
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

RATING_TO_SHORTCUT = {
    "General Audiences": "G",
    "Teen And Up Audiences": "T",
    "Mature": "M",
    "Explicit": "E",
    "Not Rated": "Not Rated"
}


@click.command()
@click.option("--username",
              prompt="AO3 username",
              help="(required) The AO3 username to get history from.")
@click.option("--cookies",
              prompt="Path to cookies file for the AO3 account",
              help="(required) Path to the cookies file for the AO3 account.")
@click.option("--out", help="Path to save the archive CSV to. (default: archivist-username-[history/markedforlater]-timestamp-pagerange.csv)")
@click.option("--start", type=int, help="Which page number to start from.")
@click.option("--end", type=int, help="Which page number to end on.")
@click.option("--later",
              is_flag=True,
              default=False,
              help="Flag to archive Marked for Later instead of History.")
def main(username, cookies, out, start, end, later):
    """Exports AO3 reading history to a CSV file."""
    archive_ao3_history(username, cookies, out, start, end, later)


def archive_ao3_history(username,
                        cookie_path,
                        out,
                        start,
                        end,
                        marked_for_later=False):
    section_to_archive = "Marked for Later" if marked_for_later else "reading history"
    click.secho(f'🔎 Loading {section_to_archive}...', fg="cyan")

    # Load AO3 history page to find page numbers
    cookies = get_cookie_jar(cookie_path)

    num_retries = 0
    success = False
    while success == False and num_retries < 3:
        soup = get_soup_for_history_page(username, cookies, marked_for_later)
        try:
            num_pages = parse_num_pages_from_soup(soup)
            success = True
        except IndexError:
            click.secho(
                "❌ Couldn’t load pages! This could mean we were rate limited by AO3. Waiting 1 minute before trying again...",
                fg="red")
            num_retries += 1
            time.sleep(60)

    if success == "False":
        click.secho(
            "❌ Could not load pages after retrying. Your cookies may have expired. Please re-export them before trying again.",
            fg="red")
        return

    # Prompt for page numbers to archive
    pages_message = f'📚 You have {num_pages} pages of {section_to_archive}.'
    click.secho(pages_message, fg="cyan")
    if start is None or start < 1 or start > num_pages:
        num_page_start = click.prompt("Which page to start archiving from?",
                                      type=int,
                                      default=1)
    else:
        num_page_start = max(start, 1)

    if (end is None and start is None) or (end is not None
                                           and end < num_page_start):
        num_page_end = click.prompt("Which page to stop archiving on?",
                                    type=int,
                                    default=num_pages)
    else:
        num_page_end = min(end, num_pages) if end is not None else num_pages

    click.secho(
        f'📚 Archiving pages {num_page_start} to {num_page_end} of {section_to_archive}...',
        fg="cyan")

    start_time = time.time()
    num_works_archived = 0
    num_works_skipped = 0
    archive_data = []
    last_page_saved = None
    for page in range(num_page_start, num_page_end + 1):
        click.echo(f'Archiving page {page}...')
        if (page != num_page_start):
            # AO3 allows 60 rpm; to be safe, target 30 rpm (1 request every 2 seconds)
            time.sleep(2)

        try:
            [data, num_archived, num_skipped] = get_archive_data_for_history_page(username, cookies,
                                                     marked_for_later, page)
            if data is None:
                # We skipped this work
                continue
            archive_data.extend(data)
            num_works_archived += num_archived
            num_works_skipped += num_skipped
            last_page_saved = page
            click.secho('...done!', fg="green")
        except KeyboardInterrupt:
            click.secho("❌ You stopped the script!", fg="red")
            click.echo(f'Script will save data up to page {page-1} and abort.')
            break
        except:
            click.secho("❌ Error loading this page!", fg="red")
            click.echo(
                f'Script will save data up to page {page-1} and abort. Please share the error with the developer:'
            )
            click.echo(traceback.print_exc())
            break

    elapsed_time = timedelta(seconds=time.time() - start_time)
    click.secho("Saving to file...")
    save_path = out if out is not None else generate_default_filename(
        username, marked_for_later, num_page_start, last_page_saved)
    save_archive_to_csv(archive_data, save_path)
    click.secho(f'\n🎉 Finished archiving {section_to_archive}!', fg="cyan")
    click.echo(f'📚 Works Archived:  {num_works_archived}')
    click.echo(f'⛔️ Works Missing:   {num_works_skipped}')
    click.echo(f'🔎 Time to Archive: {elapsed_time}')


def get_cookie_jar(cookie_path):
    cookie_jar = MozillaCookieJar(cookie_path)
    cookie_jar.load(ignore_expires=True, ignore_discard=True)
    return cookie_jar


def get_history_url_and_params(username, marked_for_later, page=None):
    history_url = f'https://archiveofourown.org/users/{username}/readings'

    params = {}
    if marked_for_later:
        params['show'] = 'to-read'
    if page:
        params['page'] = page

    return (history_url, params)


def get_soup_for_history_page(username, cookies, marked_for_later, page=None):
    url, params = get_history_url_and_params(username, marked_for_later, page)
    r = requests.get(url, params=params, cookies=cookies)
    return BeautifulSoup(r.text, 'lxml')


def get_archive_data_for_history_page(username, cookies, marked_for_later,
                                      page):
    num_retries = 0
    success = False
    while success == False and num_retries < 3:
        soup = get_soup_for_history_page(username, cookies, marked_for_later,
                                         page)
        try:
            works = soup.find_all('ol', {'class': 'reading'})[0].find_all(
                "li", {"class": "work"})
            success = True
        except IndexError:
            click.secho(
                "❌ No works found! This could mean we were rate limited by AO3. Waiting 1 minute before trying again...",
                fg="red")
            num_retries += 1
            time.sleep(60)

    if success == "False":
        click.secho(
            "❌ Could not find works after retrying. There might be an error on this page — skipping.",
            fg="red")
        return []

    data = []
    num_archived = 0
    num_skipped = 0
    for work in works:
        work_data = get_archive_data_for_work_soup(work)
        if work_data is None:
            num_skipped += 1
        else:
            num_archived += 1
            data.append(work_data)

    return [data, num_archived, num_skipped]


def get_archive_data_for_work_soup(soup):
    # TITLE
    heading_container = soup.find_all("h4", {"class": "heading"})[0]
    try:
        title_container = heading_container.find_all('a')[0]
        title = title_container.string.strip()
    except IndexError:
        # No title means it's been hidden or deleted — abort
        click.secho(
            "⛔️ A work on this page has been hidden or deleted, so we can’t archive it",
            fg="red")
        return None

    # URL
    url = f'https://archiveofourown.org{title_container["href"]}'

    # AUTHOR
    authors = soup.find_all('a', {'rel': 'author'})
    if len(authors) == 0:
        author = 'Anonymous'
    else:
        author = ', '.join([author.string for author in authors])

    # SUMMARY
    summary_container = soup.find_all('blockquote', {'class': 'summary'})
    try:
        raw_summary = summary_container[0].find_all('p')
        summary = '\n\n'.join(
            [p.get_text('\n') for p in raw_summary if p is not None])
    except IndexError:
        summary = ''

    # WORD COUNT
    word_count = soup.find_all('dd',
                               {'class': 'words'})[0].string.replace(',', '')

    # CHAPTERS
    chapters = soup.find_all('dd', {'class': 'chapters'})[0].text
    [published_chapters, total_chapters] = chapters.split("/")

    # LANGUAGE
    language = soup.find_all('dd', {'class': 'language'})[0].string

    # RATING
    full_rating = soup.find_all("span", {"class": "rating"})[0]['title']
    rating = RATING_TO_SHORTCUT[full_rating]

    # FANDOMS
    fandoms_container = soup.find_all('h5', {'class': 'fandoms'})[0]
    fandom_tags = fandoms_container.find_all('a', {'class': 'tag'})
    fandoms = ', '.join([tag.string for tag in fandom_tags])

    # TAGS
    tags_container = soup.find_all('ul', {'class': 'tags'})[0]
    warnings = parse_tags(tags_container, 'warnings')
    # not required tags
    relationship_tags = parse_tags(tags_container, 'relationships')
    character_tags = parse_tags(tags_container, 'characters')
    freeform_tags = parse_tags(tags_container, 'freeforms')

    # LAST VISITED
    last_visited_details = soup.find_all('h4', {'class': 'viewed'})[0].text
    # The string always has the format "Last visited: [Date] (details)"
    last_visited = last_visited_details.split("(")[0][15:-1].strip()

    return {
        "URL": url,
        "Title": title,
        "Author": author,
        "Summary": summary,
        "Rating": rating,
        "Warnings": warnings,
        "Fandom": fandoms,
        "Relationships": relationship_tags,
        "Characters": character_tags,
        "Tags": freeform_tags,
        "Word Count": int(word_count),
        "Published Chapters": int(published_chapters),
        "Total Chapters": total_chapters,
        "Language": language,
        "Last Visited": last_visited
    }


def parse_tags(tags_container, tag_name):
    tags = tags_container.find_all('li', {'class': tag_name})
    return ', '.join([tag.string for tag in tags])


def parse_num_pages_from_soup(soup):
    # Find the pagination buttons on the bottom of the page
    pages = soup.find_all("ol", {"class": "pagination"})[0].find_all("li")
    # The last item is the "Next" button; the 2nd to last is the last page
    return int(pages[-2].string)


def generate_default_filename(username, marked_for_later, start_page,
                              end_page):
    section = 'markedforlater' if marked_for_later else 'history'
    now = datetime.now()
    datetime_string = now.strftime("%y%m%d%H%M")
    return f'archivist-{username}-{section}-{datetime_string}-{start_page}to{end_page}.csv'


def save_archive_to_csv(data, path):
    with open(path, mode='w') as csv_file:
        fieldnames = [
            "URL", "Title", "Author", "Summary", "Rating", "Warnings",
            "Fandom", "Relationships", "Characters", "Tags", "Word Count",
            "Published Chapters", "Total Chapters", "Language", "Last Visited"
        ]
        writer = csv.DictWriter(csv_file, fieldnames)
        writer.writeheader()

        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    main()
