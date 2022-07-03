FROM cern/cc7-base
RUN 	yum -y update
RUN		yum -y install python-pip
RUN		yum -y install python3
RUN 	pip3 install --upgrade pip
RUN		yum -y install which
COPY 	./required_packages.txt .
RUN pip3 install -r required_packages.txt
RUN echo 'alias python="/usr/bin/python3"' >> ~/.bashrc
RUN useradd -m docker && \
    cp /root/.bashrc /home/docker/ && \
    mkdir /home/docker/pythium && \
    chown -R --from=root docker /home/docker
WORKDIR /home/docker/pythium
run mkdir src src/pythium scripts configs
ADD ./src/pythium/ ./src/pythium/
ADD ./scripts/ ./scripts/
ADD ./misc/*.py ./misc/*.png ./misc/
USER docker