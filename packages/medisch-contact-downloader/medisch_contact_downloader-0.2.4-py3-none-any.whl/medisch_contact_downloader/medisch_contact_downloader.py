__version__ = '0.2.4'

import appdirs
import argparse
import base36
import bs4
import configparser
import copy
from datetime import datetime
from ebooklib import epub
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
import hashlib
import mimetypes
import os
import random
import re
import requests
from sanitize_filename import sanitize
import smtplib
from tabulate import tabulate
import tempfile
import threading
import urllib
import uuid


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


class _MedischContact(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Double-checked locking pattern
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(_MedischContact, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MedischContact(metaclass=_MedischContact):
    def __init__(self):
        self._verbose = False
        self._session = requests.Session()
        self._base_url = 'https://www.medischcontact.nl'
        self._login_url = get_absolute_url(self._base_url, '/inloggen.htm')
        self._servlet_url = get_absolute_url(self._base_url, '/web/wcbservlet/nl.gx.forms.wmpformengine.servlet')
        self._orgurl = get_absolute_url(self._base_url, '/home.htm')

    def get_verbose(self):
        return self._verbose

    def set_verbose(self, verbose=True):
        self._verbose = verbose

    def get_session(self):
        return self._session

    def get_base_url(self):
        return self._base_url

    def get_csrf_token(self):
        """Return an anti-CSRF token. The token is a SHA-256 hash of the value of the
        X-CSRF-Token cookie and a nonce, postfixed with the used nonce. The
        implementation was taken from
        "https://www.medischcontact.nl/web/js/form/csrfprotection.js"

        """
        token = self._session.cookies.get('X-CSRF-Token', '')
        timestamp_float = datetime.now().timestamp()
        timestamp_int = int(timestamp_float * 1000)
        timestamp_base36 = base36.dumps(timestamp_int)
        random_float = random.random()
        random_int = int(random_float * pow(10, 16))
        random_base36 = base36.dumps(random_int)
        nonce = (timestamp_base36[2:] + random_base36[:10]).ljust(10, '0')
        token = hashlib.sha256((token + nonce).encode('ascii')).hexdigest() + nonce
        return token

    def login(self, username, password):
        if self._verbose:
            print("Going to login page...")
        response = self._session.get(self._login_url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        form = soup.find('form', {'class': 'wmpform'})
        params = {'precondition_show': form.find('input', {'name': 'precondition_show'}).attrs['value'],
                  'precondition_hide': form.find('input', {'name': 'precondition_hide'}).attrs['value'],
                  'formid': form.find('input', {'name': 'formid'}).attrs['value'],
                  'clientsideRouting': form.find('input', {'name': 'clientsideRouting'}).attrs['value'],
                  'wmformid': form.find('input', {'name': 'wmformid'}).attrs['value'],
                  'wmstepid': form.find('input', {'name': 'wmstepid'}).attrs['value'],
                  'wmlocale': form.find('input', {'name': 'wmlocale'}).attrs['value'],
                  'csfw': form.find('input', {'name': 'csfw'}).attrs['value'],
                  'csfw_versionId': form.find('input', {'name': 'csfw_versionId'}).attrs['value'],
                  'csfw_stepId': form.find('input', {'name': 'csfw_stepId'}).attrs['value'],
                  'csfw_requestedChannel': form.find('input', {'name': 'csfw_requestedChannel'}).attrs['value'],
                  'orgurl': self._orgurl,
                  'gebruikersnaam': username,
                  'wachtwoord': password,
                  'remember_me': form.find('input', {'name': 'remember_me'}).attrs['value'],
                  'csrftoken': self.get_csrf_token(),
                  }
        if self._verbose:
            print("Logging in...")
        response = self._session.post(self._servlet_url, data=params)
        if response.status_code != 200:
            raise Exception(f"Login failed for username {username} and password {password}")


class Archive:
    def __init__(self, year=None):
        singleton = MedischContact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self._archive_url = get_absolute_url(self._base_url, '/tijdschrift/medisch-contact-1945-heden.htm')
        self.year = year

    @cached_property
    def issues(self):
        return [Issue(**kwargs) for kwargs in self._fetch(self.year)]

    def _fetch(self, year):
        if self._verbose:
            print(f"Going to archive page {self._archive_url}...")
        response = self._session.get(self._archive_url, params={'year': year} if year else None)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        if year:
            year = str(year)
        else:
            year = soup.find('select', {'class': 'selectBox_select--archive', 'name': 'year'}).find('option', {'selected': 'true'}).attrs['value']
        archive_list = soup.find('ul', {'class': 'archive_list'})
        archive_items = archive_list.find_all('li', {'class': 'archive_item'})
        archive_items.reverse()
        result = []
        for idx, archive_item in enumerate(archive_items):
            result.append({'id': year + "-" + str(idx+1),
                           'issue': archive_item.strong.get_text(),
                           'time': archive_item.time.get_text(),
                           'title': archive_item.img.attrs['alt'],
                           'url': get_absolute_url(self._base_url, archive_item.a.attrs['href'])})
        return result


class Issue:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = kwargs['id']
        self.issue = kwargs['issue']
        self.time = kwargs['time']
        self.title = kwargs['title']
        self.url = kwargs['url']
        singleton = MedischContact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()

    @property
    def date(self):
        return self._fetch['date']

    @property
    def pubdate(self):
        return self._fetch['pubdate']

    @property
    def description(self):
        return self._fetch['description']

    @property
    def lang(self):
        return self._fetch['lang']

    @property
    def cover_url(self):
        return self._fetch['cover_url']

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
    def sections(self):
        return [Section(**kwargs) for kwargs in self._get_sections(self.contents)]

    @cached_property
    def _fetch(self):
        if self._verbose:
            print("Fetching contents...")
        response = self._session.get(self.url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        image = soup.find('meta', {'property': 'og:image'}).attrs['content']
        css = soup.find('link', {'rel': 'stylesheet', 'type': 'text/css'}).attrs['href']
        # Remove query from url (part after ?)
        css_path = urllib.parse.urlsplit(css)._replace(query='').geturl()
        return {'date': soup.find('meta', {'name': 'date'}).attrs['content'],
                'pubdate': soup.find('meta', {'name': 'pubdate'}).attrs['content'],
                'title': soup.find('meta', {'property': 'og:title'}).attrs['content'],
                'description': soup.find('meta', {'property': 'og:description'}).attrs['content'],
                # EPUB expects a language element with a value conforming to BCP 47 (https://www.rfc-editor.org/info/bcp47)
                'lang': soup.find('meta', {'property': 'og:locale'}).attrs['content'].replace("_", "-"),
                'cover_url': get_absolute_url(self._base_url, image),
                'css_url': get_absolute_url(self._base_url, css_path),
                'contents': soup.article}

    def _fetch_cover(self, url):
        if self._verbose:
            print(f'Fetching cover {url}...')
        cover_url = get_absolute_url(self._base_url, url)
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

    def _get_sections(self, soup):
        result = []
        for section in soup.find_all(attrs={'class': 'linkList linkList--archive'}):
            try:
                title = section.find(attrs={'class': 'linkList_heading'}).get_text().strip()
            except AttributeError:
                pass
            else:
                result.append({'title': title, 'contents': section})
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
        ebook.add_author('Medisch Contact')
        ebook.add_metadata('DC', 'description', self.description)
        ebook.add_metadata('DC', 'date', self.pubdate)

        # Add cover
        ebook.set_cover('cover.jpg', self.cover)

        # Add chapters, table of contents, and spine
        ebook.toc = []
        ebook.spine = ['cover', 'nav']
        article_uids = []
        image_uids = []
        for section in self.sections:
            if self._verbose:
                print(f"Adding section {section.title}...")

            chapters = []

            for article in section.articles:
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
                    chapters.append(chapter)

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

            ebook.toc.append([epub.Section(section.title), chapters])

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


class Section:
    def __init__(self, **kwargs):
        singleton = MedischContact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self.title = kwargs['title']
        self.contents = kwargs['contents']

    @property
    def articles(self):
        return [Article(**kwargs) for kwargs in self._get_articles(self.contents)]

    def _get_articles(self, soup):
        result = []
        for article in soup.find_all(attrs={'class': 'linkList_item'}):
            try:
                title = article.find(attrs={'class': 'linkList_link'}).get_text().strip()
                url = article.find(attrs={'class': 'linkList_link'}).attrs['href']
            except AttributeError:
                pass
            else:
                result.append({'title': title, 'url': get_absolute_url(self._base_url, url)})
        return result


class Article:
    def __init__(self, **kwargs):
        singleton = MedischContact()
        self._verbose = singleton.get_verbose()
        self._session = singleton.get_session()
        self._base_url = singleton.get_base_url()
        self.title = kwargs['title']
        self.url = kwargs['url']
        self._blacklist = [('script', True),
                           (True, {'class': 'button button--tag'}),
                           (True, {'class': 'clear'}),
                           (True, {'class': 'comments'}),
                           (True, {'class': re.compile("^comments_item")}),
                           (True, {'class': 'commentsForm'}),
                           (True, {'class': 'embed-container'}),
                           (True, {'class': 'imgprinter print'}),
                           (True, {'class': 'mobileShare'}),
                           (True, {'class': 'reactions_comments'}),
                           (True, {'class': 'socialSharing'}),
                           (True, {'id': 'reacties'}),
                           (True, {'id': 'reactions'})]

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
        for func in [self._remove_blacklist, self._remove_comments, self._fix_datalazy, self._fix_datetime]:
            func(soup)
        return soup

    @property
    def contents(self):
        soup = copy.copy(self._clean_contents)
        for func in [self._absolute_urls, self._image_urls]:
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
        return {'title': soup.find('meta', {'property': 'og:title'}).attrs['content'],
                'lang': soup.find('meta', {'property': 'og:locale'}).attrs['content'].replace("_", "-"),
                'contents': soup.article}

    def _get_image_filename(self, url):
        basename = os.path.basename(url)
        unhexified_basename = urllib.parse.unquote(basename)
        filename = "images/" + unhexified_basename.replace(" ", "_")
        return filename

    def _get_images(self, soup):
        result = []
        for img in soup.find_all('img', {'src': True}):
            title = img.get('alt', '')
            url = get_absolute_url(self._base_url, img['src'])
            filename = self._get_image_filename(img['src'])
            result.append({'url': url, 'filename': filename, 'title': title})
        return result

    def _remove_blacklist(self, soup):
        for (name, attrs) in self._blacklist:
            for tag in soup.find_all(name, attrs):
                tag.decompose()
        return soup

    def _remove_comments(self, soup):
        for element in soup.find_all(text=lambda text: isinstance(text, bs4.Comment)):
            element.extract()
        return soup

    def _fix_datalazy(self, soup):
        for tag in soup.find_all('img', {'data-lazy': True}):
            src = tag.attrs['data-lazy']
            del tag['data-lazy']
            del tag['src']
            del tag['scr']  # Fix a recurrent typo in the attribute
            tag['src'] = src
        return soup

    def _fix_datetime(self, soup):
        for tag in soup.find_all(True, {'datetime': True}):
            time_data = tag.attrs['datetime']
            format_data = "%d/%m/%Y %H:%M"
            date = datetime.strptime(time_data, format_data)
            tag['datetime'] = date.isoformat()
        return soup

    def _absolute_urls(self, soup):
        for tag in soup.find_all(attrs={'href': True}):
            tag['href'] = get_absolute_url(self._base_url, tag['href'])
        return soup

    def _image_urls(self, soup):
        for img in soup.find_all('img', {'src': True}):
            img['src'] = self._get_image_filename(img['src'])
        return soup


class Image:
    def __init__(self, **kwargs):
        # singleton instance
        singleton = MedischContact()
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


def get_absolute_url(base_url, source):
    if re.findall("^https?://", source):
        url = source
    elif source.startswith("mailto:"):
        url = source
    elif source.startswith("whatsapp:"):
        url = source
    elif source.startswith("#"):
        url = source
    else:
        url = urllib.parse.urljoin(base_url, source)
    return url


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
                        help='Set the port of the SMTP server (for example "587").If omitted the OS default behavior will be used.')
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

    dirs = appdirs.AppDirs('medisch-contact-downloader', 'Folkert van der Beek')
    config_path = get_config_path(dirs, args.config)

    if config_path:
        config.read(config_path)
        settings = {}
        for section in config.sections():
            settings.update(dict(config[section]))
            settings.update({key: value for key, value in vars(args).items() if value is not None})
    else:
        settings = vars(args)

    print(settings)

    username = settings.get('username')
    password = settings.get('password')

    # singleton instance
    MC = MedischContact()

    if settings.get('verbose'):
        MC.set_verbose(True)

    if username and password:
        MC.login(username, password)

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
        headers = ['ID', 'Title', 'Date', 'URL']
        data = [[issue.id, issue.title, issue.time, issue.url] for issue in issues]
        print(tabulate(data, headers, tablefmt='plain'))

    if settings.get('email'):
        settings['download'] = True

    if settings.get('download'):
        download_dir = settings.get('download_dir') if settings.get('download_dir') else dirs.user_data_dir
        if settings.get('verbose'):
            print(f"Download directory is set to {download_dir}")
        if not os.path.exists(download_dir):
            if settings.get('verbose'):
                print(f"Creating directory {download_dir}...")
            os.mkdir(download_dir)

        # Select the latest issue if none is selected
        if len(issues) == 0:
            issues.append(Archive().issues[-1])

        for issue in issues:
            filename = issue.id + ' ' + issue.title + '.epub'
            path = os.path.join(download_dir, sanitize(filename))
            if not os.path.exists(path):
                if settings.get('verbose'):
                    print(f"Writing file {path}...")
                epub.write_epub(path, issue.epub)
                if settings.get('email'):
                    if settings.get('verbose'):
                        print(f"Sending file as e-mail attachment...")
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
                if settings.get('verbose'):
                    print(f"Writing file {path}...")
                epub.write_epub(path, issue.epub)
                if settings.get('email'):
                    if settings.get('verbose'):
                        print(f"Sending file as e-mail attachment...")
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
                if settings.get('verbose'):
                    print(f"{path} already exists, not overwriting.")
                pass
            else:
                overwrite = input(f"{path} already exists. Overwrite? ")
                if overwrite in ['y', 'Y', 'yes', 'Yes']:
                    epub.write_epub(path, issue.epub)
                    if settings.get('email'):
                        if settings.get('verbose'):
                            print(f"Sending file as e-mail attachment...")
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
