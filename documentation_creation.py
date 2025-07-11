from agent.agent_manager import AgentManager
from agent.workflow_engine import WorkflowEngine
from core.doc_processor import DocumentProcessor
from core.chunk_manager import ChunkManager

# Define handlers
def doc_processor_handler(input_data):
    processor = DocumentProcessor(
        output_dir=input_data["workflow_data"]["output_dir"]
    )
    return processor.process_documentation()

def chunk_handler(input_data):
    chunk_manager = ChunkManager()
    return chunk_manager.get_chunk_stats()

# Setup workflow
workflow_engine = WorkflowEngine()
workflow_engine.register_node_handler("process_docs", doc_processor_handler)
workflow_engine.register_node_handler("generate_chunks", chunk_handler)

# Setup agent manager
agent_manager = AgentManager()
agent_manager.register_agent_types()

# Execute
instance_id = workflow_engine.create_workflow_instance(
    "doc_generation", 
    {"output_dir": "output/repo_name"}
)
await workflow_engine.execute_workflow(instance_id)