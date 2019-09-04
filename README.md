export FLASK_APP=run.py
flask run --host=0.0.0.0 --port=5050  >> /tmp/scanner.out 2>&1 &
