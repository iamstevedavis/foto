# FOTO

I am creating this app to run on a raspberry pi so that my family can send pictures to my grandma more easily.

## Usage

```bash
pipenv install
pipenv shell
python main.py
```

## Config

Make sure you fill out the required fields in config. Alternatly, you can add a .env file that contains the following so you don't have to make changes to config (.env should be in .gitignore)

```properties
[EMAIL]
emailPassword = Password1!
emailHandle = mygreatemailhandle
```
