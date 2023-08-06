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
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Column:
    """
    Column definition
    """

    name: str
    type: str | None = None
    default: Any | None = None


@dataclass
class Out:
    """
    Link Between nodes
    """

    id: str
    table: str = "default"
    columns: list[Column] = field(default_factory=list)

    def __post_init__(self):
        self.columns = [Column(**column) for column in self.columns]

    def __hash__(self):
        return hash((self.id, self.table))


@dataclass
class Node:
    """
    Generic node structure
    """

    id: str
    kind: str
    type: str
    settings: dict[str, Any] = field(default_factory=dict)
    out: list[Out] = field(default_factory=list)
    engine_settings: Any = None
    load_control: Any = None
    exit_conditions: Any = None

    def __post_init__(self):
        self.out: list[Out] = [Out(**out) for out in self.out]
