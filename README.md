# Event site / Freevent
## Under Construction


> Example user table:
> |id|username       |email               |password|
> |--|--------       |-----               |--------|
> |0 |Ken Thompson   |ken@google.com      |p/q2-q4!|
> |1 |Dennis Ritchie |dmr@bell-labs.com   |dmac    | 
> |2 |Brian Kernighan|bwk@cs.princeton.edu|/.,/.,  |

## How to run
* At first, You should install [`Python`](https://www.python.org).
> If you are using `GNU/Linux`, You can install Python by something like:
> ```bash
> sudo apt install python        ## Debian, Ubuntu, ...
> sudo yum install python        ## CentOS, RHEL, Fedora, ...
> sudo dnf install python        ## Fedora
> sudo pacman -S python          ## Arch, Manjaro, ... 
> ``` 

1. create a virtual environment using `python -m virtualenv venv` and activate it using `source venv/bin/activate`.
1. run `pip install -r requirements.txt` command.
1. mv `config.py.sample` to `config.py`.
1. write your configs in `config.py`.
1. run `python -m flask run` command.
1. run `python -m flask init-db` command.
1. run `python -m flask run` command again.
1. this app is underestandble for dummies, send pull request!
1. Wait!! Where is Star?
1. You can go.

