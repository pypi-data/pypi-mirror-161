# IGWN Alert System (igwn-alert)
The IGWN Alert System (`igwn-alert`) is a prototype notification service built on Apache Kafka, using the 
publish-subscribe (pubsub) protocol. It is a higher-level modification of SCIMMA's 
[hop-client](https://hop-client.readthedocs.io/) to streamline receiving and 
responding to alerts from GraceDB.

This package replaces the legacy LIGO `LVAlert` XMPP-based alert system. 
