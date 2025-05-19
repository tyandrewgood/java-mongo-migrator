import javalang
from typing import List, Dict, Any, Optional, Union
from javalang.tree import ClassDeclaration, InterfaceDeclaration, EnumDeclaration

# Mapping annotation (lowercase) to classification type
ANNOTATION_CLASS_MAP = {
    "entity": "Entity",
    "repository": "Repository",
    "dao": "Repository",
    "service": "Service",
    "stateless": "EJB",
    "singleton": "EJB",
    "inject": "CDI Injection",
    "event": "CDI Event",
    "managedbean": "JSF Managed Bean",
    "facesvalidator": "JSF Validator",
    "observes": "CDI Observer",
    "slf4j": "Logging",
    "log": "Logging"
}


def safe_annotation_name(anno) -> Optional[str]:
    """
    Safely get annotation name, returns None if not present.
    """
    return getattr(anno, "name", None)


class JavaParser:
    def parse_java_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a Java source file and extracts high-level structural information for each top-level class.
        
        Returns a list of dictionaries where each dictionary contains:
            - name: Name of the class
            - annotations: List of annotation names (lowercased)
            - fields: List of field definitions with type, name, annotations, and modifiers
            - methods: List of method definitions with name, annotations, and modifiers
            - type: Inferred classification(s) (e.g., Entity, Service, Repository)
            - nested_types: List of nested class/interface/enum declarations with full structure

        If parsing fails, returns a single-item list with an error message.
        """
        parsed_classes = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
                tree = javalang.parse.parse(code)

            for _, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = {
                    "name": node.name,
                    "annotations": [a.name.lower() for a in node.annotations],
                    "fields": self.extract_fields(node),
                    "methods": self.extract_methods(node),
                    "type": self.classify_java_component(node),
                    "nested_types": self.extract_nested_types(node)
                }
                parsed_classes.append(class_info)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            parsed_classes.append({"error": f"Failed to parse {file_path}: {str(e)}"})

        return parsed_classes

    def extract_nested_types(self, node: Union[ClassDeclaration, InterfaceDeclaration, EnumDeclaration]) -> List[Dict[str, Any]]:
        """
        Extract nested classes, interfaces, or enums inside a given class-like node.
        """
        nested_types = []
        for inner_node in getattr(node, "body", []):
            if isinstance(inner_node, (ClassDeclaration, InterfaceDeclaration, EnumDeclaration)):
                nested_types.append(self.parse_type_declaration(inner_node))
        return nested_types

    def parse_type_declaration(self, node: Union[ClassDeclaration, InterfaceDeclaration, EnumDeclaration]) -> Dict[str, Any]:
        """
        Parses a type declaration node into a structured dict including nested types.
        """
        return {
            "name": node.name,
            "kind": type(node).__name__,
            "type": self.classify_java_component(node),
            "annotations": [a.name.lower() for a in node.annotations if safe_annotation_name(a)],
            "modifiers": list(node.modifiers) if hasattr(node, "modifiers") else [],
            "fields": self.extract_fields(node),
            "methods": self.extract_methods(node),
            "nested_types": self.extract_nested_types(node)
        }

    def extract_fields(self, class_node: Union[ClassDeclaration, InterfaceDeclaration, EnumDeclaration]) -> List[Dict[str, Any]]:
        """
        Extract fields from a class, interface or enum node, including names, types,
        annotations, and modifiers.
        """
        fields = []
        for field in getattr(class_node, "fields", []):
            field_type = self.type_to_str(field.type)
            field_annotations = [a.name.lower() for a in getattr(field, "annotations", []) if safe_annotation_name(a)]
            modifiers = list(field.modifiers) if hasattr(field, "modifiers") else []
            for declarator in field.declarators:
                fields.append({
                    "name": declarator.name,
                    "type": field_type,
                    "annotations": field_annotations,
                    "modifiers": modifiers
                })
        return fields

    def extract_methods(self, class_node: Union[ClassDeclaration, InterfaceDeclaration, EnumDeclaration]) -> List[Dict[str, Any]]:
        """
        Extract methods from a class, interface or enum node including names,
        annotations, and modifiers.
        """
        methods = []
        for method in getattr(class_node, "methods", []):
            method_annotations = [a.name.lower() for a in getattr(method, "annotations", []) if safe_annotation_name(a)]
            modifiers = list(method.modifiers) if hasattr(method, "modifiers") else []
            methods.append({
                "name": method.name,
                "annotations": method_annotations,
                "modifiers": modifiers
            })
        return methods

    def type_to_str(self, type_obj: Optional[javalang.tree.Type]) -> Optional[str]:
        """
        Converts a javalang Type object to a string representation including generics.
        """
        if type_obj is None:
            return None

        base_name = getattr(type_obj, "name", None)
        if base_name is None:
            base_name = str(type_obj)

        # Handle generics, e.g. List<Foo>
        if hasattr(type_obj, "arguments") and type_obj.arguments:
            args = []
            for arg in type_obj.arguments:
                if hasattr(arg, "type"):
                    args.append(self.type_to_str(arg.type))
                else:
                    args.append(str(arg))
            base_name += "<" + ",".join(args) + ">"

        return base_name

    def classify_java_component(self, node: Union[ClassDeclaration, InterfaceDeclaration, EnumDeclaration]) -> List[str]:
        """
        Classifies a type as Entity, Repository, Service, EJB, CDI, JSF Bean, Validator, Logging, etc.
        Supports multiple classifications if multiple annotations are present.
        """
        annotations = {a.name.lower() for a in node.annotations if safe_annotation_name(a)}
        classifications = []

        for anno in annotations:
            if anno in ANNOTATION_CLASS_MAP and ANNOTATION_CLASS_MAP[anno] not in classifications:
                classifications.append(ANNOTATION_CLASS_MAP[anno])

        for field in getattr(node, "fields", []):
            field_annotations = {a.name.lower() for a in getattr(field, "annotations", []) if safe_annotation_name(a)}
            for fa in field_annotations:
                if fa in ANNOTATION_CLASS_MAP and ANNOTATION_CLASS_MAP[fa] not in classifications:
                    classifications.append(ANNOTATION_CLASS_MAP[fa])

            field_type_name = self.type_to_str(field.type)
            if field_type_name and field_type_name.startswith("Event") and "CDI Event" not in classifications:
                classifications.append("CDI Event")

        for method in getattr(node, "methods", []):
            method_annotations = {a.name.lower() for a in getattr(method, "annotations", []) if safe_annotation_name(a)}
            if "observes" in method_annotations and "CDI Observer" not in classifications:
                classifications.append("CDI Observer")

        if "managedbean" in annotations and "JSF Managed Bean" not in classifications:
            classifications.append("JSF Managed Bean")
        if "facesvalidator" in annotations and "JSF Validator" not in classifications:
            classifications.append("JSF Validator")

        if not classifications:
            classifications.append("Unknown")

        return classifications
