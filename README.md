# FOTO

I am creating this app to run on a raspberry pi so that my family can send pictures to my grandma more easily.

## Dev Usage

```bash
pipenv install
pipenv shell
python main.py
```

## Raspberry Pi Usage

1. Install the latest version of python 3, whatever it may be at the time.
   1. `apt install python3`
2. The following libraries need to be a version 2.0-0 or higher:
   1. `apt install libsdl2-mixer-2.0-0`
   2. `apt install libsdl2-image-2.0-0`
   3. `apt install libsdl2-2.0-0`
   4. `apt install libsdl2-ttf-2.0-0`
3. Install pygame > 2.0.0
   1. `python3 -m pip install pygame=2`
4. Install dependencies
   1. `pip install`
5. Run the app
   1. `python3 main.py`

## Config

Make sure you fill out the required fields in config. Alternatly, you can add a .env file that contains the following so you don't have to make changes to config (.env should be in .gitignore)

```properties
[EMAIL]
emailPassword = Password1!
emailHandle = mygreatemailhandle
```
