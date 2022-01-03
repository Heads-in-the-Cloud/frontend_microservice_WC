FROM python:3.6

EXPOSE ${FRONTEND_PORT}


WORKDIR /app
COPY . .

COPY requirements.txt /app
RUN pip install -r requirements.txt

# RUN ["chmod", "+x", "/app/entrypoint.sh"]
 
# ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD python app.py
