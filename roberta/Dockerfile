FROM python:3.10.12-slim-bullseye
WORKDIR /app
RUN pip install --upgrade pip
RUN apt update && apt install git -y
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN  curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && apt-get install git-lfs

COPY . .

RUN git clone https://huggingface.co/SamLowe/roberta-base-go_emotions

CMD ["python3", "app.py"]
