import os
import requests

def read_channels_txt(channels_file):
    with open(channels_file, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def extract_logo(line, default_logo):
    try:
        logo = line.split('tvg-logo="')[1].split('"')[0]
        if not logo:
            return default_logo
        else:
            return logo
    except IndexError:
        return default_logo

def filter_channels(playlist_sources, channel_categories):
    default_logo = "https://raw.githubusercontent.com/FunctionError/Logos/main/Pirates-Tv.png"
    default_source = 'https://raw.githubusercontent.com/FunctionError/Logos/main/PiratesTv/master.m3u8'
    filtered_channels = {}
    for source in playlist_sources:
        response = requests.get(source)
        lines = response.text.split('\n')
        for i in range(len(lines)):
            if lines[i].startswith('#EXTINF') and len(lines[i].split(',')) > 1:
                name = lines[i].split(',')[1].strip()
                url = lines[i + 1].strip()
                category = channel_categories.get(name)
                if category:
                    logo = extract_logo(lines[i], default_logo)
                    if check_channel_status(url):
                        if name not in filtered_channels:
                            filtered_channels[name] = {'url': url, 'logo': logo, 'category': category, 'source': source}
                    else:
                        # If channel source is inactive, use default source
                        filtered_channels[name] = {'url': default_source, 'logo': logo, 'category': category, 'source': source}
    return filtered_channels

def check_channel_status(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def write_m3u(output_file, channels, custom_categories):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        file.write("# All the links in this file are collected from public sources. If anyone wants to remove their source, please let us know. We respect your opinions and efforts, so we will not object to removing your source. https://www.t.me/PiratesTv_ch\n")
        for name, data in channels.items():
            url = data['url']
            logo = data['logo']
            category = data['category']
            custom_category = custom_categories.get(category, category)  
            source = data['source']
            file.write(f"#EXTINF:-1 tvg-logo=\"{logo}\" group-title=\"{custom_category}\",{name}\n")
            file.write(f"{url}\n")

def main():
    playlist_sources = [
        os.getenv('PLAYLIST_SOURCE_URL_1'),
        os.getenv('PLAYLIST_SOURCE_URL_2'),
        os.getenv('PLAYLIST_SOURCE_URL_3')
    ]
    channels_file = 'channels.txt'
    output_file = 'PiratesPlus.m3u'

    # Read channel names and categories from channels.txt
    channel_categories = {}
    with open(channels_file, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                channel_categories[parts[0]] = parts[1]

    # Filter channels based on channel categories and status
    filtered_channels = filter_channels(playlist_sources, channel_categories)

    # Read custom categories from channels.txt
    custom_categories = {}
    with open(channels_file, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                custom_categories[parts[1]] = parts[1]

    # Write filtered channels to output M3U file
    write_m3u(output_file, filtered_channels, custom_categories)

if __name__ == "__main__":
    main()
