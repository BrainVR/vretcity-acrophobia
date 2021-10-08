FROM python:3.8
RUN mkdir /app
WORKDIR /app
COPY pyproject.toml .
COPY app.py .
ADD nudz_vretcity_acrophobia/*.py nudz_vretcity_acrophobia/
ADD example-data ./example-data
ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8501
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]