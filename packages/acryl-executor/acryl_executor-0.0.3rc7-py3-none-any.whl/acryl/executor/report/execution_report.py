# Copyright 2021 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pprint
import datetime 

from dataclasses import dataclass, field
from typing import List, Dict, Optional

def format_report_line(line_type: str, headers: List[str], message: str) -> str:
    utc_time = datetime.datetime.utcnow()
    header_str = ""
    for header in headers:
        header_str = header_str + f"[{header}]"
    return f"{utc_time} {header_str} {line_type}: {message}"

@dataclass
class Report:
    def as_obj(self) -> dict:
        return self.__dict__

    def as_string(self) -> str:
        return pprint.pformat(self.as_obj(), width=150)

    def as_json(self) -> str:
        return json.dumps(self.as_obj())

"""
Report object leveraged by an Executor coordinating Task Execution.
"""
@dataclass
class ExecutionReport(Report):

    exec_id: str

    infos: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    structured_report: Optional[str] = None

    def __init__(self, exec_id: str): 
        self.exec_id = exec_id
        self.infos = []
        self.errors = []

    def report_info(self, message: str) -> None:
        formatted_message = self._format_report_line("INFO", message)
        print(formatted_message) # TODO: Add flag for printing to STDOUT
        self.infos.append(formatted_message)

    def report_error(self, message: str) -> None:
        formatted_message = self._format_report_line("ERROR", message)
        print(formatted_message) # TODO: Add flag for printing to STDOUT
        self.errors.append(formatted_message)

    def set_structured_report(self, report_content: str) -> None:
        self.structured_report = report_content

    def _format_report_line(self, line_type: str, message: str) -> str:
        headers = [
            f"exec_id={self.exec_id}"
        ]
        return format_report_line(line_type, headers, message)