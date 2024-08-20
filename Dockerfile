# May 31, 2023 - Odoo v16 official docker image > https://github.com/docker-library/repo-info/blob/04265b18740b2e7398001c645114cc9cfd98a51d/repos/odoo/remote/16.0.md
# Versions history: https://github.com/docker-library/repo-info/commits/master/repos/odoo
FROM odoo@sha256:6d2ce40a3f1c0f97ec87a3ce863b54cf161bd7a35133606f70da3271aaa43e94

USER root

# Install scripts to handle manifest
RUN apt-get -qqy update && apt-get install --no-install-recommends -qqy jq locales \
  && rm -rf /var/lib/apt/lists/*

# Set the locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# -- Install Poetry
ENV POETRY_VERSION=1.3.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

# -- Install python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false --local
RUN poetry install -v --without=dev-dependencies\
    && rm -rf /root/.cache \
    && find /usr/local/src/ -type d -name .git -exec rm -rf '{}' +
ENV PYTHONPATH=/usr/lib/python3.9/site-packages/

# -- Install Enterprise edition with authorized key found on keeper
ADD https://storage.googleapis.com/vr-debs/odoo_16.0+e.latest_all.2023-06-02.deb ./odoo_16.0+e.latest_all.deb
RUN dpkg -i odoo_16.0+e.latest_all.deb && rm ./odoo_16.0+e.latest_all.deb

ENV PYTHONPATH=/usr/lib/python3.9/site-packages/

# -- Install ShowHeroes related addons
USER odoo
ENV ADDONS_PATH=/usr/lib/python3/dist-packages/odoo/addons,/mnt/odoo16/acs_addons,/mnt/odoo16/custom_addons
COPY odoo16/acs_addons/ /mnt/odoo16/acs_addons
COPY odoo16/acs_addons/ /mnt/odoo16/custom_addons


