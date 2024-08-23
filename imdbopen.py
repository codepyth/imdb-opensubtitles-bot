import os
import re
import requests
from bs4 import BeautifulSoup

def sanitize_filename(filename):
    # Remove any invalid characters for filenames (e.g., /, \, :, *, ?, ", <, >, |)
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = filename.replace("\n", " ")  # Replace newlines with spaces
    return filename.strip()

def get_movie_details(imdb_id):
    # Extract the numeric part of the IMDb ID
    imdb_numeric_id = imdb_id[2:]
    
    # Construct the URL
    url = f"https://www.opensubtitles.org/en/search/sublanguageid-ara,eng,fre/imdbid-{imdb_numeric_id}"
    
    # Send a request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract movie details
        movie_title = soup.find('h1').text.strip()  # Assuming the title is in an h1 tag
        print(f"Movie Title: {movie_title}")
        
        # Create a folder for the movie
        sanitized_movie_title = sanitize_filename(movie_title.replace(" ", "_"))
        folder_name = f"{sanitized_movie_title}_subtitles"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Extract subtitle rows
        rows = soup.find_all('tr', class_='change')  # Find all rows with subtitles
        
        total_subtitles = 0  # Counter for downloaded subtitles
        
        for index, row in enumerate(rows):
            # Extract subtitle title
            subtitle_title_element = row.find('strong').find('a')
            subtitle_title = sanitize_filename(subtitle_title_element.text.strip()) if subtitle_title_element else f"Subtitle_{index}"
            
            
            # Extract language
            language_td = row.find('td', align='center', style=True)  # Find <td> with style attribute
            language_element = language_td.find('a') if language_td else None
            language = language_element.get('title', 'Unknown_Language') if language_element else 'Unknown_Language'
            language = sanitize_filename(language)  # Sanitize language name
            
          
            # Extract subtitle download link
            download_td = row.find('td', align='center')
            download_link_element = download_td.find('a', href=True) if download_td else None
            if download_link_element and 'sub' in download_link_element['href']:
                download_link = download_link_element['href']
                subtitle_download_url = f"https://www.opensubtitles.org{download_link}"
                
                # Download the subtitle file
                subtitle_response = requests.get(subtitle_download_url)
                subtitle_filename = os.path.join(folder_name, f"{subtitle_title}_{language}_Subtitle_{index+1}.srt")
                
                if subtitle_response.status_code == 200:
                    with open(subtitle_filename, 'wb') as file:
                        file.write(subtitle_response.content)
                        print(f"Downloaded:{subtitle_title}_{language}_Subtitle_{index+1}.srt")
                    total_subtitles += 1
                else:
                    print(f"Failed to download subtitle: {subtitle_filename}")
    
        print(f"Total subtitles downloaded: {total_subtitles}")
    
    else:
        print(f"Failed to retrieve data for IMDb ID {imdb_id}.")

# Prompt the user to enter a specific IMDb ID
imdb_id = 'tt1981115'
get_movie_details(imdb_id)
