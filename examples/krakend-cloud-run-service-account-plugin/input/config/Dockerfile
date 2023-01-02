# Build KrakenD configuration file
FROM devopsfaith/krakend:2.1.3 as builder

COPY /config /etc/krakend/config

RUN FC_ENABLE=1 \
    FC_OUT=/tmp/krakend.json \
    FC_SETTINGS="config/settings" \
    FC_TEMPLATES="config/templates" \
    krakend check -t -d -c "config/krakend.json"

RUN krakend check -c /tmp/krakend.json --lint

# Add the built configuration file to the final Docker image
FROM devopsfaith/krakend:2.1.3

COPY /config/plugins /etc/krakend/config/plugins

COPY --from=builder --chown=krakend:root /tmp/krakend.json .
