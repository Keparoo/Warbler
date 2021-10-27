echo 'environment: test'
export ENV=test

echo 'begin testing'
python -m unittest -v test_user_model.py
python -m unittest -v test_message_model.py
python -m unittest -v test_user_views.py
python -m unittest -v test_message_views.py