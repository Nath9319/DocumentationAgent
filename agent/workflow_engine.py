# core/workflow_engine.py

import os
import yaml
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime
import networkx as nx
from pathlib import Path
import logging
import uuid
from enum import Enum

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

class WorkflowEngine:
    """Flexible workflow execution system for document processing pipelines"""
    
    def __init__(self, workflows_dir: str = "workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows_dir.mkdir(exist_ok=True)
        
        self.workflows = {}
        self.workflow_instances = {}
        self.node_handlers = {}
        
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
        """Register a workflow definition"""
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
        
        # Initialize instance state
        instance = {
            "id": instance_id,
            "workflow_name": workflow_name,
            "workflow_version": workflow["definition"]["version"],
            "status": WorkflowStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": initial_data or {},
            "node_status": {node: NodeStatus.PENDING for node in workflow["graph"].nodes()},
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
        """Execute a workflow instance"""
        if instance_id not in self.workflow_instances:
            raise ValueError(f"Unknown workflow instance: {instance_id}")
        
        instance = self.workflow_instances[instance_id]
        workflow_name = instance["workflow_name"]
        workflow = self.workflows[workflow_name]
        graph = workflow["graph"]
        
        # Update instance status
        instance["status"] = WorkflowStatus.RUNNING
        instance["started_at"] = datetime.now().isoformat()
        self._log_instance(instance_id, "Started workflow execution")
        
        try:
            # Find start nodes (nodes with no incoming edges)
            start_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
            instance["current_nodes"] = start_nodes
            
            # Process nodes until completion
            while instance["current_nodes"]:
                next_nodes = []
                
                # Process current nodes
                for node_id in instance["current_nodes"]:
                    node_def = graph.nodes[node_id]
                    
                    # Skip if node already processed
                    if instance["node_status"][node_id] != NodeStatus.PENDING:
                        continue
                    
                    # Update node status
                    instance["node_status"][node_id] = NodeStatus.RUNNING
                    self._log_instance(instance_id, f"Processing node: {node_id}")
                    
                    try:
                        # Execute node
                        result = await self._execute_node(instance_id, node_id, node_def)
                        
                        # Update node status
                        instance["node_status"][node_id] = NodeStatus.COMPLETED
                        instance["completed_nodes"].append(node_id)
                        
                        # Store node result in instance data
                        instance["data"][f"node_result_{node_id}"] = result
                        
                        # Find next nodes to process
                        successors = list(graph.successors(node_id))
                        for successor in successors:
                            # Check if all predecessor nodes are completed
                            predecessors = list(graph.predecessors(successor))
                            if all(instance["node_status"][pred] in [NodeStatus.COMPLETED, NodeStatus.SKIPPED] 
                                   for pred in predecessors):
                                next_nodes.append(successor)
                    
                    except Exception as e:
                        # Update node status
                        instance["node_status"][node_id] = NodeStatus.FAILED
                        instance["failed_nodes"].append(node_id)
                        
                        error_msg = f"Node {node_id} failed: {str(e)}"
                        self._log_instance(instance_id, error_msg, level="ERROR")
                        
                        # Check if node has error handler
                        error_handler = node_def.get("error_handler")
                        if error_handler:
                            self._log_instance(instance_id, f"Executing error handler for node: {node_id}")
                            
                            try:
                                # Execute error handler
                                await self._execute_error_handler(instance_id, node_id, error_handler, e)
                                
                                # Find next nodes based on error handler
                                error_successors = error_handler.get("next_nodes", [])
                                next_nodes.extend(error_successors)
                            except Exception as handler_err:
                                self._log_instance(
                                    instance_id, 
                                    f"Error handler failed: {str(handler_err)}", 
                                    level="ERROR"
                                )
                                
                                # If error handler fails, workflow fails
                                raise
                        else:
                            # No error handler, workflow fails
                            raise
                
                # Update current nodes
                instance["current_nodes"] = next_nodes
            
            # All nodes processed
            instance["status"] = WorkflowStatus.COMPLETED
            instance["completed_at"] = datetime.now().isoformat()
            self._log_instance(instance_id, "Workflow completed successfully")
            
            return instance["data"]
        
        except Exception as e:
            # Update instance status
            instance["status"] = WorkflowStatus.FAILED
            instance["error"] = str(e)
            instance["failed_at"] = datetime.now().isoformat()
            self._log_instance(instance_id, f"Workflow failed: {str(e)}", level="ERROR")
            
            raise
        finally:
            # Update instance
            instance["updated_at"] = datetime.now().isoformat()
    
    async def _execute_node(self, instance_id: str, node_id: str, node_def: Dict[str, Any]) -> Any:
        """Execute a single workflow node"""
        node_type = node_def.get("type")
        if not node_type:
            raise ValueError(f"Node {node_id} missing type")
        
        if node_type not in self.node_handlers:
            raise ValueError(f"No handler registered for node type: {node_type}")
        
        # Get instance data
        instance = self.workflow_instances[instance_id]
        
        # Get handler
        handler = self.node_handlers[node_type]
        
        # Prepare input data
        input_data = {
            "node_id": node_id,
            "instance_id": instance_id,
            "workflow_data": instance["data"],
            "node_params": node_def.get("params", {})
        }
        
        # Execute handler
        return await handler(input_data)
    
    async def _execute_error_handler(self, instance_id: str, node_id: str, 
                                   error_handler: Dict[str, Any], exception: Exception) -> Any:
        """Execute an error handler for a failed node"""
        handler_type = error_handler.get("type")
        if not handler_type:
            raise ValueError(f"Error handler for node {node_id} missing type")
        
        if handler_type not in self.node_handlers:
            raise ValueError(f"No handler registered for error handler type: {handler_type}")
        
        # Get instance data
        instance = self.workflow_instances[instance_id]
        
        # Get handler
        handler = self.node_handlers[handler_type]
        
        # Prepare input data
        input_data = {
            "node_id": node_id,
            "instance_id": instance_id,
            "workflow_data": instance["data"],
            "error": str(exception),
            "error_type": type(exception).__name__,
            "handler_params": error_handler.get("params", {})
        }
        
        # Execute handler
        return await handler(input_data)
    
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