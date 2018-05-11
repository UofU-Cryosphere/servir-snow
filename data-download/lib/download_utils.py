import os

from datetime import date, datetime, timedelta


def ensure_folder(folder):
    if not (os.path.isdir(folder)):
        os.mkdir(folder)

    return folder


def dates_in_range(year, from_day, to_day):
    start_date = datetime(year, 1, 1) + timedelta(from_day - 1)
    end_date = datetime(year, 1, 1) + timedelta(to_day)

    dates = [
        date.fromordinal(i)
        for i in range(start_date.toordinal(), end_date.toordinal())
    ]

    print('Downloading files from: ' +
          str(dates[0].strftime("%Y-%m-%d")) + ' to: ' +
          str(dates[-1].strftime("%Y-%m-%d")))
    return dates


def download_file(session, name, url, download_folder):
    file_size = int(session.head(url).headers['Content-Length'])
    file_name = os.path.join(download_folder, name)

    if not os.path.isfile(file_name) or os.path.getsize(file_name) != file_size:
        response = session.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=2000000):
                f.write(chunk)
        if response.status_code is 200:
            print('Successfully downloaded: ' + name)
        else:
            print('Download for: ' + name + ' failed')
    else:
        print('File: ' + name + ' already downloaded')
