from urllib.request import urlopen
import requests
from urllib.error import URLError
class Web:
    def hasSSL(url):
        """
        Checks if the url has SSL
        """
        try:
            if "str" in type(url):
                if "https://" in url:
                    requests.get(url)
                    return True
                elif "http://" in url:
                    return False
            else:
                return 'Invalid object type was passed to hasSSL'
        except requests.exceptions.MissingSchema:
            try:
                if not "https://" in url or not "http://" in url:
                    requests.get("https://" + url)
                    return True
            except requests.exceptions.MissingSchema:
                try:
                    if not "https://" in url or not "http://" in url:
                        requests.get("http://" + url)
                        return True
                except requests.exceptions.MissingSchema:
                    return 'Invalid URL was passed to hasSSL'
    def getHostDomain(url):
        """
        Gets the host domain of the URL.
        """
        try:
            if url.count('/') > 2:
                urlopen(url)
                return url.split('/')[2]
            elif url.count('/') == 2:
                urlopen(url)
                return 'URL entered is already the main domain.'   
            elif url.count('/') == 0:
                urlopen(url)
                return 'URL entered is already the main domain.'
            elif not "https://" in url or "http://" in url and url.count('/') == 1:
                urlopen(url)
                return 'URL entered is already the main domain.'
            else:
                return 'Invalid URL was passed to getHostDomain'
        except URLError:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            return url.split('/')[2]
        except ValueError:
            try:
                if not "https://" in url or not "http://" in url and url.count('/') == 0:
                    urlopen("https://" + url)
                    return 'URL entered is already the main domain.'
                elif not "https://" in url or not "http://" in url and not url.count('/') == 0:
                    urlopen("https://" + url)
                    return url.split('/')[2]
            except ValueError:
                return 'Invalid URL was passed to getHostDomain'
            except URLError:
                try:
                    import ssl
                    ssl._create_default_https_context = ssl._create_unverified_context
                    if not "https://" in url or not "http://" in url and not url.count('/') > 2:
                        urlopen("https://" + url)
                        return 'URL entered is already the main domain.'
                    elif url.count('/') > 2:
                        urlopen(url)
                        return url.split('/')[2]
                    elif url.count('/') == 2:
                        return 'URL entered is already the main domain.'
                    elif url.count('/') == 0:
                        return 'URL entered is already the main domain.'
                    elif "https://" in url or "http://" in url and url.count('/') > 2:
                        urlopen(url)
                        return url.split('/')[2]
                except ValueError:
                    return 'Invalid URL was passed to getHostDomain'
                    
    def getHTMLElements(url):
        """
        Gets the HTML elements of the URL.
        """
        try:
            return urlopen(url).read()
        except URLError:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            return urlopen(url).read()
        except ValueError:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            return urlopen('https://' + url).read()
        except:
            return 'An error occured while getting the HTML elements of the URL'