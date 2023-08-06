from distutils.core import setup
setup(
  name = 'mildtrix-dlms',         # How you named your package folder (MyLib)
  package_dir={'mildtrix_dlms': 'mildtrix_dlms'},
  packages = ['mildtrix_dlms','mildtrix_dlms.enums','mildtrix_dlms.internal',
  'mildtrix_dlms.manufacturersettings','mildtrix_dlms.objects','mildtrix_dlms.plc','mildtrix_dlms.secure',
  'mildtrix_dlms.objects.enums','mildtrix_dlms.plc.enums',],   # Chose the same as "name"
  package_data={'mildtrix_dlms': ['OBISCodes.txt', 'India.txt', 'Italy.txt', 'SaudiArabia.txt', 'Spain.txt']},
  include_package_data=True,
  version = '0.17',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Mildtrix library for smartmeter',   # Give a short description about your library
  author = 'Ravi Chandra',                   # Type in your name
  author_email = 'ravichandra178@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/ravichandra99',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/ravichandra99/mildtrix-dlms/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['mildtrix', 'dlms', 'smartmeter'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.7',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)