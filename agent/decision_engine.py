# Modified decision_engine.py with LangGraph integration

import os
import json
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import logging
from pathlib import Path
from enum import Enum
import uuid
import random
# Add LangGraph imports
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver

# Define decision state
class DecisionState(TypedDict):
    context_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str
    decision: Optional[str]
    confidence: float
    alternatives: List[Dict[str, Any]]
    rationale: Optional[str]
    errors: List[str]

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
    """Rule-based and ML-powered decision system using LangGraph for document processing"""
    
    def __init__(self, rules_dir: str = "decision_rules"):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(exist_ok=True)
        
        self.rules = {}
        self.models = {}
        self.decision_log = []
        
        self.logger = logging.getLogger("DecisionEngine")
        self._setup_logging()
        
        # Initialize LangGraph components
        self.checkpointer = MemorySaver()
        self._create_decision_graph()
        
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
    
    def _create_decision_graph(self):
        """Create the LangGraph decision graph"""
        # Define the nodes for decision making
        
        def initialize_decision(state: DecisionState) -> DecisionState:
            """Initialize decision state"""
            state["decision"] = None
            state["confidence"] = 0.0
            state["alternatives"] = []
            state["errors"] = []
            return state
        
        def select_rule(state: DecisionState) -> Dict[str, Any]:
            """Select appropriate rule based on context"""
            context_data = state["data"]
            # Logic to select a rule based on context
            rule_name = self._select_rule_for_context(context_data)
            return {"rule": rule_name}
        
        def evaluate_condition(state: DecisionState) -> Dict[str, Any]:
            """Evaluate rule condition"""
            rule_name = state.get("rule")
            if not rule_name or rule_name not in self.rules:
                return {"decision_path": "error"}
            
            rule = self.rules[rule_name]
            conditions = rule.get("conditions", {})
            
            try:
                result = self._evaluate_conditions(conditions, state["data"])
                return {"condition_result": result, "decision_path": "success" if result else "failure"}
            except Exception as e:
                state["errors"].append(str(e))
                return {"decision_path": "error"}
        
        def execute_action(state: DecisionState) -> Dict[str, Any]:
            """Execute rule action based on condition result"""
            rule_name = state.get("rule")
            if not rule_name or rule_name not in self.rules:
                return {"decision": "error", "confidence": 0.0, "rationale": "Rule not found"}
            
            rule = self.rules[rule_name]
            actions = rule.get("actions", {})
            
            try:
                if state["decision_path"] == "success":
                    action_data = actions.get("success", {})
                else:
                    action_data = actions.get("failure", {})
                
                decision = action_data.get("decision", "unknown")
                confidence = action_data.get("confidence", 0.5)
                rationale = action_data.get("rationale", "Based on rule evaluation")
                
                return {
                    "decision": decision,
                    "confidence": confidence,
                    "rationale": rationale
                }
            except Exception as e:
                state["errors"].append(str(e))
                return {"decision": "error", "confidence": 0.0, "rationale": f"Error: {str(e)}"}
        
        def generate_alternatives(state: DecisionState) -> Dict[str, Any]:
            """Generate alternative decisions"""
            rule_name = state.get("rule")
            if not rule_name or rule_name not in self.rules:
                return {"alternatives": []}
            
            rule = self.rules[rule_name]
            alternatives = rule.get("alternatives", [])
            
            return {"alternatives": alternatives}
        
        def log_decision(state: DecisionState) -> Dict[str, Any]:
            """Log the decision for audit purposes"""
            log_entry = {
                "context_id": state["context_id"],
                "rule": state.get("rule", "unknown"),
                "decision": state["decision"],
                "confidence": state["confidence"],
                "rationale": state["rationale"],
                "timestamp": datetime.now().isoformat(),
                "alternatives": state["alternatives"]
            }
            
            self.decision_log.append(log_entry)
            return {}
        
        # Create the graph
        graph = StateGraph(DecisionState)
        
        # Add nodes
        graph.add_node("initialize", initialize_decision)
        graph.add_node("select_rule", select_rule)
        graph.add_node("evaluate_condition", evaluate_condition)
        graph.add_node("execute_action", execute_action)
        graph.add_node("generate_alternatives", generate_alternatives)
        graph.add_node("log_decision", log_decision)
        
        # Define the edges
        graph.set_entry_point("initialize")
        graph.add_edge("initialize", "select_rule")
        graph.add_edge("select_rule", "evaluate_condition")
        
        # Add conditional edges based on evaluation result
        graph.add_conditional_edges(
            "evaluate_condition",
            lambda x: x["decision_path"],
            {
                "success": "execute_action",
                "failure": "execute_action",
                "error": END
            }
        )
        
        graph.add_edge("execute_action", "generate_alternatives")
        graph.add_edge("generate_alternatives", "log_decision")
        graph.add_edge("log_decision", END)
        
        # Compile the graph
        self.decision_graph = graph.compile()
    
    def _select_rule_for_context(self, context_data: Dict[str, Any]) -> Optional[str]:
        """Select an appropriate rule based on context"""
        for rule_name, rule in self.rules.items():
            # Check if rule applies to context
            if self._rule_applies_to_context(rule, context_data):
                return rule_name
        
        return None
    
    def _rule_applies_to_context(self, rule: Dict[str, Any], context_data: Dict[str, Any]) -> bool:
        """Check if a rule applies to a given context"""
        # Check context requirements
        if "context_requirements" in rule:
            for key, value in rule["context_requirements"].items():
                if key not in context_data or context_data[key] != value:
                    return False
        
        return True
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate conditions against data"""
        operator = conditions.get("operator")
        if not operator:
            return True
        
        if operator == "eq":
            left = self._get_nested_value(data, conditions.get("left"))
            right = self._get_nested_value(data, conditions.get("right"))
            return left == right
        elif operator == "ne":
            left = self._get_nested_value(data, conditions.get("left"))
            right = self._get_nested_value(data, conditions.get("right"))
            return left != right
        elif operator == "gt":
            left = self._get_nested_value(data, conditions.get("left"))
            right = self._get_nested_value(data, conditions.get("right"))
            return left > right
        elif operator == "lt":
            left = self._get_nested_value(data, conditions.get("left"))
            right = self._get_nested_value(data, conditions.get("right"))
            return left < right
        elif operator == "contains":
            container = self._get_nested_value(data, conditions.get("container"))
            item = self._get_nested_value(data, conditions.get("item"))
            return item in container
        elif operator == "and":
            subconditions = conditions.get("conditions", [])
            return all(self._evaluate_conditions(sc, data) for sc in subconditions)
        elif operator == "or":
            subconditions = conditions.get("conditions", [])
            return any(self._evaluate_conditions(sc, data) for sc in subconditions)
        elif operator == "not":
            subcondition = conditions.get("condition")
            return not self._evaluate_conditions(subcondition, data)
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
    
    async def make_decision(self, context: Union[Dict[str, Any], DecisionContext]) -> DecisionResult:
        """Make a decision using the LangGraph decision engine"""
        # Convert context if needed
        if isinstance(context, dict):
            context_id = str(uuid.uuid4())
            context = DecisionContext(context_id, context)
        
        # Prepare initial state
        initial_state = DecisionState(
            context_id=context.id,
            data=context.data,
            metadata=context.metadata,
            metrics=context.metrics,
            timestamp=context.timestamp,
            decision=None,
            confidence=0.0,
            alternatives=[],
            rationale=None,
            errors=[]
        )
        
        # Configure LangGraph with thread_id for persistence
        config = {
            "configurable": {
                "thread_id": f"decision_{context.id}",
                "context_id": context.id
            }
        }
        
        # Execute the decision graph
        try:
            final_state = self.decision_graph.invoke(initial_state, config=config)
            
            # Create result from final state
            result = DecisionResult(
                decision=final_state["decision"],
                confidence=final_state["confidence"],
                alternatives=final_state["alternatives"],
                rationale=final_state["rationale"]
            )
            
            return result
        except Exception as e:
            self.logger.error(f"Error in decision graph: {e}")
            return DecisionResult(
                decision="error",
                confidence=0.0,
                rationale=f"Error in decision process: {str(e)}"
            )