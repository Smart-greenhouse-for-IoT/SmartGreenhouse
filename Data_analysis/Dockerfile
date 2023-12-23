FROM python:3.11.5-slim
COPY . ./
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONUNBUFFERED=1
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
EXPOSE 8090
CMD ["python", "./data_analysis.py"]