FROM python:3.9.7
ADD . /python-flask
WORKDIR /python-flask
RUN pip install -r requirements.txt
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0" ]