import os
import json
import pickle
import networkx as nx
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from config import logger, INCREMENTAL_SAVE_DIR
from nodes import component_loader_node, scrapper_node, selector_node, parallel_writer_node_sync, compiler_node, should_continue_processing, load_all_data
from typing import TypedDict, List, Dict, Optional
from documentation_state import DocumentationState
from datetime import datetime, timedelta
import os
import re
from config import logger, INCREMENTAL_SAVE_DIR, llm
from documentation_utils import save_incremental_progress, save_section_content, save_llm_interaction, sanitize_filename,log_processing_summary
from langchain_openai import AzureChatOpenAI
from system_prompts import ALL_SECTIONS, HIERARCHICAL_STRUCTURE, AGENT_PROMPTS
from langchain_core.prompts import ChatPromptTemplate
import pickle
import json
import threading
import asyncio
from langgraph.graph import StateGraph, END
from tqdm import tqdm
from workflow import app

if __name__ == "__main__":
    start_time = datetime.now()
    progress_bar = None

    JSON_FILE = "output/CalculatorCode/documentation_and_graph_data.json"
    GRAPH_FILE = "output/CalculatorCode/conceptual_graph.pkl"
    FINAL_DOC_DIR = "final_docs"
    os.makedirs(FINAL_DOC_DIR, exist_ok=True)
    OUTPUT_FILE_BASE = "Complete_Technical_Documentation.md"
    OUTPUT_FILE = os.path.join(FINAL_DOC_DIR, OUTPUT_FILE_BASE)

    logger.info(" DOCUMENTATION GENERATION STARTED")
    logger.info(f" Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(" AI DOCUMENTATION GENERATOR")
    print("=" * 80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    logger.info(" File validation:")
    logger.info(f" JSON file: {JSON_FILE}")
    logger.info(f" Graph file: {GRAPH_FILE}")
    logger.info(f" Output file: {OUTPUT_FILE}")
    print(f"Input files:")
    print(f"  - JSON: {JSON_FILE}")
    print(f"  - Graph: {GRAPH_FILE}")
    print(f"  - Output: {OUTPUT_FILE}")

    try:
        logger.info(" Loading initial data...")
        print("\n Loading initial data...")
        
        initial_data = load_all_data(JSON_FILE, GRAPH_FILE)
        if initial_data:
            total_components = len(initial_data["all_data"])
            logger.info(f" Data loaded successfully")
            logger.info(f" Total components to process: {total_components}")
            print(f" Data loaded: {total_components} components found")

            # Use tqdm to show progress of component processing
            component_names = sorted(initial_data["all_data"].keys())
            progress_bar = tqdm(total=total_components, desc="Initializing...", unit="component", 
                               bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

            logger.info(" Initializing documentation state...")
            print(" Initializing documentation state...")
            
            initial_state = DocumentationState(
                unprocessed_components=component_names.copy(),
                all_data=initial_data["all_data"],
                nx_graph=initial_data["nx_graph"],
                document_content={section: "" for section in ALL_SECTIONS},
                current_component_name=None,
                current_component_doc=None,
                current_component_context=None,
                target_sections=[],
                final_document=None,
                scrapper_decision="",
                connected_nodes=[],
                # Initialize architectural diagram fields
                architectural_components={},
                architectural_relationships=[],
                diagram_mermaid_code="graph TD\n",
                diagram_description="## System Architecture Overview\n\nThis diagram represents the architectural components and their relationships:\n\n"
            )

            config = {"recursion_limit": total_components * 4 + 15}
            logger.info(f" Graph configuration:")
            logger.info(f" Graph recursion limit set to: {config['recursion_limit']}")
            logger.info(f" Available documentation sections: {len(ALL_SECTIONS)}")
            print(f" Graph recursion limit: {config['recursion_limit']}")
            print(f" Documentation sections: {len(ALL_SECTIONS)}")
            print(f"--- Running graph with recursion limit: {config['recursion_limit']} ---")

            logger.info(" Starting documentation generation pipeline...")
            print("\n STARTING DOCUMENTATION GENERATION PIPELINE")
            print("=" * 60)
            
            final_state = app.invoke(initial_state, config=config)
            
            logger.info(" Pipeline execution completed")
            print("\n PIPELINE EXECUTION COMPLETED")
            print("=" * 60)
            
            if final_state and final_state.get("final_document"):
                # --- Save final document in versioned manner ---
                logger.info(" Saving final documentation...")
                print(" Saving final documentation...")
                
                def get_versioned_filename(base_path):
                    base_dir, base_name = os.path.split(base_path)
                    name, ext = os.path.splitext(base_name)
                    version = 1
                    candidate = os.path.join(base_dir, base_name)
                    while os.path.exists(candidate):
                        candidate = os.path.join(base_dir, f"{name}_v{version}{ext}")
                        version += 1
                    return candidate

                save_path = get_versioned_filename(OUTPUT_FILE)
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(final_state["final_document"])

                # Save final state as JSON
                final_state_file = os.path.join(INCREMENTAL_SAVE_DIR, f"final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                save_incremental_progress(final_state, "final_completion")

                end_time = datetime.now()
                duration = end_time - start_time

                # Log comprehensive statistics
                doc_length = len(final_state['final_document'])
                char_count = doc_length
                word_count = len(final_state['final_document'].split())
                line_count = final_state['final_document'].count('\n') + 1
                
                logger.info(" DOCUMENTATION GENERATION COMPLETED SUCCESSFULLY")
                logger.info(f" End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f" Total duration: {duration}")
                logger.info(f" Final document saved to: {save_path}")
                logger.info(f" Document statistics:")
                logger.info(f"   - Length: {char_count} characters")
                logger.info(f"   - Words: {word_count}")
                logger.info(f"   - Lines: {line_count}")
                logger.info(f" Incremental saves stored in: {INCREMENTAL_SAVE_DIR}")
                
                # Log comprehensive processing summary
                log_processing_summary()

                print("\n" + "=" * 80)
                print(" SUCCESS! DOCUMENTATION GENERATION COMPLETED")
                print("=" * 80)
                print(f" Document saved to: {save_path}")
                print(f" Total processing time: {duration}")
                print(f"� Document statistics:")
                print(f"   - Characters: {char_count:,}")
                print(f"   - Words: {word_count:,}")
                print(f"   - Lines: {line_count:,}")
                print(f"� Incremental saves: {INCREMENTAL_SAVE_DIR}")
                
                # Run diagram beautification
                # print("\n Running diagram beautification...")
                # logger.info(" Starting diagram beautification...")
                # try:
                #     import subprocess
                #     beautify_script = os.path.join(FINAL_DOC_DIR, "beautify_diagram.py")
                #     if os.path.exists(beautify_script):
                #         logger.info(f" Executing beautification script: {beautify_script}")
                #         result = subprocess.run([sys.executable, beautify_script], 
                #                               capture_output=True, text=True, cwd=os.getcwd())
                #         if result.returncode == 0:
                #             logger.info(" Diagram beautification completed successfully")
                #             print(" Diagram beautification completed successfully!")
                #             print(result.stdout)
                #         else:
                #             logger.warning(f" Diagram beautification had issues: {result.stderr}")
                #             print(f" Diagram beautification had issues: {result.stderr}")
                #     else:
                #         logger.warning(f" Beautification script not found: {beautify_script}")
                #         print(" Beautification script not found")
                # except Exception as e:
                #     logger.error(f" Could not run beautification automatically: {e}")
                #     print(f" Could not run beautification automatically: {e}")
                #     print(f" You can run it manually: python {os.path.join(FINAL_DOC_DIR, 'beautify_diagram.py')}")

            else:
                logger.error(" FAILURE: The final document could not be generated")
                print("\n" + "=" * 80)
                print(" FAILURE: THE FINAL DOCUMENT COULD NOT BE GENERATED")
                print("=" * 80)
        
        else:
            logger.error(" Failed to load initial data")
            print(" Failed to load initial data")
            
    except Exception as e:
        logger.error(f" CRITICAL ERROR during documentation generation: {e}")
        print(f"\n CRITICAL ERROR: {e}")
        print("=" * 80)
    
    finally:
        # Ensure progress bar is always closed
        if progress_bar:
            progress_bar.close()
        
        end_time = datetime.now()
        total_duration = end_time - start_time
        logger.info(f" Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f" Total execution time: {total_duration}")
        print(f"\n Process ended at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Total execution time: {total_duration}")
        print("=" * 80)