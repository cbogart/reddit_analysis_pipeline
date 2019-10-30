FROM adoptopenjdk/maven-openjdk8

# Install maven
RUN apt-get update
RUN apt-get install -y netcat git python

WORKDIR /pipeline
RUN git clone https://github.com/discoursedb/discoursedb-core.git discoursedb
WORKDIR /pipeline/discoursedb
COPY docker ./docker

RUN mvn clean
RUN mvn install
RUN mvn dependency:copy-dependencies
WORKDIR /pipeline/discoursedb/discoursedb-api-rest
RUN cp /pipeline/discoursedb/docker/discoursedb/custom.properties.user.management /pipeline/custom.properties.temp
RUN mv /pipeline/discoursedb/docker/discoursedb/custom.properties.user.management /pipeline/discoursedb/user-management/target/classes/custom.properties
RUN find .. -name custom.properties -exec cp ../custom.properties.temp {} \;
RUN mvn install
RUN mvn dependency:copy-dependencies
RUN mv /pipeline/discoursedb/docker/discoursedb/custom.properties.docker target/classes/custom.properties
RUN mv /pipeline/discoursedb/docker/discoursedb/localhost_keystore.p12 /pipeline/discoursedb/discoursedb-api-rest/src/main/resources/localhost_keystore.p12
RUN mv /pipeline/discoursedb/docker/discoursedb/wait-for .
WORKDIR /pipeline/discoursedb/user-management
RUN mvn install
RUN mvn dependency:copy-dependencies
WORKDIR /pipeline/discoursedb/discoursedb-api-rest
RUN chmod 777 wait-for

RUN mkdir /bratdata /lightdata

RUN groupadd -r bratuser
RUN useradd -g bratuser -ms /bin/bash bratuser
RUN chown -R bratuser:bratuser /bratdata
RUN chown -R bratuser:bratuser /lightdata

VOLUME /bratdata

EXPOSE 5280

USER bratuser
CMD ["sh","-c","while ! nc -z discoursedb_mysql 3306; do echo sleeping; sleep 1; done; echo Ready to Start `pwd`; java -cp  discoursedb-api-rest-0.9-SNAPSHOT.jar:target/classes:target/dependency/* edu.cmu.cs.lti.discoursedb.api.DiscourseApiStarter"]
