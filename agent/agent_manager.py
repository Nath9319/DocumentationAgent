# Modified agent_manager.py with LangGraph integration

import os
import json
import time
import networkx as nx
from typing import Dict, List, Any, Optional, Callable, TypedDict
from datetime import datetime
import asyncio
from pathlib import Path
import logging
from langchain_openai import AzureChatOpenAI
# Add LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.doc_processor import DocumentProcessor
from core.graph_searcher import RepoSearcher
# Define a TypedDict for agent state
class AgentState(TypedDict):
    agent_id: str
    status: str
    data: Dict[str, Any]
    messages: List[Dict[str, Any]]
    errors: List[str]
    metrics: Dict[str, Any]

class AgentRegistry:
    """Registry for managing available agent types and instances"""
    
    def __init__(self):
        self.agent_types = {}
        self.agent_instances = {}
        self.logger = logging.getLogger("AgentRegistry")
    
    def register_agent_type(self, agent_type: str, agent_factory: Callable):
        """Register a new agent type with its factory function"""
        self.agent_types[agent_type] = agent_factory
        self.logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(self, agent_type: str, agent_id: str, config: Dict[str, Any]) -> str:
        """Create a new agent instance of the specified type"""
        if agent_type not in self.agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        factory = self.agent_types[agent_type]
        agent = factory(agent_id, config)
        
        self.agent_instances[agent_id] = {
            "type": agent_type,
            "instance": agent,
            "config": config,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "last_health_check": None,
            "metrics": {}
        }
        
        self.logger.info(f"Created agent instance: {agent_id} (type: {agent_type})")
        return agent_id
    
    def get_agent(self, agent_id: str) -> Any:
        """Get an agent instance by ID"""
        if agent_id not in self.agent_instances:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        return self.agent_instances[agent_id]["instance"]
    
    def list_agents(self, agent_type: str = None) -> List[Dict[str, Any]]:
        """List all agent instances, optionally filtered by type"""
        results = []
        
        for agent_id, agent_info in self.agent_instances.items():
            if agent_type is None or agent_info["type"] == agent_type:
                results.append({
                    "id": agent_id,
                    "type": agent_info["type"],
                    "status": agent_info["status"],
                    "created_at": agent_info["created_at"],
                    "last_health_check": agent_info["last_health_check"]
                })
        
        return results

class AgentManager:
    """Central coordination system for multi-agent lifecycle management using LangGraph"""
    
    def __init__(self, data_dir: str = "agent_manager_data"):
        self.registry = AgentRegistry()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize checkpointer for state persistence
        self.checkpointer = MemorySaver()
        
        self.message_queue = asyncio.Queue()
        self.resource_limits = {
            "max_agents": 10,
            "max_tokens_per_agent": 100000,
            "max_concurrent_runs": 5
        }
        
        self.logger = logging.getLogger("AgentManager")
        self._setup_logging()
        
        # Initialize state tracking with LangGraph state
        self.agent_states = {}
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_file = self.data_dir / "agent_manager.log"
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def register_agent_types(self):
        """Register available agent types"""
        from agent.agent_graph import create_agent_graph
        
        # Register documentation agent
        self.registry.register_agent_type("documentation", 
            lambda agent_id, config: create_agent_graph())
        
    def create_documentation_agents(self, 
                                graph: nx.MultiDiGraph,
                                num_agents: int = 3) -> List[str]:
        """Create specialized documentation agents"""
        agents = []
        
        # Memory Agent - creates and manages compressed memory
        memory_agent_id = self.registry.create_agent(
            "memory_agent", 
            f"memory_agent_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            {"graph": graph, "role": "memory_creation"}
        )
        agents.append(memory_agent_id)
        
        # Similarity Agent - manages document similarity and chunking
        similarity_agent_id = self.registry.create_agent(
            "similarity_agent",
            f"similarity_agent_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            {"graph": graph, "role": "similarity_management"}
        )
        agents.append(similarity_agent_id)
        
        # Content Generation Agents
        for i in range(num_agents - 2):
            content_agent_id = self.registry.create_agent(
                "content_agent",
                f"content_agent_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                {"graph": graph, "role": "content_generation", "agent_id": i}
            )
            agents.append(content_agent_id)
        
        return agents

    async def coordinate_documentation_generation(self, 
                                            document_ids: List[str],
                                            graph: nx.MultiDiGraph) -> Dict[str, Any]:
        """Coordinate multi-agent documentation generation"""
        
        # Step 1: Create agents
        agents = self.create_documentation_agents(graph)
        memory_agent, similarity_agent = agents[0], agents[1]
        content_agents = agents[2:]
        
        # Step 2: Memory agent creates compressed understanding
        memory_result = await self.start_agent(memory_agent, {
            "action": "create_memory",
            "graph": graph,
            "documents": document_ids
        })
        
        # Step 3: Similarity agent organizes documents into chunks
        chunking_result = await self.start_agent(similarity_agent, {
            "action": "organize_chunks",
            "documents": document_ids,
            "memory": memory_result.get("compressed_memory"),
            "graph": graph
        })
        
        # Step 4: Content agents generate documentation
        generation_tasks = []
        chunks = chunking_result.get("chunks", [])
        
        for i, chunk in enumerate(chunks):
            agent_id = content_agents[i % len(content_agents)]
            task = self.start_agent(agent_id, {
                "action": "generate_content",
                "chunk": chunk,
                "memory": memory_result.get("compressed_memory"),
                "graph": graph
            })
            generation_tasks.append(task)
        
        # Wait for all content generation to complete
        results = await asyncio.gather(*generation_tasks)
        
        return {
            "memory_creation": memory_result,
            "chunking": chunking_result,
            "content_generation": results
        }


    async def start_agent(self, agent_id: str, initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start an agent with LangGraph state management"""
        if agent_id not in self.registry.agent_instances:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        agent_info = self.registry.agent_instances[agent_id]
        agent = agent_info["instance"]
        
        try:
            # Set up initial state
            state = initial_state or {}
            
            # Create LangGraph state
            agent_state = AgentState(
                agent_id=agent_id,
                status="running",
                data=state,
                messages=[],
                errors=[],
                metrics={}
            )
            
            # Store reference to the agent's state
            self.agent_states[agent_id] = agent_state
            
            # Update agent status
            agent_info["status"] = "running"
            agent_info["started_at"] = datetime.now().isoformat()
            
            self.logger.info(f"Started agent: {agent_id}")
            
            # Create thread_id for checkpointing
            thread_id = f"agent_{agent_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Configure LangGraph with checkpointer
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "agent_id": agent_id
                }
            }
            
            # For async agents, use agent.ainvoke(state, config)
            # For sync agents, use a separate thread
            result = agent.invoke(state, config=config)
            
            # Update agent status on completion
            agent_info["status"] = "completed"
            agent_info["completed_at"] = datetime.now().isoformat()
            
            return result
        except Exception as e:
            # Update agent status on error
            agent_info["status"] = "failed"
            agent_info["error"] = str(e)
            
            self.logger.error(f"Agent {agent_id} failed: {e}")
            raise
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop a running agent"""
        if agent_id not in self.registry.agent_instances:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        agent_info = self.registry.agent_instances[agent_id]
        
        if agent_info["status"] != "running":
            return False
        
        # Update agent status
        agent_info["status"] = "stopped"
        agent_info["stopped_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Stopped agent: {agent_id}")
        return True
    
    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Send a message from one agent to another using LangGraph state"""
        if to_agent not in self.registry.agent_instances:
            raise ValueError(f"Unknown target agent ID: {to_agent}")
        
        # Create message envelope
        envelope = {
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        # Add to message queue
        await self.message_queue.put(envelope)
        self.logger.info(f"Message queued from {from_agent} to {to_agent}")
        
        # If the target agent has state, add message to its state
        if to_agent in self.agent_states:
            target_state = self.agent_states[to_agent]
            target_state["messages"].append(envelope)
    
    async def message_processor(self):
        """Process messages in the queue with LangGraph state updates"""
        while True:
            # Get the next message
            envelope = await self.message_queue.get()
            
            try:
                to_agent = envelope["to"]
                agent_instance = self.registry.get_agent(to_agent)
                
                # Get agent state
                agent_state = self.agent_states.get(to_agent)
                if agent_state:
                    # Update state with new message
                    agent_state["messages"].append(envelope)
                    
                    # Create thread_id for continuation
                    thread_id = f"agent_{to_agent}_msg_{len(agent_state['messages'])}"
                    
                    # Configure LangGraph with thread_id for state continuity
                    config = {
                        "configurable": {
                            "thread_id": thread_id,
                            "agent_id": to_agent
                        }
                    }
                    
                    # Process message with the agent
                    # This would be implemented differently depending on how agents handle messages
                    # For LangGraph agents, we might update state and re-invoke
                    self.logger.info(f"Processing message for {to_agent}")
                
                self.logger.info(f"Delivered message to {to_agent}")
            except Exception as e:
                self.logger.error(f"Error delivering message: {e}")
            finally:
                self.message_queue.task_done()
    
    async def health_check(self, agent_id: str) -> Dict[str, Any]:
        """Check the health of an agent"""
        if agent_id not in self.registry.agent_instances:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        agent_info = self.registry.agent_instances[agent_id]
        
        # Perform health check
        health = {
            "status": agent_info["status"],
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "memory_usage": 0,  # Would need to be implemented
                "token_usage": 0,   # Would need to be implemented
                "runtime": 0        # Would need to be implemented
            }
        }
        
        # Update last health check
        agent_info["last_health_check"] = health["timestamp"]
        agent_info["metrics"] = health["metrics"]
        
        return health
    
    async def restart_agent(self, agent_id: str) -> bool:
        """Restart a failed or stopped agent with LangGraph state persistence"""
        if agent_id not in self.registry.agent_instances:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        # Stop the agent if it's running
        if self.registry.agent_instances[agent_id]["status"] == "running":
            await self.stop_agent(agent_id)
        
        # Get the last state from checkpointer if available
        thread_id = f"agent_{agent_id}"
        saved_state = self.checkpointer.get(thread_id)
        
        # Recreate the agent
        agent_info = self.registry.agent_instances[agent_id]
        agent_type = agent_info["type"]
        config = agent_info["config"]
        
        # Remove old instance
        del self.registry.agent_instances[agent_id]
        
        # Create new instance
        self.registry.create_agent(agent_type, agent_id, config)
        
        # Start the new instance with saved state or existing state
        initial_state = saved_state or self.agent_states.get(agent_id, {}).get("data", {})
        await self.start_agent(agent_id, initial_state)
        
        self.logger.info(f"Restarted agent: {agent_id}")
        return True