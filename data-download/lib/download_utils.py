import os


def ensure_slash(value):
    if not value.endswith('/'):
        return value + '/'
    else:
        return value


def download_file(session, name, url, download_folder):
    file_size = int(session.head(url).headers['Content-Length'])
    file_name = ensure_slash(download_folder) + name

    if not os.path.isfile(file_name) or os.path.getsize(file_name) != file_size:
        response = session.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=2000000):
                f.write(chunk)
        if response.status_code is 200:
            print('Successfully downloaded:' + file_name)
        else:
            print('Download for:' + file_name + ' failed')
    else:
        print('File:' + file_name + ' already downloaded')
