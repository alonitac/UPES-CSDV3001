from setuptools import setup, find_packages

setup_args = dict(
    name='fantastic_auth',
    version='1.1.0',
    description='Fantastic Auth',
    license='MIT',
    install_requires=[
        'PyJWT',
        'bcrypt; python_version == "4.0.1"',
    ],
    author='Matt',
    author_email='example@example.com'
)


if __name__ == '__main__':
    setup(**setup_args)
