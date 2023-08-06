from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='apti',
    version='0.0.3',
    decription='This will help you make robots',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Mikko Shogren',
    author_email='mikkocoding@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['robot', 'window'],
    packages=find_packages(),
    install_requires=['pyautogui', 'opencv-python', 'pywhatkit', 'pynput', 'speechrecognition', 'keyboard', 'pyttsx3', 'googletrans', 'sklearn','pandas']
)