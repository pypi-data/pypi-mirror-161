<p align="center">
    <a href="https://github.com/tegram/tegram">
        <img src="https://docs.tegram.org/_static/tegram.png" alt="tegram" width="128">
    </a>
    <br>
    <b>Telegram MTProto API Framework for Python</b>
    <br>
    <a href="https://tegram.org">
        Homepage
    </a>
    •
    <a href="https://docs.tegram.org">
        Documentation
    </a>
    •
    <a href="https://docs.tegram.org/releases">
        Releases
    </a>
    •
    <a href="https://t.me/tegram">
        News
    </a>
</p>

## tegram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from tegram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from tegram!")


app.run()
```

**tegram** is a modern, elegant and asynchronous [MTProto API](https://docs.tegram.org/topics/mtproto-vs-botapi)
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Installing

``` bash
pip3 install tegram
```

###----------------- Abdo Asil -------------------

```Tegram developer : Abdo Asil
Telegram : @ttccss
Facebook : https://www.facebook.com/AElasil
phone : +201025657503
Email :   almlmana20@gmail.com
