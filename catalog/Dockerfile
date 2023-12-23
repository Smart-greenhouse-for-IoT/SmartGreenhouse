FROM python:3.11.5-slim
COPY . ./
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -r ./requirements.txt
EXPOSE 8081
CMD ["python", "./catalog.py"]