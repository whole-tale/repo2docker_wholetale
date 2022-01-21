import sys

if sys.version_info >= (3, 8):
    cookie_options = {"SameSite": None, "Secure": True}
    c.NotebookApp.tornado_settings = {"xsrf_cookie_kwargs": cookie_options}
    c.NotebookApp.cookie_options = cookie_options
