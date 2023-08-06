# Querier
**Querier** is a library for HTTP parameter (Query) parsing.<br>
Adding default values and a basic parser.<br>

# Installation
```sh
# Git + Pip
pip install git+https://github.com/ZSendokame/Querier

# Pip
pip install webQuerier
```

# Use
```py
from flask import Flask, request
import Querier

app = Flask(__name__)


@app.before_request
def before():
    global parser
    parser = Querier.Parser(request.url)  # URL To parse

    # Add "name" to default queries, with a default value.
    parser.add('name', default_value='ZSendokame')
    parser.parse()  # Parse.


@app.get('/')
def get():
    # Unparse URL, show original queries.
    parser.query_list['unparsed_url'] = Querier.unparse(parser.query_list)

    return parser.query_list # Return query: value.


app.run()


# url: http://127.0.0.1:5000/?name=Julio&surname=Iglesias
# {
#   "name": "Julio",
#   "surname": "Iglesias",
#   "unparsed_url": "?name=Julio&surname=Iglesias"
# }
```