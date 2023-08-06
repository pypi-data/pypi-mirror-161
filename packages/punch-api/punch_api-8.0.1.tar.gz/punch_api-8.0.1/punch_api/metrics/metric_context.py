#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The punch prometheus context makes it easier to correctly name the metrics,
in particular the usage of the namespace and subsystem, and the
right use of labels.

Using the plain prometheus client API, each metric user must
go through a child metric to publish values with the right labels.

Besides, the punch API uses a light facade API which makes it
future-proof to accommodate other metric back ends.
"""

__author__ = "RT"

import prometheus_client

import punch_api.metrics.counter
import punch_api.metrics.gauge
import punch_api.metrics.histogram


class MetricContext:
    counters: dict[str, prometheus_client.Counter]
    gauges: dict[str, prometheus_client.Gauge]
    histograms: dict[str, prometheus_client.Histogram]
    __labels: dict[str, str]
    __subsystem: str
    __namespace: str

    def __init__(
        self,
        namespace: str | None,
        subsystem: str | None,
        labels: dict[str, str] = None,
    ) -> None:
        self.__subsystem = "" if subsystem is None else subsystem
        self.__namespace = "" if namespace is None else namespace
        self.__labels = {} if labels is None else labels

    def get_new_subsystem_context(self, subsystem: str) -> "MetricContext":
        """
        Derive a context from a parent to add some specific tags for a subsystem.
        :param subsystem: the subsystem, typically netty, kafka, elasticsearch
        :return: a new context instance
        """
        return MetricContext(self.__namespace, subsystem, self.__labels)

    def add_tag(self, key: str, value: str) -> None:
        """Update the tag if it exists, otherwise add it"""
        self.__labels[key] = value

    def __get_labels(self) -> list[str]:
        return list(self.__labels.keys())

    def __get_label_values(self) -> list[str]:
        return list(self.__labels.values())

    def start(self, port: int) -> "MetricContext":
        if 0 < port < 65536:
            prometheus_client.start_http_server(port)
        else:
            raise ValueError(
                f"Bad port value: got {port}, expected value between 1 and 65535."
            )

        return self

    def get_counter(
        self, name: str, doc: str, unit: str
    ) -> punch_api.metrics.counter.Counter:
        return punch_api.metrics.counter.Counter(
            self.__get_create_registered_counter(name, doc, unit),
            self.__get_label_values(),
        )

    def get_histogram(
        self, name: str, doc: str, unit: str
    ) -> punch_api.metrics.histogram.Histogram:
        return punch_api.metrics.histogram.Histogram(
            self.__get_create_registered_histogram(name, doc, unit),
            self.__get_label_values(),
        )

    def get_gauge(
        self, name: str, doc: str, unit: str
    ) -> punch_api.metrics.gauge.Gauge:
        return punch_api.metrics.gauge.Gauge(
            self.__get_create_registered_gauge(name, doc, unit),
            self.__get_label_values(),
        )

    def __get_create_registered_counter(
        self, name: str, doc: str, unit: str
    ) -> prometheus_client.Counter:
        key: str = self.__get_metric_name(name, unit)
        if key not in self.counters:
            self.counters[key] = prometheus_client.Counter(
                name=name,
                subsystem=self.__subsystem,
                namespace=self.__namespace,
                unit=unit,
                labelnames=self.__get_labels(),
                documentation=doc,
            )
        return self.counters[key]

    def __get_create_registered_gauge(
        self, name: str, doc: str, unit: str
    ) -> prometheus_client.Gauge:
        key: str = self.__get_metric_name(name, unit)
        if key not in self.gauges:
            self.gauges[key] = prometheus_client.Gauge(
                name=name,
                subsystem=self.__subsystem,
                namespace=self.__namespace,
                unit=unit,
                labelnames=self.__get_labels(),
                documentation=doc,
            )
        return self.gauges[key]

    def __get_create_registered_histogram(
        self, name: str, doc: str, unit: str
    ) -> prometheus_client.Histogram:
        key: str = self.__get_metric_name(name, unit)
        if key not in self.histograms:
            self.histograms[key] = prometheus_client.Histogram(
                name=name,
                subsystem=self.__subsystem,
                namespace=self.__namespace,
                unit=unit,
                labelnames=self.__get_labels(),
                documentation=doc,
            )
        return self.histograms[key]

    def __get_metric_name(self, name: str, unit: str) -> str:
        sb: str = self.__namespace
        if len(self.__subsystem) > 0:
            sb += "_" + self.__subsystem
        sb += "_" + name
        if len(unit) > 0:
            sb += "_" + unit
        return sb
