# FOTO

I am creating this app to run on a raspberry pi so that my family can send pictures to my grandma more easily during the pandemic.

![foto_gh](https://user-images.githubusercontent.com/5615792/111934373-a5208a00-8a97-11eb-8e40-a7b229224431.gif)

## Dev Usage

```bash
pipenv install
pipenv shell
python main.py
```

## Raspberry Pi Usage

### Basic Setup

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

### Start on Boot

If that works, we can set it up so it runs on boot using a service.

1. Create a system service
   1. `sudo systemctl edit --force --full foto.service`
2. Insert the following:

I have no idea what portion in [Unit] actually works as it seems this is an ongoing issue for people trying to run scripts after the network is connected.  What I do know works is the ExecStartPre in the [Service] section. Feel free to put up an MR if you can figure it out.

#### **`foto.service`**
```bash
[Unit]
Description=Foto by iamstevedavis
Wants=network.target network-online.target
After=network.target network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/git/foto
ExecStartPre=/din/sh -c 'until ping -c1 google.com; dosleep 1; done;'
ExecStart=python3 /home/pi/git/foto/main.py

[Install]
WantedBy=multi-user.target
```

3. Enable the service
   1. `sudo systemctl enable foto.service`

At this point you can reboot and see if the service starts.
If you need to edit:

- `sudo systemctl edit --full foto.service`

If you want to debug (check if the network is properly connecting):

- `sudo systemctl status foto.service`

### Additional Reading on Service Setup

Here are a few links on the topic covering the issue I mentioned above:

[Improved (=reliable) Wait for Network implementation](https://www.raspberrypi.org/forums/viewtopic.php?t=187225)

[systemd: start service at boot time after network is really up](https://stackoverflow.com/questions/35805354/systemd-start-service-at-boot-time-after-network-is-really-up-for-wol-purpose/57469241#57469241)

[launch program after network up with Stretch](https://raspberrypi.stackexchange.com/questions/100666/launch-program-after-network-up-with-stretch)

[Cause a script to execute after networking has started?](https://unix.stackexchange.com/questions/126009/cause-a-script-to-execute-after-networking-has-started)

[Running a script after an internet connection is established](https://raspberrypi.stackexchange.com/questions/78991/running-a-script-after-an-internet-connection-is-established/79033)

### Startup After Updating Repo

One additional thing I did was wrote a shell script to automatically pull the latest code on boot. I did not include this in the repo because it's specific to me, you can copy and modify it for your pi. If you do, change your ExecStart to point to the script.

#### **`startup.sh`**
```bash
#!/bin/bash

cd ~/git/foto
echo "Pull latest foto"
git pull origin master
echo "Got latest foto"
echo "Starting foto"
python3 /home/pi/git/foto/main.py
```

Then in your service:

`ExecStart=/bin/sh /home/pi/Desktop/foto.sh`

## Config

Make sure you fill out the required fields in config. Alternatly, you can add a .env file that contains the following so you don't have to make changes to config (.env should be in .gitignore)

```properties
[EMAIL]
emailPassword = Password1!
emailHandle = mygreatemailhandle
```
