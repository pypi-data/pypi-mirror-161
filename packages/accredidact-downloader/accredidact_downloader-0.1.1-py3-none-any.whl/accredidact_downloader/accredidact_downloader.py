__version__ = '0.1.1'

import appdirs
import argparse
import bs4
import configparser
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
import os
import re
import requests
from sanitize_filename import sanitize
import smtplib
from tabulate import tabulate
import tempfile
import threading
import urllib


class YearAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        years = []
        for elt in values:
            m = re.match(r'(\d{4})(?:-(\d{4}))?$', elt)
            if not m:
                raise argparse.ArgumentTypeError("'" + elt + "' is not a valid argument. Expected a (range of) 4-digit number(s)")
            elif m[1] and m[2]:
                years.extend(range(int(m[1]), int(m[2])+1))
            elif m[1]:
                years.append(int(m[1]))
                years.sort()
        setattr(namespace, self.dest, years)


class _AccreDidact(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Double-checked locking pattern
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(_AccreDidact, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AccreDidact(metaclass=_AccreDidact):
    def __init__(self):
        self._verbose = False
        self._session = requests.Session()
        self._base_url = 'https://www.accredidact.nl/'
        self._login_success_msg = 'U bent nu ingelogd'

    def get_verbose(self):
        return self._verbose

    def set_verbose(self, verbose=True):
        self._verbose = verbose

    def get_session(self):
        return self._session

    def get_base_url(self):
        return self._base_url

    def login(self, username, password):
        if self._verbose:
            print("Going to login page...")
        response = self._session.get(self._base_url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        form = soup.find('form', {'id': 'loginform'})
        params = {'loginform_submit': 1,
                  'loginform_formCheck': None,
                  'username': username,
                  'wachtwoord': password}
        if self._verbose:
            print("Logging in...")
        response = self._session.post(self._base_url, data=params)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        if self._verbose:
            print("Logging in...done")


class Archive:
    def __init__(self):
        singleton = AccreDidact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self._archive_url = urllib.parse.urljoin(self._base_url, '/mijn-dossier/archief')

    @cached_property
    def issues(self):
        return [Issue(**kwargs) for kwargs in self._fetch()]

    def _fetch(self):
        if self._verbose:
            print(f"Going to archive page {self._archive_url}...")
        response = self._session.get(self._archive_url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        archive = soup.find('div', {'class': 'archief'})
        result = []
        items = archive.find_all('div', {'class': 'archief-artikel'})
        items.reverse()
        for item in items:
            source = item.find('div', {'class': 'artikel__button-container'}).a.attrs['href']
            url = urllib.parse.urljoin(self._base_url, source)
            subtitle = item.find('h4', {'class': 'archief-artikel__ondertitel'}).a.get_text().strip()
            result.append({'id': subtitle.replace('/', '-'),
                           'title': item.find('h3', {'class': 'archief-artikel__title'}).a.get_text().strip(),
                           'url': url})
        return result


class Issue:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.title = kwargs['title']
        self.url = kwargs['url']
        singleton = AccreDidact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()

    @cached_property
    def pdf(self):
        if self.url:
            return self._fetch_pdf(self.url)

    def _fetch_pdf(self, url):
        if self._verbose:
            print(f'Fetching pdf {url}...')
        try:
            response = self._session.get(url)
            response.raise_for_status()
        except urllib.error.HTTPError as e:
            print(e)
        else:
            with tempfile.TemporaryFile() as temp:
                for chunk in response.iter_content(chunk_size=128):
                    temp.write(chunk)
                    temp.seek(0)
                    data = temp.read()
                return data

    def write_pdf(self, path):
        if self.pdf:
            with open(path, 'wb') as f:
                f.write(self.pdf)


def validate_path(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{path}: No such file or directory")
    elif not os.access(path, os.W_OK):
        raise argparse.ArgumentTypeError(f"{path}: Permission denied")
    else:
        return path


def get_config_path(dirs, config):
    filename = 'config.ini'
    local_path = os.path.join(dirs.user_config_dir, filename)
    system_path = os.path.join(dirs.site_config_dir, filename)
    if config:
        return config.name
    elif os.path.exists(local_path):
        return local_path
    elif os.path.exists(system_path):
        return system_path
    else:
        return None


def email(smtp_host=None,
          smtp_port=None,
          smtp_username=None,
          smtp_password=None,
          sender=None,
          recipient=None,
          subject=None,
          body=None,
          attachment=None):
    from_addr = sender
    if not isinstance(recipient, list):
        to_addrs = [recipient]
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ", ".join(to_addrs)
    if subject:
        if isinstance(subject, str):
            msg['Subject'] = subject
        elif isinstance(subject, list):
            msg['Subject'] = ' '.join(subject)
    if body:
        if isinstance(body, str):
            msg.attach(MIMEText(body, 'plain'))
        elif isinstance(body, list):
            msg.attach(MIMEText(' '.join(body), 'plain'))
    filename = os.path.basename(attachment)
    with open(attachment, 'rb') as f:
        file = MIMEApplication(f.read(),
                               name=filename)
    file['Content-Disposition'] = f'attachment; filename = "{filename}"'
    msg.attach(file)
    # Initiate the SMTP connection
    smtp = smtplib.SMTP(smtp_host, smtp_port)
    # Send an EHLO (Extended Hello) command
    smtp.ehlo()
    # Enable transport layer security (TLS) encryption
    smtp.starttls()
    # Authenticate
    smtp.login(smtp_username, smtp_password)
    # Send mail
    smtp.sendmail(from_addr, to_addrs, msg.as_string())
    # Quit the server connection
    smtp.quit()


def main():
    parser = argparse.ArgumentParser()
    config = configparser.ConfigParser()
    parser.add_argument('-v',
                        '--verbose',
                        help='explain what is being done',
                        action='store_true')
    parser.add_argument('-f',
                        '--force',
                        help='do not prompt before overwriting (overrides a previous -n option)',
                        action='store_true')
    parser.add_argument('-n',
                        '--no_clobber',
                        help='do not overwrite an existing file',
                        action='store_true')
    parser.add_argument('-l',
                        '--list',
                        help='List the issues of the current year. When used in conjunction with --id or --year, list the selected IDs or years respectively.',
                        action='store_true')
    parser.add_argument('-d',
                        '--download',
                        help='Download the latest issue. When used in conjunction with --id or --year, download the selected IDs or years respectively.',
                        action='store_true')
    parser.add_argument('-e',
                        '--email',
                        help='Send the latest issue as an attachment via email. When used in conjunction with --id or --year, send the selected IDs or years respectively. This option presumes the --download option.',
                        action='store_true')
    parser.add_argument('-i',
                        '--id',
                        help='Select the ID(s) for use by subsequent options. Add more arguments to select more than one ID, such as "-i 2022-4 2022-5".',
                        nargs="*")
    parser.add_argument('-y',
                        '--year',
                        help='Select the year(s) for use by subsequent options. Add more arguments to select more than one year, such as "-y 2002 2004 2006-2008" to operate on the years 2002, 2004, 2006, 2007, and 2008.',
                        nargs="*",
                        action=YearAction)
    parser.add_argument('-u',
                        '--username',
                        help='Set the username for authentication')
    parser.add_argument('-p',
                        '--password',
                        help='Set the password for authentication')
    parser.add_argument('-w',
                        '--download_dir',
                        help='Set the download directory.',
                        type=validate_path)
    parser.add_argument('-c',
                        '--config',
                        help='Specify the location of a config file.',
                        type=argparse.FileType('r'))
    parser.add_argument('--smtp_host',
                        help='Set the host name or ip address of the SMTP server (for example "smtp.gmail.com"). If omitted the OS default behavior will be used.')
    parser.add_argument('--smtp_port',
                        help='Set the port of the SMTP server (for example "587"). If omitted the OS default behavior will be used.')
    parser.add_argument('--smtp_username',
                        help='Set the account name, user name, or email address of your email account for authentication.')
    parser.add_argument('--smtp_password',
                        help='Set password of your email account for authentication. Please note that if you use 2-step-verification in a Gmail-account, you might need an App Password (see https://support.google.com/accounts/answer/185833).')
    parser.add_argument('--sender',
                        help='Set the sender\'s email address.')
    parser.add_argument('--recipient',
                        help='Set the recipient\'s email address.',
                        nargs="*",
                        action='extend')
    parser.add_argument('--subject',
                        help='Set the subject of an email message.',
                        nargs="*")
    parser.add_argument('--body',
                        help='Set the body of an email message.',
                        nargs="*")

    args = parser.parse_args()

    dirs = appdirs.AppDirs('accredidact-downloader', 'Folkert van der Beek')
    config_path = get_config_path(dirs, args.config)

    if config_path:
        config.read(config_path)
        settings = {}
        for section in config.sections():
            settings.update(dict(config[section]))
            settings.update({key: value for key, value in vars(args).items() if value is not None})
    else:
        settings = vars(args)

    username = settings.get('username')
    password = settings.get('password')

    # singleton instance
    AD = AccreDidact()

    if settings.get('verbose'):
        AD.set_verbose(True)

    if username and password:
        AD.login(username, password)
    else:
        raise Exception("No username and password provided")

    issues = []

    years = settings.get('year')
    if years:
        for year in years:
            for issue in Archive().issues:
                m = re.match(r'(\d{4})-(\d{1})$', issue.id)
                if str(year) == m[1]:
                    issues.append(issue)

    ids = settings.get('id')
    if ids:
        for id in ids:
            for issue in Archive().issues:
                if issue.id == id:
                    issues.append(issue)

    if settings.get('list'):
        if len(issues) == 0:
            issues.extend(Archive().issues)
        headers = ['ID', 'Title', 'URL']
        data = [[issue.id, issue.title, issue.url] for issue in issues]
        print(tabulate(data, headers, tablefmt='plain'))

    if settings.get('email'):
        settings['download'] = True

    if settings.get('download'):
        download_dir = settings.get('download_dir') if settings.get('download_dir') else dirs.user_data_dir
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)

        # Select the latest issue if none is selected
        if len(issues) == 0:
            issues.append(Archive().issues[-1])

        for issue in issues:
            filename = issue.id + ' ' + issue.title + '.pdf'
            path = os.path.join(download_dir, sanitize(filename))
            if not os.path.exists(path):
                issue.write_pdf(path)
                if settings.get('email'):
                    email(smtp_host=settings.get('smtp_host'),
                          smtp_port=settings.get('smtp_port'),
                          smtp_username=settings.get('smtp_username'),
                          smtp_password=settings.get('smtp_password'),
                          sender=settings.get('sender') if settings.get('sender') else settings.get('smtp_username'),
                          recipient=settings.get('recipient'),
                          subject=settings.get('subject') if settings.get('subject') else issue.title,
                          body=settings.get('body'),
                          attachment=path)
            elif settings.get('force'):
                issue.write_pdf(path)
                if settings.get('email'):
                    email(smtp_host=settings.get('smtp_host'),
                          smtp_port=settings.get('smtp_port'),
                          smtp_username=settings.get('smtp_username'),
                          smtp_password=settings.get('smtp_password'),
                          sender=settings.get('sender') if settings.get('sender') else settings.get('smtp_username'),
                          recipient=settings.get('recipient'),
                          subject=settings.get('subject') if settings.get('subject') else issue.title,
                          body=settings.get('body'),
                          attachment=path)
            elif settings.get('no_clobber'):
                pass
            else:
                overwrite = input(f"overwrite '{path}'? ")
                if overwrite in ['y', 'Y', 'yes', 'Yes']:
                    issue.write_pdf(path)
                    if settings.get('email'):
                        email(smtp_host=settings.get('smtp_host'),
                              smtp_port=settings.get('smtp_port'),
                              smtp_username=settings.get('smtp_username'),
                              smtp_password=settings.get('smtp_password'),
                              sender=settings.get('sender') if settings.get('sender') else settings.get('smtp_username'),
                              recipient=settings.get('recipient'),
                              subject=settings.get('subject') if settings.get('subject') else issue.title,
                              body=settings.get('body'),
                              attachment=path)


if __name__ == '__main__':
    main()
