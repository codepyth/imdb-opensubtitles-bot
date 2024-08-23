import os
import re
import requests
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = filename.replace("\n", " ")
    return filename.strip()

def get_movie_details(imdb_id):
    imdb_numeric_id = imdb_id[2:]
    url = f"https://www.opensubtitles.org/en/search/sublanguageid-ara,eng,fre/imdbid-{imdb_numeric_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    }
    
    session = requests.Session()
    response = session.get(url, headers=headers, allow_redirects=True)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        movie_title = soup.find('h1').text.strip()
        print(f"Movie Title: {movie_title}")
        return movie_title, soup.find_all('tr', class_='change')
    else:
        print(f"Failed to retrieve data for IMDb ID {imdb_id}.")
        return None, None

def download_subtitles(movie_title, rows):
    sanitized_movie_title = sanitize_filename(movie_title.replace(" ", "_"))
    folder_name = f"{sanitized_movie_title}_subtitles"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    total_subtitles = 0
    
    for index, row in enumerate(rows):
        subtitle_title_element = row.find('strong').find('a')
        subtitle_title = sanitize_filename(subtitle_title_element.text.strip()) if subtitle_title_element else f"Subtitle_{index}"
        language_td = row.find('td', align='center', style=True)
        language_element = language_td.find('a') if language_td else None
        language = language_element.get('title', 'Unknown_Language') if language_element else 'Unknown_Language'
        language = sanitize_filename(language)

        download_link = None
        for td in row.find_all('td', align='center'):
            download_link_element = td.find('a', href=True)
            if download_link_element and "/en/subtitleserve/sub/" in download_link_element['href']:
                download_link = f"https://dl.opensubtitles.org{download_link_element['href']}"
                break

        if download_link:
            subtitle_filename = os.path.join(folder_name, f"{subtitle_title}_{language}_Subtitle_{index+1}.zip")
            subtitle_filename_print = f"{subtitle_title}_{language}_Subtitle_{index+1}.zip"
            response = requests.get(download_link, allow_redirects=True)
            if response.status_code == 200:
                with open(subtitle_filename, 'wb') as file:
                    file.write(response.content)
                    print(f"Downloaded: {subtitle_filename_print}")
                total_subtitles += 1
            else:
                print(f"Failed to download subtitle: {subtitle_filename_print}")
    
    print(f"Total subtitles downloaded: {total_subtitles}")

def main():
    imdb_id = input("Enter IMDb ID: ")
    movie_title, rows = get_movie_details(imdb_id)
    if movie_title and rows:
        download_choice = input(f"Do you want to download subtitles for {movie_title}? (yes/no): ").strip().lower()
        if download_choice == 'yes' or download_choice == 'y':
            download_subtitles(movie_title, rows)
        else:
            print("Download canceled.")

if __name__ == "__main__":
    main()
