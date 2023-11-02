FROM python:3.11.5-alpine
COPY . ./
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -r ./requirements.txt
EXPOSE 8084
CMD ["python", "./telegram_bot.py"]