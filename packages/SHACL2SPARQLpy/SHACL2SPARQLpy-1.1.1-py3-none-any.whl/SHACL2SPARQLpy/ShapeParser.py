# -*- coding: utf-8 -*-
__author__ = "Monica Figuera and Philipp D. Rohde"

import os
import json
from SHACL2SPARQLpy.VariableGenerator import VariableGenerator
from SHACL2SPARQLpy.constraints.MinMaxConstraint import MinMaxConstraint
from SHACL2SPARQLpy.constraints.MinOnlyConstraint import MinOnlyConstraint
from SHACL2SPARQLpy.constraints.MaxOnlyConstraint import MaxOnlyConstraint
from SHACL2SPARQLpy.Shape import Shape
from SHACL2SPARQLpy.utils.globals import PARSING_ORDER
from urllib.parse import urlparse


class ShapeParser:

    def __init__(self):
        return

    def parseShapesFromDir(self, path, shapeFormat, useSelectiveQueries, maxSplitSize, ORDERBYinQueries):
        fileExtension = self.getFileExtension(shapeFormat)
        filesAbsPaths = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if fileExtension in file:
                    filesAbsPaths.append(os.path.join(r, file))

        if not filesAbsPaths:
            raise FileNotFoundError(path + " does not contain any shapes of the format " + shapeFormat)

        if shapeFormat == "JSON":
            return [self.parseJson(p, useSelectiveQueries, maxSplitSize, ORDERBYinQueries) for p in filesAbsPaths]
        else:  # TODO: implement parsing of TTL format
            print("Unexpected format: " + shapeFormat)

    def getFileExtension(self, shapeFormat):
        if shapeFormat == "SHACL":
            return ".ttl"
        else:
            return ".json"  # dot added for convenience

    def parseJson(self, path, useSelectiveQueries, maxSplitSize, ORDERBYinQueries):
        targetQuery = None

        file = open(path, "r")
        obj = json.load(file)
        targetDef = obj.get("targetDef")

        name = obj["name"]
        PARSING_ORDER.append(name)
        id = name + "_d1"  # str(i + 1) but there is only one set of conjunctions
        constraints = self.parseConstraints(name, obj["constraintDef"]["conjunctions"], targetDef, id)

        includeSPARQLPrefixes = self.abbreviatedSyntaxUsed(constraints)
        prefixes = None
        if "prefix" in obj.keys():
            prefixes = obj["prefix"]
        prefix_string = ''
        if prefixes:
            prefix_string = "\n".join(["".join("PREFIX " + key + ": " + value) for (key, value) in prefixes.items()]) + "\n"
        referencedShapes = self.shapeReferences(obj["constraintDef"]["conjunctions"][0])

        if targetDef is not None:
            query = targetDef["query"]
            if query is not None:
                targetQuery = ''.join([prefix_string if includeSPARQLPrefixes else '', query])
            if urlparse(targetDef["class"]).netloc != '':  # if the target class is a url, add '<>' to it
                targetDef = '<' + targetDef["class"] + '>'
            else:
                targetDef = targetDef["class"]

        return Shape(name, targetDef, targetQuery, constraints, id, referencedShapes,
                     useSelectiveQueries, maxSplitSize, ORDERBYinQueries, includeSPARQLPrefixes, prefix_string)

    def abbreviatedSyntaxUsed(self, constraints):
        """
        Run after parsingConstraints.
        Returns false if the constraints' predicates are using absolute paths instead of abbreviated ones
        :param constraints: all shape constraints
        :return:
        """
        for c in constraints:
            if c.path.startswith("<") and c.path.endswith(">"):
                return False
        return True

    def shapeReferences(self, constraints):
        return {c.get("shape"): c.get("path") for c in constraints if c.get("shape") is not None}

    def parseConstraints(self, shapeName, array, targetDef, constraintsId):
        varGenerator = VariableGenerator()
        return [self.parseConstraint(varGenerator, array[0][i], constraintsId + "_c" + str(i + 1), targetDef) for i in range(len(array[0]))]

    def parseConstraint(self, varGenerator, obj, id, targetDef):
        min = obj.get("min")
        max = obj.get("max")
        shapeRef = obj.get("shape")
        datatype = obj.get("datatype")
        value = obj.get("value")
        path = obj.get("path")
        negated = obj.get("negated")

        oMin = None if (min is None) else int(min)
        oMax = None if (max is None) else int(max)
        oShapeRef = None if (shapeRef is None) else str(shapeRef)
        oDatatype = None if (datatype is None) else str(datatype)
        oValue = None if (value is None) else str(value)
        oPath = None if (path is None) else str(path)
        oNeg = True if (negated is None) else not negated  # True means it is a positive constraint

        if urlparse(path).netloc != '':  # if the predicate is a url, add '<>' to it
            oPath = '<' + path + '>'

        if oPath is not None:
            if oMin is not None:
                if oMax is not None:
                    return MinMaxConstraint(varGenerator, id, oPath, oMin, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)
                return MinOnlyConstraint(varGenerator, id, oPath, oMin, oNeg, oDatatype, oValue, oShapeRef, targetDef)
            if oMax is not None:
                return MaxOnlyConstraint(varGenerator, id, oPath, oMax, oNeg, oDatatype, oValue, oShapeRef, targetDef)
