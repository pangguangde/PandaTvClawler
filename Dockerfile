FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.doubanio.com/simple --trusted-host pypi.doubanio.com

COPY . .

CMD ["python", "WebService.py"]