FROM library/python:3 as python-base

COPY . /felt/
WORKDIR "/felt/"
RUN python setup.py bdist_egg

FROM python:3

COPY --from=python-base /felt/dist/felt-1.0.0-py3.6.egg /

RUN easy_install /felt-1.0.0-py3.6.egg

RUN felt --init /srv

ENV PYTHONUNBUFFERED 0

ENTRYPOINT ["felt"]

CMD ["--verbose", "/srv"]
