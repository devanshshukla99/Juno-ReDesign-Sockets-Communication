# Juno: Sockets Communication

<p style='font-size:110%;'>Package for easy-straight-forward socket communication with 128-bit AES encryption.</p>

<h2>Getting Started</h2>

<h3> Installing the Dependencies </h3>

```python
pip install -r requirements.txt
```
<p style='font-size:110%;'>Dependency includes <strong>Chromos</strong>, install via git, <a href='https://www.github.com/devanshshukla99/Chromos'>Chromos</a></p>

<h3>RSA Keys</h3>

The program will auto generate RSA Keys for Server and Client.
For authentication, the user will have to copy the server's public key from ``SKeys`` to ``CKeys`` folder and name it ``public.key``.

<h3>Help</h3>

```python
python3 juno.py --help

usage: juno.py [-h] [--bind BIND_IP] [--port BIND_PORT] [--timeout TIMEOUT]
               [--username USERNAME] [--server]

Package for easy-straight-forward socket communication with 128-bit AES
encryption.

optional arguments:
  -h, --help            show this help message and exit
  --bind BIND_IP, -b BIND_IP
                        Bind IP
  --port BIND_PORT, -p BIND_PORT
                        Bind Port
  --timeout TIMEOUT, -t TIMEOUT
                        Timeout [30s]
  --username USERNAME, -u USERNAME
                        Username
  --server, -s          Initiate a server instance
```


<h3> Prompt Commands </h3>

```\start server```

```\start client```

```\who```

```\whoisthis```

```\connect```

<p style='color:#6A8ED2;font-size:120%;'>Etc, discover as you go!!</p>
