import sys

from db import init
from timeline import timeline, run_insert

AUTH = {
    'consumer_key': 'Gg7eA8iADELAcZMBdyPONRT6S',
    'consumer_secret': 'gUC42t7oZKzapXfkw6jZeXqP4OLYm5KpgR9DrwElbR4XNG7fsA',
    'access_token': '260546258-Xc9X55LLe0HAk7rD3oJXH46MU4yWJF1xRwao1h5k',
    'access_token_secret': 'fYCEAG2RzWIzDaklHv9rgpTs0CNAXKvPA7xkpkw5XjoRe'
}

def main(method, term):
    methods = ['timeline', 'init']
    method = method.strip('--')

    if method not in methods:
        print 'ERROR: Invalid method. Please include a valid method.'
        sys.exit(1)

    if method == 'init':
        init()
    elif method == 'timeline':
        timeline(AUTH, term)

if __name__ == '__main__':
    method = sys.argv[1]
    term = sys.argv[2]
    main(method, term)
