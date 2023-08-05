from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name='django_app_novadata',
    version='0.1.1',
    url='https://github.com/TimeNovaData/django_novadata.git',
    license='MIT License',
    author='Emanuel Morais',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='emanuelbruno2018vasc@gmail.com',
    keywords='Pacote',
    description=u'Esta primeira versão traz um pacote que será utilizado para padronizar projetos distintos sem ser necessário modicação no código',
    packages=find_packages(),
    include_package_data=True,
    project_urls = {
        'Código fonte': 'https://github.com/TimeNovaData/django_novadata',
        'Download': 'https://github.com/TimeNovaData/django_novadata.git'
    }
)