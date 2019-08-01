from setuptools import setup

setup(
    name='porthole',
    version='0.8.1',
    description='An automated reporting package.',
    author='Billy McMonagle',
    author_email='speedyturkey@gmail.com',
    url='https://github.com/speedyturkey/porthole',
    packages=['porthole'],
    python_requires='>3.6',
    install_requires=[
        'openpyxl',
        'psycopg2-binary',
        'pymysql',
        'pytz',
        'SQLAlchemy',
        'xlsxwriter',
    ],
    extras_require={
        'AWS': ["boto3"]
    },
    zip_safe=False
)
