# -*- coding: utf-8 -*-
# Copyright (c) 2019, Aerele Technologies Private Limited and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.version.version import get_diff
from erpnext.controllers.item_variant import generate_keyed_value_combinations, get_variant, create_variant

def create_variants(item_template, args):
	args_set = generate_keyed_value_combinations(args)
	variants = []
	for attribute_values in args_set:
		existing_variant = get_variant(item_template, args=attribute_values)
		if not existing_variant:
			variant = create_variant(item_template, attribute_values)
			variant.save()
			variants.append(variant.name)
		else:
			variants.append(existing_variant)

	return variants

def get_attr_dict(attrs):
	attribute_set = {}
	for attribute in attrs:
		attribute_set[attribute.attribute] = [attribute.attribute_value]
	return attribute_set

def get_item_attribute_set(item_attribute_arrays):
	attribute_set = {}
	for item_attr_array in item_attribute_arrays:
		attr_set = get_attr_dict(item_attr_array)
		for attr in attr_set:
			if attr in attribute_set:
				attribute_set[attr].extend(attr_set[attr])
				attribute_set[attr] = list(set(attribute_set[attr]))
			else:
				attribute_set[attr] = attr_set[attr]
	return attribute_set


def is_similar_bom(bom1, bom2):
	diff = get_bom_diff(bom1, bom2)
	for key in diff.changed:
		if key[0] in ["quantity", "uom"]:
			return False
	for row in diff.row_changed:
		if row[0] == "items":
			for key in row[3]:
				if key[0] in ["qty", "uom", "rate"]:
					return False
	return True


def get_bom_diff(bom1, bom2):
	from frappe.model import table_fields

	out = get_diff(bom1, bom2)
	out.row_changed = []
	out.added = []
	out.removed = []

	meta = bom1.meta

	identifiers = {
		'operations': 'operation',
		'items': 'item_code',
		'scrap_items': 'item_code',
		'exploded_items': 'item_code'
	}

	for df in meta.fields:
		old_value, new_value = bom1.get(df.fieldname), bom2.get(df.fieldname)

		if df.fieldtype in table_fields:
			identifier = identifiers[df.fieldname]
			# make maps
			old_row_by_identifier, new_row_by_identifier = {}, {}
			for d in old_value:
				old_row_by_identifier[d.get(identifier)] = d
			for d in new_value:
				new_row_by_identifier[d.get(identifier)] = d

			# check rows for additions, changes
			for i, d in enumerate(new_value):
				if d.get(identifier) in old_row_by_identifier:
					diff = get_diff(old_row_by_identifier[d.get(identifier)], d, for_child=True)
					if diff and diff.changed:
						out.row_changed.append((df.fieldname, i, d.get(identifier), diff.changed))
				else:
					out.added.append([df.fieldname, d.as_dict()])

			# check for deletions
			for d in old_value:
				if not d.get(identifier) in new_row_by_identifier:
					out.removed.append([df.fieldname, d.as_dict()])

	return out

def create_additional_parts(colors,sizes,items):
	additioanl_parts=[]
	attribute_set={"Apparelo Colour":[],"Apparelo Size":[]}
	colors_=[]
	sizes_=[]
	if colors and sizes and items:
		for item in items:
			for size in sizes:
				for color in colors:
					if item.item == size.item and item.item == color.item:
						if not color in colors_:
							colors_.append(color)
						if not size  in sizes_:
							sizes_.append(size)
			attribute_set["Apparelo Colour"]=colors_
			attribute_set["Apparelo Size"]=sizes_
			additioanl_parts.extend(create_variants(item.item,attribute_set))
	print(additional_parts)
	ee
	return additioanl_parts

			
			
