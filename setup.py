from setuptools import setup

setup(name='porthole',
      version='0.6.2',
      description='An automated reporting package.',
      author='Billy McMonagle',
      author_email='speedyturkey@gmail.com',
      url='https://github.com/speedyturkey/porthole',
      packages=['porthole'],
      python_requires='>3.6',
      install_requires=[
                        'pymysql',
                        'psycopg2',
                        'xlsxwriter',
                        'SQLAlchemy'
                    ],
      zip_safe=False)
