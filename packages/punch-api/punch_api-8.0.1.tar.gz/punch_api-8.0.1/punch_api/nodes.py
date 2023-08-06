#!/usr/bin/env python
# -*- coding: utf-8 -*-

# License Agreement
# This code is licensed under the outer restricted Tiss license:
#
#  Copyright [2014]-[2019] Thales Services under the Thales Inner Source Software License
#  (Version 1.0, InnerPublic -OuterRestricted the "License");
#
#  You may not use this file except in compliance with the License.
#
#  The complete license agreement can be requested at contact@punchplatform.com.
#
#  Refer to the License for the specific language governing permissions and limitations
#  under the License.

from abc import abstractmethod

from punch_api.dag import Node
from punch_api.datasets import InputDatasets, OutputDatasets
from punch_api.logger import print_error


class Source(Node):
    def __init__(self):
        """
        Override Node's dataclass __init__
        Classic Node's attributes are set by NodeRunner, not by __init__
        """
        pass

    @abstractmethod
    def execute(self, output_datasets: OutputDatasets) -> None:
        """Execute the node

        :param output_datasets: an empty custom object that is used to publish data to the outs with output.put()
        :return: None
        """

        print_error("execute(self, output_datasets) must be override by your own node.")
        raise NotImplementedError("abstract method execute")


class Function(Node):
    @abstractmethod
    def execute(
        self, input_datasets: InputDatasets, output_datasets: OutputDatasets
    ) -> None:
        """
        Execute the node

        :param input_datasets: a custom object containing the data from the connected input out
        :param output_datasets: an empty custom object that is used to publish data to the output outs with output.put()
        :return: None
        """

        print_error(
            "execute(self, input_datasets, output_datasets) must be override by your own node."
        )
        raise NotImplementedError("abstract method execute")
