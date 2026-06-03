FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN useradd -m -u 1000 user && chown -R user /app
USER user

EXPOSE 7860

CMD ["python", "-m", "streamlit", "run", "frontend/app.py", "--server.port=7860", "--server.address=0.0.0.0"]