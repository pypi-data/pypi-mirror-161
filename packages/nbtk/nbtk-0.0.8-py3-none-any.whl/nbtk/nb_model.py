"""
The ``nbtk.nb_model`` module provides the definition of a "nebula model".
This module provides functions of setting/loading variables of a model

@author: Zhilin
@date: 21/12/10
@version: v0.1
"""

import logging
import yaml
import json


class Model(yaml.YAMLObject):
	yaml_tag = 'nebula_model'

	def __init__(
		self,
	    name,
		author=None,
	    version=None,
	    type=None,
	    field=None,
	    dependency_command=None,
	    train_req=None,
	    inference_req=None,
	    param_json=[{"formItem": [], "formData": {}, "intro": ""}],
	    metrics={},
	    summary=None,
	    keyword=None,
	    desc=None,
	    reference=None,
	    cite=None,
		output=None
	):
		self.name = name
		self.author = author
		self.version = version
		self.type = type
		self.field = field
		self.dependency_command = dependency_command
		self.train_req = train_req
		self.inference_req = inference_req
		self.param_json = param_json
		self.metrics = metrics
		self.summary = summary
		self.keyword = keyword
		self.desc = desc
		self.reference = reference
		self.cite = cite
		self.output = output

	def log_metric(self, metric, value):
		"""
		Record one metric in the model configuration file (model.yml).

		: param metric: Metric name to be displayed on the model evaluation interface.
		: param value: Exact value of the metric.
		"""
		if metric in self.metrics.keys():
			self.metrics[metric].append(value)
		else:
			self.metrics[metric] = [value]
		return self

	def def_param(
		self,
		name,
		value="",
		type="text",
		max=None,
		min=None,
		precision=None,
		relyBind=None,
		props=None,
		condition=None,
		display_name=None,
		message=None,
		rules=None
	):
		"""
		Define a model parameter, including its name, interaction type, description, default_value
		and value selection bounds. For pro developers, more interactions are provided, such as the rely relationship,
		the condition of hiding/showing the parameter, etc.

		: param name: parameter name(as a varaible name)
		: param value: Exact value of the metric.
		"""
		if display_name is None:
			display_name = name

		if props is None and max is not None and min is not None:
			if precision is None:
				precision = 0
			props = {"max":max, "min":min, "precision":precision}

		item = {"chineseName": display_name, "name": name, "type": type, "props": props, "message": message}

		if rules is not None:
			item["rules"] = rules

		if relyBind is not None:
			item["relyBind"] = relyBind

		#update formItem
		self.param_json[0]["formItem"].append(item)

		#update condition
		if condition is not None:
			if "condition" in self.param_json[0].keys():
				self.param_json[0]["condition"].append(condition)
			else:
				self.param_json[0]["condition"] = [condition]

		#update formData
		self.param_json[0]["formData"][name] = value
		return self

	def set_name(self, name):
		"""
		Set model name

		: param name: name to be set
		"""
		self.name = name
		return self

	def gen_config(self, file="my_model.yml"):
		"""
		Export the nb model object to a yaml configuration file

		: param file: "File_path" to dump the yaml-formatted model
		"""

		if self.desc:
			self.param_json[0]["intro"] = self.desc

		json_file_name = file.split(".yml")[0] + "_params.json"
		with open(json_file_name, 'w') as param_json:
			json.dump(self.param_json, param_json)

		self.param_json = json_file_name

		with open(file, 'w') as config_file:
			yaml.dump(self, config_file, default_flow_style=False)

	def load_config(self, file="my_model.yml"):
		model_loaded = self
		try:
			with open(file, 'r') as config_file:
				model_loaded = yaml.load(config_file)
		except Exception as e:
			print(e)
		finally:
			return model_loaded



# ----------------------------------------Development_and_test------------------------------------------------

_logger = log.getLogger(__name__)

model = Model(name="Model Name")

model.log_metric("r2", 0.923)
model.log_metric("r2", 0.9323)
model.log_metric("r2", 0.9243)
model.log_metric("r2", 0.92123)

model.log_metric("mse", 0.21)
model.def_param(name="columns", type="select", value=2, min=10, max=100)
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--s", type=str, required=True)
parser.add_argument("--n", type=int, default=2)

args = parser.parse_args()

model.output = {"df":"res.csv"}

model.gen_config()
#
# model.load_config("fsdaf").set_name("second").gen_config("my_model2.yml")

