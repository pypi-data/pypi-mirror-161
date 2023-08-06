from setuptools import setup

#reading long description from file
#with open('DESCRIPTION.txt') as file:
#	long_description = file.read()

# specify requirements of your package here
REQUIREMENTS = ['selenium','webdriver-manager','pandas']
  
# some more details
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    'Topic :: Terminals',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    ]
  
# calling the setup function 
setup(name='search_buddy_mac',
      version='1.1.1',
      description='A tool to simplify initial literature searches',
      #long_description=long_description,
      url='https://github.com/soapGame34/lib-search-buddy',
      author='Alexander J. Calder',
      author_email='alexcalder91@gmail.com',
      license='MIT',
      entry_points = { 'console_scripts' : ['litsearch = search_buddy_mac.search_buddy_mac.command_line:main']},
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      keywords='research literature-search'
      )
