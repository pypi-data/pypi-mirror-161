from urllib.parse import urljoin, quote
from mkdocs.plugins import BasePlugin

class Plugin(BasePlugin):
    def on_pre_page(self, page, config, files, **kwargs):
        self._set_edit_url(page, config.get('repo_url', None))
        return page
        
    def _set_edit_url(self, page, repo_url):
        if repo_url:
            src_path = page.file.src_path.replace('\\', '_').replace('/', '_')
            src_path = src_path.replace('.md', '')
            src_path = quote(src_path)
            # Ensure urljoin behavior is correct
            if not repo_url.endswith('/'):
                repo_url += '/'
            page.edit_url = urljoin(repo_url, src_path + '/_edit')
        else:
            page.edit_url = None