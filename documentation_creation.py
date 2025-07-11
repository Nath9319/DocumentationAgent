import asyncio
import os
from agent.agent_manager import AgentManager
from agent.workflow_engine import WorkflowEngine
from core.doc_processor import DocumentProcessor

def doc_processor_handler(input_data):
    output_dir = input_data["workflow_data"]["output_dir"]
    os.makedirs(output_dir, exist_ok=True)
    processor = DocumentProcessor(output_dir=output_dir)
    return processor.process_documentation()

async def main():
    workflow_engine = WorkflowEngine()
    workflow_engine.register_node_handler("process_docs", doc_processor_handler)
    
    instance_id = workflow_engine.create_workflow_instance(
        "doc_generation", 
        {"output_dir": "output\CalculatorCode"}
    )
    
    result = await workflow_engine.execute_workflow(instance_id)
    return result

# Run it
if __name__ == "__main__":
    result = asyncio.run(main())
    print("Documentation generated:", result)