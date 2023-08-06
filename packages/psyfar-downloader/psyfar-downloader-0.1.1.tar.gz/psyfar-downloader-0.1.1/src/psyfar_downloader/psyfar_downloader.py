__version__ = '0.1.1'

import appdirs
import argparse
import bs4
import configparser
import copy
from ebooklib import epub
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
import html
import json
import mimetypes
import os
import re
import requests
from sanitize_filename import sanitize
import smtplib
from tabulate import tabulate
import tempfile
import threading
import urllib
import uuid
import w3lib.url

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


class IssueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ids = []
        for elt in values:
            m = re.match(r'(\d{4})-(\d{1,2})$', elt)
            if not m:
                raise ValueError("'" + elt + "' is not a valid ID. Expected 4 digits, a dash and 1 or 2 digits")
            elif int(m[2]) < 1:
                raise ValueError("'" + elt + "' is not a valid ID. Expected a number greater than or equal to 1 after the dash")
            else:
                ids.append({'year': int(m[1]), 'issue': int(m[2]) - 1})
                ids.sort(key=lambda elt: (elt['year'], elt['issue']))
        setattr(namespace, self.dest, ids)


class _Psyfar(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Double-checked locking pattern
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(_Psyfar, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Psyfar(metaclass=_Psyfar):
    def __init__(self):
        self._verbose = False
        self._session = requests.Session()
        self._base_url = 'https://www.psyfar.nl/'
        self._login_url = urllib.parse.urljoin(self._base_url, '/inloggen')
        self._action_url = urllib.parse.urljoin(self._base_url, '/front_gebruiker/login-formulier/check-login')

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
        response = self._session.get(self._login_url)
        params = {'username': username,
                  'wachtwoord': password}
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        if self._verbose:
            print("Logging in...")
        response = self._session.post(self._action_url, data=params, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        result = json.loads(soup.p.get_text())
        success = result.get('success')
        if success and self._verbose:
            print("Logging in...done")
        elif not success:
            raise Exception("Logging in failed")


class Archive:
    def __init__(self, year=None):
        singleton = Psyfar()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self._archive_url = urllib.parse.urljoin(self._base_url, '/tijdschrift')
        self.year = year

    @cached_property
    def issues(self):
        return [Issue(**kwargs) for kwargs in self._fetch(self.year)]

    def _fetch(self, year):
        if self._verbose:
            print(f"Going to archive page {self._archive_url}...")
        response = self._session.get(self._archive_url, params={'jaar': year} if year else None)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        if year:
            year = str(year)
        else:
            year = soup.find('li', {'class': 'active'}).a.get_text()
        archive_items = soup.find_all('article', {'class': 'tijdschriften__item'})
        archive_items.reverse()
        result = []
        for idx, archive_item in enumerate(archive_items):
            result.append({'id': year + "-" + str(idx+1),
                           'cover_url': archive_item.find('p', {'class': 'tijdschriften__itemCover'}).a.img.attrs['src'].strip(),
                           'title': archive_item.find('h2', {'class': 'tijdschriften__itemTitel'}).a.get_text().strip(),
                           'url': urllib.parse.urljoin(self._base_url, archive_item.find('a', {'class': 'button'}).attrs['href'].strip())})
        return result


class Issue:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = kwargs['id']
        self.cover_url = kwargs['cover_url']
        self.title = kwargs['title']
        self.url = kwargs['url']
        singleton = Psyfar()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()

    @property
    def description(self):
        return self._fetch['description']

    @property
    def lang(self):
        return self._fetch['lang']

    @property
    def cover(self):
        return self._fetch_cover(self.cover_url)

    @property
    def css_url(self):
        return self._fetch['css_url']

    @property
    def css(self):
        return self._fetch_css(self.css_url)

    @property
    def contents(self):
        return self._fetch['contents']

    @property
    def articles(self):
        return [Article(**kwargs) for kwargs in self._get_articles(self.contents)]

    @cached_property
    def _fetch(self):
        if self._verbose:
            print("Fetching contents...")
        response = self._session.get(self.url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        css = soup.find('link', {'rel': 'stylesheet', 'media': 'screen', 'type': 'text/css'}).attrs['href']
        # Remove query from url (part after ?)
        css_path = urllib.parse.urlsplit(css)._replace(query='').geturl()
        return {'title': soup.find('meta', {'property': 'og:title'}).attrs['content'],
                'description': soup.find('meta', {'property': 'og:description'}).attrs['content'],
                # EPUB expects a language element with a value conforming to BCP 47 (https://www.rfc-editor.org/info/bcp47)
                'lang': soup.find('meta', {'property': 'og:locale'}).attrs['content'].replace("_", "-"),
                'css_url': urllib.parse.urljoin(self._base_url, css_path),
                'contents': soup.find('div', {'class': 'editie'})}

    def _fetch_cover(self, url):
        if self._verbose:
            print(f'Fetching cover {url}...')
        cover_url = urllib.parse.urljoin(self._base_url, url)
        try:
            response = self._session.get(cover_url)
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

    def _fetch_css(self, url):
        if self._verbose:
            print(f"Fetching CSS {url}...")
        try:
            response = self._session.get(url)
            response.raise_for_status()
        except urllib.error.HTTPError as e:
            print(e)
        else:
            return response.text

    def _get_articles(self, soup):
        result = []
        for article in soup.find_all('article'):
                title = article.find('h2', {'class': 'teaser__title'}).get_text('. ', strip=True)
                source = article.find('h2', {'class': 'teaser__title'}).find('a', {'class': 'teaser__title-link'}).attrs['href']
                url = urllib.parse.urljoin(self._base_url, source)
                metadata = article.find('div', {'class': 'teaser__metadata'}).find_all('li', {'class': 'teaser__metadata-list-item'})
                date = metadata[0].get_text().strip()
                section = metadata[1].a.get_text().strip()
                result.append({'title': title, 'url': url, 'date': date, 'section': section})
        return result

    @cached_property
    def epub(self):
        if self._verbose:
            print(f"Creating EPUB {self.title}...")

        ebook = epub.EpubBook()

        # Generate a UUID using a SHA-1 hash of a namespace UUID and URL and prepend a 'u',
        # because per the XML specification for ids, xml:ids should not start with a number
        ebook.set_identifier('u'+str(uuid.uuid5(uuid.NAMESPACE_URL, self.url)))
        ebook.set_title(self.title)
        # The language element specifies the language of the content. This value is not inherited by the individual resources.
        ebook.set_language(self.lang)
        ebook.add_author('Psyfar')
        ebook.add_metadata('DC', 'description', self.description)

        # Add cover
        ebook.set_cover('cover.jpg', self.cover)

        # Add chapters, table of contents, and spine
        ebook.toc = []
        ebook.spine = ['cover', 'nav']
        article_uids = []
        image_uids = []

        for article in self.articles:
            if article.uid not in article_uids:
                if self._verbose:
                    print(f"Adding article {article.title}...")
                article_uids.append(article.uid)
                chapter = epub.EpubHtml(uid=article.uid,
                                        title=article.title,
                                        file_name=article.filename,
                                        lang=article.lang,
                                        content=article.contents.prettify())
                ebook.add_item(chapter)
                ebook.spine.append(chapter)

                for image in article.images:
                    if image.uid not in image_uids and image.mimetype:
                        if self._verbose:
                            print(f"Adding image {image.url}...")
                        image_uids.append(image.uid)
                        epub_image = epub.EpubImage()
                        epub_image.id = image.uid
                        epub_image.file_name = image.filename
                        epub_image.media_type = image.mimetype
                        epub_image.content = image.contents
                        ebook.add_item(epub_image)

                ebook.toc.append(chapter)

        # Add stylesheet
        if self._verbose:
            print("Adding stylesheet...")
        ebook.add_item(epub.EpubItem(uid='u'+str(uuid.uuid5(uuid.NAMESPACE_URL, self.css_url)),
                                     file_name='style/styles.css',
                                     media_type='text/css',
                                     content=self.css))

        # Add NCX and Navigation tile
        ebook.add_item(epub.EpubNcx())
        ebook.add_item(epub.EpubNav())

        return ebook


class Article:
    def __init__(self, **kwargs):
        singleton = Psyfar()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = 'https://elearning.psyfar.nl/'
        self.title = kwargs['title']
        self.url = kwargs['url']
        self.date = kwargs['date']
        self.section = kwargs['section']
        self._blacklist = [('div', {'class': 'action-bar'}),
                           ('img', {'class': 'artikel__afbeeldingUitgelicht-background'})]

    @property
    def uid(self):
        return 'u'+str(uuid.uuid5(uuid.NAMESPACE_URL, self.url))

    @property
    def filename(self):
        basename = os.path.basename(self.url)
        splitext = os.path.splitext(basename)
        filename = splitext[0] + ".xhtml"
        return filename

    @property
    def lang(self):
        return self._fetch['lang']

    @property
    def _raw_contents(self):
        return self._fetch['contents']

    @property
    def _clean_contents(self):
        soup = copy.copy(self._raw_contents)
        for func in [self._remove_blacklist, self._remove_reactions]:
            func(soup)
        return soup

    @property
    def contents(self):
        soup = copy.copy(self._clean_contents)
        for func in [self._image_urls]:
            func(soup)
        return soup

    @property
    def images(self):
        return [Image(**kwargs) for kwargs in self._get_images(self._clean_contents)]

    @cached_property
    def _fetch(self):
        if self._verbose:
            print(f"Fetching article {self.url}...")
        response = self._session.get(self.url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        header = soup.find('div', {'class': 'artikelHeader'})
        article = soup.find('div', {'class': 'artikel'})
        contents = bs4.BeautifulSoup()
        contents.extend([header, article])
        return {'title': soup.find('meta', {'property': 'og:title'}).attrs['content'],
                'type': soup.find('meta', {'property': 'og:type'}).attrs['content'],
                'image': soup.find('meta', {'property': 'og:image'}).attrs['content'],
                'description': soup.find('meta', {'property': 'og:description'}).attrs['content'],
                'keywords': soup.find('meta', {'name': 'keywords'}).attrs['content'].split(", "),
                'lang': soup.find('meta', {'property': 'og:locale'}).attrs['content'].replace("_", "-"),
                'published_time': soup.find('meta', {'property': 'article:published_time'}).attrs['content'],
                'modified_time': soup.find('meta', {'property': 'article:modified_time'}).attrs['content'],
                'contents': contents}

    def _get_image_filename(self, url):
        basename = os.path.basename(url)
        unhexified_basename = urllib.parse.unquote(basename)
        filename = "images/" + unhexified_basename.replace(" ", "_")
        return filename

    def _get_images(self, soup):
        result = []
        for img in soup.find_all('img', {'src': True}):
            source = img['src']
            try:
                # fix bug where the data URLs are prefixed with 'https://elearning.psyfar.nl/'
                data_url = source.replace('https://elearning.psyfar.nl/', '')
                w3lib.url.parse_data_uri(data_url)
            except ValueError:
                # fix bug where URLs are escaped
                decoded_source = html.unescape(source)
                query = urllib.parse.urlsplit(decoded_source).query
                if query:
                    src = urllib.parse.parse_qs(query).get('src')
                    if src:
                        url = urllib.parse.urljoin(self._base_url, src[0])
                    else:
                        url = urllib.parse.urlsplit(decoded_source)._replace(query='').geturl()
                else:
                    url = source
                filename = self._get_image_filename(url)
                title = img.get('alt', '')
                result.append({'url': url, 'filename': filename, 'title': title})
        return result

    def _remove_blacklist(self, soup):
        for (name, attrs) in self._blacklist:
            for tag in soup.find_all(name, attrs):
                tag.decompose()
        return soup

    def _remove_reactions(self, soup):
        tag = soup.find('a', {'href': '#reacties'})
        if tag:
            for parent in tag.parents:
                if parent.name == 'li':
                    parent.decompose()
                    break
        return soup

    def _image_urls(self, soup):
        for img in soup.find_all('img', {'src': True}):
            source = img['src']
            try:
                data_url = source.replace('https://elearning.psyfar.nl/', '')
                w3lib.url.parse_data_uri(data_url)
                img['src'] = data_url
            except ValueError:
                # fix bug where URLs are escaped
                # url = html.unescape(source)
                decoded_source = html.unescape(source)
                query = urllib.parse.urlsplit(decoded_source).query
                if query:
                    src = urllib.parse.parse_qs(query).get('src')
                    if src:
                        url = urllib.parse.urljoin(self._base_url, src[0])
                    else:
                        url = urllib.parse.urlsplit(decoded_source)._replace(query='').geturl()
                else:
                    url = source
                img['src'] = self._get_image_filename(url)
        return soup


class Image:
    def __init__(self, **kwargs):
        # singleton instance
        singleton = Psyfar()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self.url = kwargs['url']
        self.filename = kwargs['filename']
        self.title = kwargs['title']

    @property
    def _basename(self):
        return os.path.basename(self.url)

    @property
    def uid(self):
        return 'u'+str(uuid.uuid5(uuid.NAMESPACE_URL, self.url))

    @property
    def mimetype(self):
        return mimetypes.guess_type(self._basename)[0]

    @cached_property
    def contents(self):
        if self._verbose:
            print(f"Fetching image {self.url}...")
        try:
            response = self._session.get(self.url)
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
                        nargs="*",
                        action=IssueAction)
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

    dirs = appdirs.AppDirs('psyfar-downloader', 'Folkert van der Beek')
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
    P = Psyfar()

    if settings.get('verbose'):
        P.set_verbose(True)

    if username and password:
        P.login(username, password)

    issues = []

    years = settings.get('year')
    if years:
        for year in years:
            issues.extend(Archive(year).issues)

    ids = settings.get('id')
    if ids:
        for id in ids:
            issues.append(Archive(id['year']).issues[id['issue']])

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
            filename = issue.id + ' Psyfar ' + issue.title + '.epub'
            path = os.path.join(download_dir, sanitize(filename))
            if not os.path.exists(path):
                epub.write_epub(path, issue.epub)
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
                epub.write_epub(path, issue.epub)
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
                    epub.write_epub(path, issue.epub)
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
