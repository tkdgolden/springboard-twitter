python3 -m venv
source venv/bin/activate
pip install -r requirements.txt
createdb warbler
python seed.py
flask run

sudo service postgresql start
createdb warbler-test
FLASK_ENV=production python -m unittest