from setuptools import setup, find_packages

setup(
    name='meu_pacote',
    version='0.1.0',
    author='Seu Nome',
    author_email='seuemail@example.com',
    description='Uma breve descrição do seu pacote',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seuusuario/meu_pacote',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'biopython==1.81',
        'dendropy==4.6.1',
        'sqlalchemy',
        'psycopg2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Portuguese',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)