from setuptools import setup, find_packages

setup(
    name="latina-store-bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "qrcode[pil]==7.4.2",
        "mercadopago>=2.0.0,<3.0.0",
        "flask==2.3.3",
    ],
)