# core/decision_engine.py

import os
import json
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import logging
from pathlib import Path
from enum import Enum
import uuid
import random

class DecisionContext:
    """Context for decision making with metadata and metrics"""
    
    def __init__(self, context_id: str, data: Dict[str, Any], metadata: Dict[str, Any] = None):
        self.id = context_id
        self.data = data
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.metrics = {}
    
    def add_metric(self, name: str, value: Any):
        """Add a metric to the context"""
        self.metrics[name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "id": self.id,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "metrics": self.metrics
        }

class DecisionResult:
    """Result of a decision with confidence score and rationale"""
    
    def __init__(self, decision: str, confidence: float, 
                alternatives: List[Dict[str, Any]] = None, rationale: str = None):
        self.decision = decision
        self.confidence = confidence
        self.alternatives = alternatives or []
        self.rationale = rationale
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "decision": self.decision,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "rationale": self.rationale,
            "timestamp": self.timestamp
        }

class DecisionEngine:
    """Rule-based and ML-powered decision system for document processing"""
    
    def __init__(self, rules_dir: str = "decision_rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        
        self.rules = {}
        self.models = {}
        self.decision_log = []
        
        self.logger = logging.getLogger("DecisionEngine")
        self._setup_logging()
        
        # Load predefined rules
        self._load_rules()
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_file = self.rules_dir / "decision_engine.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _load_rules(self):
        """Load rule definitions from JSON files"""
        for file_path in self.rules_dir.glob("*.json"):
            try:
                rule_name = file_path.stem
                
                with open(file_path, 'r') as f:
                    rule_def = json.load(f)
                
                self.register_rule(rule_name, rule_def)
                self.logger.info(f"Loaded rule: {rule_name}")
            except Exception as e:
                self.logger.error(f"Error loading rule from {file_path}: {e}")
    
    def register_rule(self, name: str, definition: Dict[str, Any]):
        """Register a decision rule"""
        # Validate rule definition
        required_keys = ["type", "conditions", "actions"]
        for key in required_keys:
            if key not in definition:
                raise ValueError(f"Rule definition missing required key: {key}")
        
        # Store the rule
        self.rules[name] = definition
    
    def register_model(self, name: str, model_instance: Any, model_type: str):
        """Register a decision model"""
        self.models[name] = {
            "instance": model_instance,
            "type": model_type,
            "registered_at": datetime.now().isoformat()
        }
        
        self.logger.info(f"Registered model: {name} (type: {model_type})")
    
    async def make_decision(self, context: Union[Dict[str, Any], DecisionContext], 
                          rule_name: str = None) -> DecisionResult:
        """Make a decision using rules or models"""
        # Convert context if needed
        if isinstance(context, dict):
            context_id = str(uuid.uuid4())
            context = DecisionContext(context_id, context)
        
        # Use specified rule or select based on context
        if rule_name and rule_name in self.rules:
            rule = self.rules[rule_name]
        else:
            # Select rule based on context
            rule = self._select_rule(context)
        
        if not rule:
            raise ValueError("No suitable rule found for context")
        
        # Process rule based on type
        rule_type = rule["type"]
        
        if rule_type == "decision_tree":
            result = await self._process_decision_tree(rule, context)
        elif rule_type == "ml_model":
            result = await self._process_ml_model(rule, context)
        elif rule_type == "fuzzy_logic":
            result = await self._process_fuzzy_logic(rule, context)
        elif rule_type == "abtest":
            result = await self._process_abtest(rule, context)
        else:
            raise ValueError(f"Unsupported rule type: {rule_type}")
        
        # Log decision
        self._log_decision(context, rule, result)
        
        return result
    
    def _select_rule(self, context: DecisionContext) -> Optional[Dict[str, Any]]:
        """Select an appropriate rule based on context"""
        for rule_name, rule in self.rules.items():
            # Check if rule applies to context
            if self._rule_applies_to_context(rule, context):
                return rule
        
        return None
    
    def _rule_applies_to_context(self, rule: Dict[str, Any], context: DecisionContext) -> bool:
        """Check if a rule applies to a given context"""
        # Check context requirements
        if "context_requirements" in rule:
            for key, value in rule["context_requirements"].items():
                if key not in context.data or context.data[key] != value:
                    return False
        
        return True
    
    async def _process_decision_tree(self, rule: Dict[str, Any], 
                                   context: DecisionContext) -> DecisionResult:
        """Process a decision tree rule"""
        conditions = rule["conditions"]
        
        # Traverse the decision tree
        current_node = conditions.get("root")
        if not current_node:
            raise ValueError("Decision tree missing root node")
        
        path = ["root"]
        while "children" in current_node:
            # Evaluate condition
            condition = current_node.get("condition")
            if not condition:
                break
            
            condition_result = self._evaluate_condition(condition, context.data)
            
            # Choose branch based on condition
            next_node_id = None
            if condition_result:
                next_node_id = current_node.get("if_true")
            else:
                next_node_id = current_node.get("if_false")
            
            if not next_node_id or next_node_id not in current_node["children"]:
                break
            
            # Move to next node
            current_node = current_node["children"][next_node_id]
            path.append(next_node_id)
        
        # Get decision from leaf node
        decision = current_node.get("decision")
        confidence = current_node.get("confidence", 1.0)
        rationale = current_node.get("rationale", f"Decision path: {' -> '.join(path)}")
        
        # Get alternatives if any
        alternatives = []
        if "alternatives" in current_node:
            for alt in current_node["alternatives"]:
                alternatives.append({
                    "decision": alt["decision"],
                    "confidence": alt.get("confidence", 0.0)
                })
        
        return DecisionResult(decision, confidence, alternatives, rationale)
    
    async def _process_ml_model(self, rule: Dict[str, Any], 
                              context: DecisionContext) -> DecisionResult:
        """Process a machine learning model rule"""
        model_name = rule.get("model_name")
        if not model_name or model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_info = self.models[model_name]
        model = model_info["instance"]
        
        # Prepare input features
        feature_mapping = rule.get("feature_mapping", {})
        features = {}
        
        for target_feature, source_path in feature_mapping.items():
            features[target_feature] = self._get_nested_value(context.data, source_path)
        
        # Get prediction from model
        prediction = await self._get_model_prediction(model, features)
        
        # Parse prediction
        decision = prediction.get("decision")
        confidence = prediction.get("confidence", 0.0)
        alternatives = prediction.get("alternatives", [])
        rationale = prediction.get("rationale", "Model-based decision")
        
        return DecisionResult(decision, confidence, alternatives, rationale)
    
    async def _process_fuzzy_logic(self, rule: Dict[str, Any], 
                                 context: DecisionContext) -> DecisionResult:
        """Process a fuzzy logic rule"""
        fuzzy_variables = rule.get("fuzzy_variables", {})
        fuzzy_rules = rule.get("fuzzy_rules", [])
        
        # Calculate fuzzy variable values
        variable_values = {}
        for var_name, var_def in fuzzy_variables.items():
            source_path = var_def.get("source_path")
            if source_path:
                raw_value = self._get_nested_value(context.data, source_path)
                
                # Apply membership functions
                membership = {}
                for set_name, set_def in var_def.get("membership_functions", {}).items():
                    membership[set_name] = self._calculate_membership(raw_value, set_def)
                
                variable_values[var_name] = {
                    "raw_value": raw_value,
                    "membership": membership
                }
        
        # Apply fuzzy rules
        rule_activations = []
        for fuzzy_rule in fuzzy_rules:
            antecedent = fuzzy_rule.get("if")
            consequent = fuzzy_rule.get("then")
            
            # Calculate activation level
            activation = self._evaluate_fuzzy_antecedent(antecedent, variable_values)
            
            if activation > 0:
                rule_activations.append({
                    "rule": fuzzy_rule,
                    "activation": activation,
                    "consequent": consequent
                })
        
        # Defuzzify to get final decision
        decision, confidence = self._defuzzify(rule_activations)
        
        # Get alternatives
        alternatives = []
        for ra in rule_activations:
            if ra["consequent"]["decision"] != decision:
                alternatives.append({
                    "decision": ra["consequent"]["decision"],
                    "confidence": ra["activation"]
                })
        
        # Sort alternatives by confidence
        alternatives.sort(key=lambda x: x["confidence"], reverse=True)
        
        rationale = f"Fuzzy logic decision based on {len(rule_activations)} activated rules"
        
        return DecisionResult(decision, confidence, alternatives, rationale)
    
    async def _process_abtest(self, rule: Dict[str, Any], 
                            context: DecisionContext) -> DecisionResult:
        """Process an A/B testing rule"""
        variants = rule.get("variants", [])
        if not variants:
            raise ValueError("A/B test rule has no variants")
        
        # Check if context already has a variant assignment
        variant_key = rule.get("variant_key", "variant")
        assigned_variant = context.metadata.get(variant_key)
        
        if assigned_variant:
            # Use previously assigned variant
            for variant in variants:
                if variant["id"] == assigned_variant:
                    decision = variant.get("decision")
                    confidence = variant.get("confidence", 1.0)
                    rationale = f"Using previously assigned A/B test variant: {assigned_variant}"
                    
                    # Create alternatives from other variants
                    alternatives = []
                    for other_variant in variants:
                        if other_variant["id"] != assigned_variant:
                            alternatives.append({
                                "decision": other_variant.get("decision"),
                                "confidence": other_variant.get("confidence", 0.0)
                            })
                    
                    return DecisionResult(decision, confidence, alternatives, rationale)
        
        # Assign a variant based on weights
        total_weight = sum(variant.get("weight", 1) for variant in variants)
        rand_val = random.random() * total_weight
        
        cumulative_weight = 0
        selected_variant = None
        
        for variant in variants:
            weight = variant.get("weight", 1)
            cumulative_weight += weight
            
            if rand_val <= cumulative_weight:
                selected_variant = variant
                break
        
        if not selected_variant:
            selected_variant = variants[-1]
        
        # Update context with assigned variant
        context.metadata[variant_key] = selected_variant["id"]
        
        # Return decision
        decision = selected_variant.get("decision")
        confidence = selected_variant.get("confidence", 1.0)
        rationale = f"Assigned A/B test variant: {selected_variant['id']}"
        
        # Create alternatives from other variants
        alternatives = []
        for other_variant in variants:
            if other_variant["id"] != selected_variant["id"]:
                alternatives.append({
                    "decision": other_variant.get("decision"),
                    "confidence": other_variant.get("confidence", 0.0)
                })
        
        return DecisionResult(decision, confidence, alternatives, rationale)
    
    def _evaluate_condition(self, condition: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate a condition against data"""
        operator = condition.get("operator")
        if not operator:
            raise ValueError("Condition missing operator")
        
        if operator == "eq":
            left = self._get_nested_value(data, condition.get("left"))
            right = self._get_nested_value(data, condition.get("right"))
            return left == right
        elif operator == "ne":
            left = self._get_nested_value(data, condition.get("left"))
            right = self._get_nested_value(data, condition.get("right"))
            return left != right
        elif operator == "gt":
            left = self._get_nested_value(data, condition.get("left"))
            right = self._get_nested_value(data, condition.get("right"))
            return left > right
        elif operator == "lt":
            left = self._get_nested_value(data, condition.get("left"))
            right = self._get_nested_value(data, condition.get("right"))
            return left < right
        elif operator == "contains":
            container = self._get_nested_value(data, condition.get("container"))
            item = self._get_nested_value(data, condition.get("item"))
            return item in container
        elif operator == "and":
            subconditions = condition.get("conditions", [])
            return all(self._evaluate_condition(sc, data) for sc in subconditions)
        elif operator == "or":
            subconditions = condition.get("conditions", [])
            return any(self._evaluate_condition(sc, data) for sc in subconditions)
        elif operator == "not":
            subcondition = condition.get("condition")
            return not self._evaluate_condition(subcondition, data)
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    
    def _get_nested_value(self, data: Dict[str, Any], path: Union[str, Any]) -> Any:
        """Get a value from nested dictionaries using dot notation path"""
        # If path is not a string, return it as a literal value
        if not isinstance(path, str):
            return path
        
        # Handle empty path
        if not path:
            return None
        
        # Handle literal values prefixed with $literal:
        if path.startswith("$literal:"):
            return path[9:]
        
        # Handle nested paths with dot notation
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    async def _get_model_prediction(self, model: Any, features: Dict[str, Any]) -> Dict[str, Any]:
        """Get prediction from a model"""
        # This is a placeholder - actual implementation would depend on model type
        if hasattr(model, "predict"):
            raw_prediction = model.predict(features)
            return {
                "decision": raw_prediction,
                "confidence": 0.9,  # Placeholder
                "alternatives": []  # Placeholder
            }
        elif hasattr(model, "predict_proba"):
            probas = model.predict_proba(features)
            # Process probabilities to get decision and alternatives
            # This is a simplified example
            classes = getattr(model, "classes_", list(range(len(probas[0]))))
            decision_idx = probas[0].argmax()
            
            return {
                "decision": classes[decision_idx],
                "confidence": probas[0][decision_idx],
                "alternatives": [
                    {"decision": classes[i], "confidence": probas[0][i]}
                    for i in range(len(probas[0]))
                    if i != decision_idx
                ]
            }
        
        # Fallback to using AzureChatOpenAI for ML model
        from langchain_openai import AzureChatOpenAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        
        llm = AzureChatOpenAI(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.0,
            max_tokens=1024
        )
        
        prompt = PromptTemplate.from_template(
            """Given the following features, make a decision:
            
            Features:
            {features}
            
            Return a JSON object with the following structure:
            {
                "decision": "The decision value",
                "confidence": 0.95,  // A number between 0 and 1
                "alternatives": [
                    {
                        "decision": "Alternative 1",
                        "confidence": 0.85
                    },
                    // Other alternatives...
                ],
                "rationale": "Explanation for the decision"
            }
            """
        )
        
        chain = prompt | llm | JsonOutputParser()
        
        try:
            result = chain.invoke({"features": json.dumps(features, indent=2)})
            return result
        except Exception as e:
            self.logger.error(f"Error getting prediction from LLM: {e}")
            return {
                "decision": "unknown",
                "confidence": 0.0,
                "alternatives": [],
                "rationale": f"Error: {str(e)}"
            }
    
    def _calculate_membership(self, value: Any, membership_function: Dict[str, Any]) -> float:
        """Calculate membership degree for a fuzzy set"""
        mf_type = membership_function.get("type")
        
        if mf_type == "triangle":
            a = membership_function.get("a", 0)
            b = membership_function.get("b", 0.5)
            c = membership_function.get("c", 1)
            
            if value <= a or value >= c:
                return 0.0
            elif a < value <= b:
                return (value - a) / (b - a)
            else:  # b < value < c
                return (c - value) / (c - b)
        
        elif mf_type == "trapezoid":
            a = membership_function.get("a", 0)
            b = membership_function.get("b", 0.25)
            c = membership_function.get("c", 0.75)
            d = membership_function.get("d", 1)
            
            if value <= a or value >= d:
                return 0.0
            elif a < value <= b:
                return (value - a) / (b - a)
            elif b < value <= c:
                return 1.0
            else:  # c < value < d
                return (d - value) / (d - c)
        
        elif mf_type == "gaussian":
            mean = membership_function.get("mean", 0.5)
            sigma = membership_function.get("sigma", 0.1)
            
            return math.exp(-((value - mean) ** 2) / (2 * sigma ** 2))
        
        else:
            return 0.0
    
    def _evaluate_fuzzy_antecedent(self, antecedent: Dict[str, Any], 
                                 variable_values: Dict[str, Dict[str, Any]]) -> float:
        """Evaluate a fuzzy antecedent"""
        operator = antecedent.get("operator", "and")
        
        if operator == "and":
            # Minimum of all membership values
            values = []
            for clause in antecedent.get("clauses", []):
                var_name = clause.get("variable")
                set_name = clause.get("set")
                
                if var_name in variable_values and set_name in variable_values[var_name]["membership"]:
                    values.append(variable_values[var_name]["membership"][set_name])
                else:
                    values.append(0.0)
            
            return min(values) if values else 0.0
        
        elif operator == "or":
            # Maximum of all membership values
            values = []
            for clause in antecedent.get("clauses", []):
                var_name = clause.get("variable")
                set_name = clause.get("set")
                
                if var_name in variable_values and set_name in variable_values[var_name]["membership"]:
                    values.append(variable_values[var_name]["membership"][set_name])
                else:
                    values.append(0.0)
            
            return max(values) if values else 0.0
        
        else:
            return 0.0
    
    def _defuzzify(self, rule_activations: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Defuzzify rule activations to get final decision"""
        if not rule_activations:
            return "unknown", 0.0
        
        # Group by decision
        decision_activations = {}
        for ra in rule_activations:
            decision = ra["consequent"]["decision"]
            if decision not in decision_activations:
                decision_activations[decision] = []
            
            decision_activations[decision].append(ra["activation"])
        
        # Calculate maximum activation for each decision
        decision_max = {d: max(activations) for d, activations in decision_activations.items()}
        
        # Find decision with highest activation
        max_decision = max(decision_max.items(), key=lambda x: x[1])
        
        return max_decision[0], max_decision[1]
    
    def _log_decision(self, context: DecisionContext, rule: Dict[str, Any], 
                    result: DecisionResult):
        """Log a decision for auditing"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "context_id": context.id,
            "context_data": context.data,
            "context_metadata": context.metadata,
            "rule_name": rule.get("name", "unknown"),
            "rule_type": rule.get("type", "unknown"),
            "decision": result.decision,
            "confidence": result.confidence,
            "rationale": result.rationale,
            "alternatives": result.alternatives
        }
        
        self.decision_log.append(log_entry)
        
        # Write to log file
        log_file = self.rules_dir / "decisions.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")