# arquivo necessário para armazenas as info necessárias para o pypi.org utilizar os pacotes

from setuptools import setup,find_packages
from pathlib import Path

setup(        
    name='pro_video_mj_teste',
    version=1.0,
    description='Este pacote irá fornecer ferramentas de processamentos de multimidia',
    long_description=Path('README.md').read_text(), #Lê o readme e tranfere para a home do pypi,
    author='Mauro Júnior',
    author_email='email@email.com',
    keywords=['camera','video','processamento'], #palavras relacionadas
    packages=find_packages() #quando a pessoa roda o pip install "nome do meu pacote" ele instala todas as dependência do package)
)