#!/usr/bin/env python3

import click
import youtube_dl
from playwright.sync_api import sync_playwright


@click.command()
@click.option('-u', '--username', required=True, help="cda.pl username")
@click.option('-p', '--password', required=True, help="cda.pl password")
@click.option('-f', '--folder-url', required=True, help="cda.pl folder url")
@click.option('-d', '--dest-path', required=True, help="downloads destination path")
def main(username, password, folder_url, dest_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        login(page, username, password)
        urls = scrape_folder_urls(page, folder_url)

        with youtube_dl.YoutubeDL({'outtmpl': f"{dest_path}/%(title)s.%(ext)s"}) as ydl:
            ydl.download(urls)

        browser.close()


def login(page, username, password):
    page.goto("https://www.cda.pl/login")

    login_form = page.query_selector('#logowanieContainer *> form[action="https://www.cda.pl/login"]')
    username_input = login_form.query_selector('input[name="username"]')
    password_input = login_form.query_selector('input[name="password"]')
    login_form_submit = login_form.query_selector('button')

    username_input.fill(username)
    password_input.fill(password)
    login_form_submit.click()


def get_next_folder_url(page):
    next_link = page.query_selector('.paginationControl *> .next')
    if next_link:
        return next_link.get_attribute('href')
    return None


def scrape_folder_urls(page, folder_url):
    page.goto(folder_url)

    urls = []
    urls += map(lambda video_link_element: f'https://www.cda.pl{video_link_element.get_attribute("href")}',
                page.query_selector_all('.thumbnail-link'))

    next_folder_url = get_next_folder_url(page)
    if next_folder_url:
        urls += scrape_folder_urls(page, next_folder_url)

    return urls


if __name__ == "__main__":
    main()
