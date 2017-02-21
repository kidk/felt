FROM python:2.7

COPY . /felt/

RUN pip install -r /felt/requirements.txt

WORKDIR "/felt/"

RUN python main.py --init /srv

CMD ["python","main.py","--test","/srv"]
