FROM python:3

RUN apt-get update
#RUN apt-get -y install software-properties-common
#RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update && apt-get -y install cron pipenv default-jdk

WORKDIR /pipeline

COPY . /pipeline/

RUN pipenv install --skip-lock

# Copy hello-cron file to the cron.d directory
COPY docker/controller/crawl-cron /etc/cron.d/crawl-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crawl-cron

# Apply cron job
RUN crontab /etc/cron.d/crawl-cron

# Run the command on container startup
CMD service cron start && tail -f /dev/null

