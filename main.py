import sys

from timeline import timeline, run_insert

AUTH = {
    'consumer_key': 'Gg7eA8iADELAcZMBdyPONRT6S',
    'consumer_secret': 'gUC42t7oZKzapXfkw6jZeXqP4OLYm5KpgR9DrwElbR4XNG7fsA',
    'access_token': '260546258-Xc9X55LLe0HAk7rD3oJXH46MU4yWJF1xRwao1h5k',
    'access_token_secret': 'fYCEAG2RzWIzDaklHv9rgpTs0CNAXKvPA7xkpkw5XjoRe'
}

def main(scraper, term):
    scrapers = ['timeline']
    scraper = scraper.strip('--')

    if scraper not in scrapers:
        print 'ERROR: Invalid scraper. Please include a valid scraper.'
        sys.exit(1)

    if scraper == 'timeline':
        timeline(AUTH, term)

if __name__ == '__main__':
    scraper = sys.argv[1]
    term = sys.argv[2]
    main(scraper, term)
