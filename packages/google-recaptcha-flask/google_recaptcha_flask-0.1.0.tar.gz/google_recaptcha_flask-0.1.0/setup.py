from setuptools import setup

with open("README.md", "r", encoding="utf8") as fh:
    readme = fh.read()

setup(
    name='google_recaptcha_flask',
    version='0.1.0',
    url='https://github.com/brunolimasp/Flask-Google-reCaptcha',
    license='MIT License',
    author='Bruno Augusto',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='augusto.han@gmail.com',
    keywords=['flask', 'recaptcha', "google"],
    description=u'Exemplo de pacote PyPI',
    py_modules=['google_recaptcha_flask'],
    include_package_data=True,
    install_requires=['requests', 'MarkupSafe'],
    )