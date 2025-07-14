# Modified workflow_engine.py with LangGraph integration

import os
import yaml
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union, TypedDict
from datetime import datetime
import networkx as nx
from pathlib import Path
import logging
import uuid
from enum import Enum
# Add LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Define WorkflowState for LangGraph
class WorkflowState(TypedDict):
    instance_id: str
    workflow_name: str
    status: str
    data: Dict[str, Any]
    node_status: Dict[str, str]
    current_nodes: List[str]
    completed_nodes: List[str]
    failed_nodes: List[str]
    logs: List[Dict[str, Any]]
    error: Optional[str]

class WorkflowEngine:
    """Flexible workflow execution system using LangGraph for document processing pipelines"""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(exist_ok=True)
        
        self.workflows = {}
        self.workflow_instances = {}
        self.node_handlers = {}
        
        # Add LangGraph components
        self.checkpointer = MemorySaver()
        self.workflow_graphs = {}
        
        self.logger = logging.getLogger("WorkflowEngine")
        self._setup_logging()
        
        # Load predefined workflows
        self._load_workflows()
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_file = self.workflows_dir / "workflow_engine.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _load_workflows(self):
        """Load workflow definitions from YAML/JSON files"""
        for ext in [".yaml", ".yml", ".json"]:
            for file_path in self.workflows_dir.glob(f"*{ext}"):
                try:
                    workflow_name = file_path.stem
                    
                    with open(file_path, 'r') as f:
                        if ext == ".json":
                            workflow_def = json.load(f)
                        else:
                            workflow_def = yaml.safe_load(f)
                    
                    self.register_workflow(workflow_name, workflow_def)
                    self.logger.info(f"Loaded workflow: {workflow_name}")
                except Exception as e:
                    self.logger.error(f"Error loading workflow from {file_path}: {e}")
    
    def register_workflow(self, name: str, definition: Dict[str, Any]):
        """Register a workflow definition and create a LangGraph representation"""
        # Validate workflow definition
        required_keys = ["version", "nodes", "edges"]
        for key in required_keys:
            if key not in definition:
                raise ValueError(f"Workflow definition missing required key: {key}")
        
        # Create a directed graph representation
        workflow_graph = nx.DiGraph()
        
        # Add nodes
        for node_id, node_def in definition["nodes"].items():
            workflow_graph.add_node(node_id, **node_def)
        
        # Add edges
        for edge in definition["edges"]:
            source = edge["source"]
            target = edge["target"]
            condition = edge.get("condition")
            
            workflow_graph.add_edge(source, target, condition=condition)
        
        # Check if graph is a DAG
        if not nx.is_directed_acyclic_graph(workflow_graph):
            raise ValueError(f"Workflow '{name}' contains cycles")
        
        # Store the workflow
        self.workflows[name] = {
            "definition": definition,
            "graph": workflow_graph,
            "version": definition["version"]
        }
        
        # Pass workflow_graph to LangGraph creation
        self._create_workflow_langgraph(name, definition, workflow_graph)

    def _create_workflow_langgraph(self, workflow_name: str, definition: Dict[str, Any], workflow_graph: nx.DiGraph):
        """Create a LangGraph representation of the workflow"""
        
        # Create StateGraph with WorkflowState
        workflow_builder = StateGraph(WorkflowState)
        
        # Add nodes
        for node_id, node_def in definition["nodes"].items():
            def node_executor(state: WorkflowState, node_id=node_id, node_def=node_def):
                state["node_status"][node_id] = NodeStatus.RUNNING.value
                state["current_nodes"] = [n for n in state["current_nodes"] if n != node_id] + [node_id]
                input_data = {
                    "node_id": node_id,
                    "instance_id": state["instance_id"],
                    "workflow_data": state["data"],
                    "node_params": node_def.get("params", {})
                }
                try:
                    if node_def.get("type") in self.node_handlers:
                        handler = self.node_handlers[node_def["type"]]
                        result = handler(input_data)
                        state["data"][f"node_result_{node_id}"] = result
                        state["node_status"][node_id] = NodeStatus.COMPLETED.value
                        state["completed_nodes"] = state["completed_nodes"] + [node_id]
                        state["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": f"Node {node_id} completed successfully"
                        })
                    else:
                        state["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"No handler for node type: {node_def.get('type')}"
                        })
                        state["node_status"][node_id] = NodeStatus.FAILED.value
                        state["failed_nodes"] = state["failed_nodes"] + [node_id]
                        state["error"] = f"No handler for node type: {node_def.get('type')}"
                except Exception as e:
                    state["logs"].append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "ERROR",
                        "message": f"Node {node_id} failed: {str(e)}"
                    })
                    state["node_status"][node_id] = NodeStatus.FAILED.value
                    state["failed_nodes"] = state["failed_nodes"] + [node_id]
                    state["error"] = str(e)
                return state
            workflow_builder.add_node(node_id, node_executor)
        
        # Add edges
        for edge in definition["edges"]:
            source = edge["source"]
            target = edge["target"]
            condition = edge.get("condition")
            if condition:
                def edge_router(state: WorkflowState, condition=condition):
                    try:
                        condition_var = condition.get("variable", "")
                        if condition_var in state["data"]:
                            expected_value = condition.get("value")
                            actual_value = state["data"][condition_var]
                            if actual_value == expected_value:
                                return target
                            else:
                                alt_targets = [e["target"] for e in definition["edges"] 
                                            if e["source"] == source and e != edge]
                                if alt_targets:
                                    return alt_targets[0]
                                else:
                                    return END
                        else:
                            return END
                    except Exception as e:
                        state["logs"].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "ERROR",
                            "message": f"Error evaluating condition: {str(e)}"
                        })
                        return END
                workflow_builder.add_conditional_edges(
                    source,
                    edge_router,
                    {
                        target: target,
                        END: END
                    }
                )
            else:
                workflow_builder.add_edge(source, target)
        
        # Find start nodes (nodes with no incoming edges)
        start_nodes = [node for node in workflow_graph.nodes() 
                    if workflow_graph.in_degree(node) == 0]
        if start_nodes:
            workflow_builder.set_entry_point(start_nodes[0])
        
        # Find end nodes (nodes with no outgoing edges)
        end_nodes = [node for node in workflow_graph.nodes() 
                    if workflow_graph.out_degree(node) == 0]
        for end_node in end_nodes:
            workflow_builder.add_edge(end_node, END)
        
        compiled_graph = workflow_builder.compile()
        self.workflow_graphs[workflow_name] = compiled_graph

# Add to WorkflowEngine class
    def create_documentation_workflow(self) -> str:
        """Create workflow definition for graph-based documentation"""
        workflow_def = {
            "version": "1.0",
            "nodes": {
                "initialize": {
                    "type": "initialize_processor",
                    "params": {"setup_memory": True, "setup_similarity": True}
                },
                "create_memory": {
                    "type": "memory_creation", 
                    "params": {"compression_level": "balanced"}
                },
                "organize_chunks": {
                    "type": "similarity_chunking",
                    "params": {"max_docs_per_chunk": 10, "max_similar_chunks": 3}
                },
                "generate_content": {
                    "type": "content_generation",
                    "params": {"use_memory": True, "use_graph": True}
                },
                "finalize": {
                    "type": "finalize_output",
                    "params": {"format": "markdown"}
                }
            },
            "edges": [
                {"source": "initialize", "target": "create_memory"},
                {"source": "create_memory", "target": "organize_chunks"},
                {"source": "organize_chunks", "target": "generate_content"},
                {"source": "generate_content", "target": "finalize"}
            ]
        }
        
        self.register_workflow("documentation_generation", workflow_def)
        return "documentation_generation"

    def register_node_handler(self, node_type: str, handler: Callable):
        """Register a handler function for a node type"""
        self.node_handlers[node_type] = handler
        self.logger.info(f"Registered handler for node type: {node_type}")
    
    def create_workflow_instance(self, workflow_name: str, initial_data: Dict[str, Any] = None) -> str:
        """Create a new instance of a workflow"""
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        
        # Generate a unique instance ID
        instance_id = str(uuid.uuid4())
        
        # Get all nodes from the workflow definition
        all_nodes = list(workflow["graph"].nodes())
        
        # Initialize instance state
        instance = {
            "id": instance_id,
            "workflow_name": workflow_name,
            "workflow_version": workflow["definition"]["version"],
            "status": WorkflowStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": initial_data or {},
            "node_status": {node: NodeStatus.PENDING.value for node in all_nodes},
            "current_nodes": [],
            "completed_nodes": [],
            "failed_nodes": [],
            "logs": []
        }
        
        # Store the instance
        self.workflow_instances[instance_id] = instance
        
        self.logger.info(f"Created workflow instance: {instance_id} (workflow: {workflow_name})")
        return instance_id
    
    async def execute_workflow(self, instance_id: str) -> Dict[str, Any]:
        """Execute a workflow instance using LangGraph"""
        if instance_id not in self.workflow_instances:
            raise ValueError(f"Unknown workflow instance: {instance_id}")
        
        instance = self.workflow_instances[instance_id]
        workflow_name = instance["workflow_name"]
        
        if workflow_name not in self.workflow_graphs:
            raise ValueError(f"No LangGraph implementation for workflow: {workflow_name}")
        
        graph = self.workflow_graphs[workflow_name]
        
        # Update instance status
        instance["status"] = WorkflowStatus.RUNNING.value
        instance["started_at"] = datetime.now().isoformat()
        self._log_instance(instance_id, "Started workflow execution")
        
        # Create initial state for LangGraph
        initial_state = WorkflowState(
            instance_id=instance_id,
            workflow_name=workflow_name,
            status=WorkflowStatus.RUNNING.value,
            data=instance["data"],
            node_status=instance["node_status"],
            current_nodes=instance["current_nodes"],
            completed_nodes=instance["completed_nodes"],
            failed_nodes=instance["failed_nodes"],
            logs=instance["logs"],
            error=None
        )
        
        # Configure LangGraph with thread_id for persistence
        config = {
            "configurable": {
                "thread_id": f"workflow_{instance_id}",
                "instance_id": instance_id
            }
        }
        
        try:
            # Execute the workflow graph
            final_state = graph.invoke(initial_state, config=config)
            
            # Update instance with final state
            instance["status"] = WorkflowStatus.COMPLETED.value
            instance["completed_at"] = datetime.now().isoformat()
            instance["data"] = final_state["data"]
            instance["node_status"] = final_state["node_status"]
            instance["completed_nodes"] = final_state["completed_nodes"]
            instance["failed_nodes"] = final_state["failed_nodes"]
            
            self._log_instance(instance_id, "Workflow completed successfully")
            
            return instance["data"]
        
        except Exception as e:
            # Update instance status
            instance["status"] = WorkflowStatus.FAILED.value
            instance["error"] = str(e)
            instance["failed_at"] = datetime.now().isoformat()
            self._log_instance(instance_id, f"Workflow failed: {str(e)}", level="ERROR")
            
            raise
        finally:
            # Update instance
            instance["updated_at"] = datetime.now().isoformat()
    
    def _log_instance(self, instance_id: str, message: str, level: str = "INFO"):
        """Add a log entry to a workflow instance"""
        instance = self.workflow_instances[instance_id]
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        instance["logs"].append(log_entry)
        
        if level == "ERROR":
            self.logger.error(f"Instance {instance_id}: {message}")
        else:
            self.logger.info(f"Instance {instance_id}: {message}")