FROM python:3

WORKDIR /usr/src/app

# Install application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "8080"]

