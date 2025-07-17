import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import sys
import os
import json
import re
from datetime import datetime, timedelta
import queue
import time
import psutil

class DocumentationGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 AI Documentation Generator - Real-time Monitor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Queue for thread communication
        self.log_queue = queue.Queue()
        self.process = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            'total_components': 0,
            'processed_components': 0,
            'current_component': '',
            'current_section': '',
            'sections_completed': 0,
            'llm_calls': 0,
            'start_time': None,
            'estimated_time': 'Calculating...'
        }
        
        self.setup_ui()
        self.setup_styles()
        
        # Start the log monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        self.monitor_thread.start()
        
        # Schedule UI updates
        self.root.after(100, self.update_ui)
    
    def setup_styles(self):
        """Configure custom styles for the UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom colors
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#ffffff', background='#1e1e1e')
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#4CAF50', background='#1e1e1e')
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground='#e0e0e0', background='#1e1e1e')
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground='#4CAF50', background='#1e1e1e')
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground='#f44336', background='#1e1e1e')
        style.configure('Warning.TLabel', font=('Segoe UI', 10), foreground='#ff9800', background='#1e1e1e')
        style.configure('Progress.TLabel', font=('Segoe UI', 9), foreground='#2196F3', background='#1e1e1e')
    
    def setup_ui(self):
        """Create the main UI layout"""
        
        # Main title frame
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(fill='x', padx=15, pady=10)
        
        title_label = ttk.Label(title_frame, text="🤖 AI Documentation Generator", style='Title.TLabel')
        title_label.pack(side='left')
        
        # Control buttons
        control_frame = tk.Frame(title_frame, bg='#1e1e1e')
        control_frame.pack(side='right')
        
        self.start_btn = tk.Button(control_frame, text="▶️ Start Generation", command=self.start_generation,
                                  bg='#4CAF50', fg='white', font=('Segoe UI', 10, 'bold'), 
                                  relief='flat', padx=15, pady=5)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ Stop", command=self.stop_generation,
                                 bg='#f44336', fg='white', font=('Segoe UI', 10, 'bold'), 
                                 relief='flat', padx=15, pady=5, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(control_frame, text="🗑️ Clear Logs", command=self.clear_logs,
                                  bg='#757575', fg='white', font=('Segoe UI', 10), 
                                  relief='flat', padx=15, pady=5)
        self.clear_btn.pack(side='left', padx=5)
        
        self.open_output_btn = tk.Button(control_frame, text="📁 Open Output", command=self.open_output_folder,
                                        bg='#2196F3', fg='white', font=('Segoe UI', 10), 
                                        relief='flat', padx=15, pady=5)
        self.open_output_btn.pack(side='left', padx=5)
        
        # Create main container with notebook tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Progress tab
        self.progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_frame, text="📊 Progress Monitor")
        self.setup_progress_tab()
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="📋 Live Logs")
        self.setup_logs_tab()
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📈 Statistics")
        self.setup_statistics_tab()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_progress_tab(self):
        """Create the progress monitoring tab"""
        
        # Overall progress section
        overall_frame = tk.LabelFrame(self.progress_frame, text="📊 Overall Progress", 
                                     bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        overall_frame.pack(fill='x', padx=15, pady=10)
        
        # Progress bar and labels
        progress_info_frame = tk.Frame(overall_frame, bg='#2b2b2b')
        progress_info_frame.pack(fill='x', padx=15, pady=10)
        
        self.overall_progress = ttk.Progressbar(progress_info_frame, mode='determinate', length=400)
        self.overall_progress.pack(pady=5)
        
        progress_labels_frame = tk.Frame(progress_info_frame, bg='#2b2b2b')
        progress_labels_frame.pack(fill='x', pady=5)
        
        self.overall_label = ttk.Label(progress_labels_frame, text="0/0 Components (0%)", style='Info.TLabel')
        self.overall_label.pack(side='left')
        
        self.time_remaining_label = ttk.Label(progress_labels_frame, text="Time Remaining: Calculating...", style='Info.TLabel')
        self.time_remaining_label.pack(side='right')
        
        # Current component section
        component_frame = tk.LabelFrame(self.progress_frame, text="🔄 Current Component", 
                                       bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        component_frame.pack(fill='x', padx=15, pady=10)
        
        current_info_frame = tk.Frame(component_frame, bg='#2b2b2b')
        current_info_frame.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(current_info_frame, text="Processing:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.current_component_label = ttk.Label(current_info_frame, text="None", style='Info.TLabel')
        self.current_component_label.grid(row=0, column=1, sticky='w', padx=10)
        
        ttk.Label(current_info_frame, text="Section:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=5)
        self.current_section_label = ttk.Label(current_info_frame, text="None", style='Info.TLabel')
        self.current_section_label.grid(row=1, column=1, sticky='w', padx=10)
        
        ttk.Label(current_info_frame, text="Status:", style='Header.TLabel').grid(row=2, column=0, sticky='w', padx=5)
        self.current_status_label = ttk.Label(current_info_frame, text="Idle", style='Info.TLabel')
        self.current_status_label.grid(row=2, column=1, sticky='w', padx=10)
        
        # Recent activity section
        activity_frame = tk.LabelFrame(self.progress_frame, text="📋 Recent Activity", 
                                      bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        activity_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=15, bg='#1e1e1e', fg='#ffffff',
                                                      font=('Consolas', 9), wrap=tk.WORD)
        self.activity_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure text tags for different activity types
        self.activity_text.tag_configure('COMPONENT', foreground='#4CAF50', font=('Consolas', 9, 'bold'))
        self.activity_text.tag_configure('SECTION', foreground='#2196F3')
        self.activity_text.tag_configure('SUCCESS', foreground='#8BC34A')
        self.activity_text.tag_configure('ERROR', foreground='#f44336')
        self.activity_text.tag_configure('WARNING', foreground='#ff9800')
    
    def setup_logs_tab(self):
        """Create the logs monitoring tab"""
        
        # Log controls
        log_controls_frame = tk.Frame(self.logs_frame, bg='#2b2b2b')
        log_controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(log_controls_frame, text="Filter:", style='Header.TLabel').pack(side='left', padx=5)
        
        self.log_filter_var = tk.StringVar(value="ALL")
        self.log_filter_combo = ttk.Combobox(log_controls_frame, textvariable=self.log_filter_var,
                                            values=["ALL", "INFO", "ERROR", "WARNING", "SUCCESS", "LLM", "PROGRESS"])
        self.log_filter_combo.pack(side='left', padx=5)
        self.log_filter_combo.bind('<<ComboboxSelected>>', self.filter_logs)
        
        auto_scroll_frame = tk.Frame(log_controls_frame, bg='#2b2b2b')
        auto_scroll_frame.pack(side='right', padx=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_scroll_check = tk.Checkbutton(auto_scroll_frame, text="Auto-scroll", variable=self.auto_scroll_var,
                                               bg='#2b2b2b', fg='#ffffff', selectcolor='#2b2b2b')
        self.auto_scroll_check.pack(side='right')
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(self.logs_frame, bg='#1e1e1e', fg='#ffffff',
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Configure text tags for different log levels
        self.log_text.tag_configure('INFO', foreground='#4CAF50')
        self.log_text.tag_configure('ERROR', foreground='#f44336')
        self.log_text.tag_configure('WARNING', foreground='#ff9800')
        self.log_text.tag_configure('SUCCESS', foreground='#8BC34A')
        self.log_text.tag_configure('PROGRESS', foreground='#2196F3')
        self.log_text.tag_configure('LLM', foreground='#9C27B0')
        self.log_text.tag_configure('TIMESTAMP', foreground='#757575')
    
    def setup_statistics_tab(self):
        """Create the statistics tab"""
        
        # Performance metrics
        perf_frame = tk.LabelFrame(self.stats_frame, text="⚡ Performance Metrics", 
                                  bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        perf_frame.pack(fill='x', padx=15, pady=10)
        
        perf_grid = tk.Frame(perf_frame, bg='#2b2b2b')
        perf_grid.pack(fill='x', padx=15, pady=10)
        
        # Row 1
        ttk.Label(perf_grid, text="Start Time:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.start_time_label = ttk.Label(perf_grid, text="Not started", style='Info.TLabel')
        self.start_time_label.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(perf_grid, text="Elapsed Time:", style='Header.TLabel').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.elapsed_time_label = ttk.Label(perf_grid, text="00:00:00", style='Info.TLabel')
        self.elapsed_time_label.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        # Row 2
        ttk.Label(perf_grid, text="Estimated Remaining:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.estimated_time_label = ttk.Label(perf_grid, text="Calculating...", style='Info.TLabel')
        self.estimated_time_label.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(perf_grid, text="Components/Minute:", style='Header.TLabel').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        self.processing_rate_label = ttk.Label(perf_grid, text="0.0", style='Info.TLabel')
        self.processing_rate_label.grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # LLM metrics
        llm_frame = tk.LabelFrame(self.stats_frame, text="🤖 LLM Metrics", 
                                 bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        llm_frame.pack(fill='x', padx=15, pady=10)
        
        llm_grid = tk.Frame(llm_frame, bg='#2b2b2b')
        llm_grid.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(llm_grid, text="Total LLM Calls:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.llm_calls_label = ttk.Label(llm_grid, text="0", style='Info.TLabel')
        self.llm_calls_label.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(llm_grid, text="Successful Calls:", style='Header.TLabel').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.successful_calls_label = ttk.Label(llm_grid, text="0", style='Success.TLabel')
        self.successful_calls_label.grid(row=0, column=3, sticky='w', padx=10, pady=5)
        
        ttk.Label(llm_grid, text="Failed Calls:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.failed_calls_label = ttk.Label(llm_grid, text="0", style='Error.TLabel')
        self.failed_calls_label.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(llm_grid, text="Average Response Time:", style='Header.TLabel').grid(row=1, column=2, sticky='w', padx=10, pady=5)
        self.avg_response_time_label = ttk.Label(llm_grid, text="0.0s", style='Info.TLabel')
        self.avg_response_time_label.grid(row=1, column=3, sticky='w', padx=10, pady=5)
        
        # System metrics
        system_frame = tk.LabelFrame(self.stats_frame, text="💻 System Resources", 
                                    bg='#2b2b2b', fg='#4CAF50', font=('Segoe UI', 12, 'bold'))
        system_frame.pack(fill='x', padx=15, pady=10)
        
        system_grid = tk.Frame(system_frame, bg='#2b2b2b')
        system_grid.pack(fill='x', padx=15, pady=10)
        
        ttk.Label(system_grid, text="CPU Usage:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.cpu_usage_label = ttk.Label(system_grid, text="0%", style='Info.TLabel')
        self.cpu_usage_label.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        ttk.Label(system_grid, text="Memory Usage:", style='Header.TLabel').grid(row=0, column=2, sticky='w', padx=10, pady=5)
        self.memory_usage_label = ttk.Label(system_grid, text="0%", style='Info.TLabel')
        self.memory_usage_label.grid(row=0, column=3, sticky='w', padx=10, pady=5)
    
    def setup_status_bar(self):
        """Create the status bar"""
        self.status_bar = tk.Frame(self.root, bg='#424242', height=30)
        self.status_bar.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(self.status_bar, text="Ready", bg='#424242', fg='#ffffff', 
                                    font=('Segoe UI', 9), anchor='w')
        self.status_label.pack(side='left', padx=15, pady=5)
        
        self.time_label = tk.Label(self.status_bar, text="", bg='#424242', fg='#ffffff', 
                                  font=('Segoe UI', 9), anchor='e')
        self.time_label.pack(side='right', padx=15, pady=5)
    
    def start_generation(self):
        """Start the documentation generation process"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.stats['start_time'] = datetime.now()
        
        # Clear previous logs and statistics
        self.log_text.delete(1.0, tk.END)
        self.activity_text.delete(1.0, tk.END)
        self.reset_statistics()
        
        # Start the subprocess
        try:
            self.process = subprocess.Popen(
                [sys.executable, 'mainG.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace',
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Start monitoring thread
            self.output_thread = threading.Thread(target=self.read_output, daemon=True)
            self.output_thread.start()
            
            self.add_log("🚀 Documentation generation started", 'SUCCESS')
            self.add_activity("🚀 Process started", 'SUCCESS')
            self.status_label.config(text="Running documentation generation...")
            
        except Exception as e:
            self.add_log(f"❌ Failed to start process: {e}", 'ERROR')
            self.is_running = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
    
    def stop_generation(self):
        """Stop the documentation generation process"""
        if self.process and self.is_running:
            self.process.terminate()
            self.add_log("⏹️ Process stopped by user", 'WARNING')
            self.add_activity("⏹️ Process stopped by user", 'WARNING')
            
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Stopped")
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.activity_text.delete(1.0, tk.END)
        self.add_log("🗑️ Logs cleared", 'INFO')
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = "final_docs"
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showinfo("Info", "Output directory doesn't exist yet. Run the generation first.")
    
    def read_output(self):
        """Read output from the subprocess"""
        if not self.process:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.log_queue.put(('output', line.strip()))
                if self.process.poll() is not None:
                    break
                    
            # Process has finished
            return_code = self.process.poll()
            if return_code == 0:
                self.log_queue.put(('status', 'completed'))
            else:
                self.log_queue.put(('status', 'failed'))
                
        except Exception as e:
            self.log_queue.put(('error', str(e)))
    
    def monitor_logs(self):
        """Monitor the log file for incremental saves"""
        log_file = "documentation_generation.log"
        incremental_dir = "incremental_saves"
        
        while True:
            try:
                # Check for new incremental saves
                if os.path.exists(incremental_dir):
                    for file in os.listdir(incremental_dir):
                        if file.endswith('.json') and not file.startswith('final_state_'):
                            filepath = os.path.join(incremental_dir, file)
                            if os.path.getmtime(filepath) > time.time() - 5:  # File modified in last 5 seconds
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                    self.log_queue.put(('progress_update', data))
                                except:
                                    pass
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception:
                time.sleep(5)  # Wait longer if there's an error
    
    def update_ui(self):
        """Update UI with new data from the queue"""
        try:
            while True:
                try:
                    msg_type, data = self.log_queue.get_nowait()
                    
                    if msg_type == 'output':
                        self.parse_output_line(data)
                    elif msg_type == 'progress_update':
                        self.update_progress_from_data(data)
                    elif msg_type == 'status':
                        self.handle_process_status(data)
                    elif msg_type == 'error':
                        self.add_log(f"❌ Error: {data}", 'ERROR')
                        
                except queue.Empty:
                    break
                    
            # Update time labels
            if self.stats['start_time']:
                elapsed = datetime.now() - self.stats['start_time']
                self.elapsed_time_label.config(text=str(elapsed).split('.')[0])
                
                # Calculate estimated remaining time
                if self.stats['processed_components'] > 0:
                    rate = self.stats['processed_components'] / (elapsed.total_seconds() / 60)  # components per minute
                    remaining_components = self.stats['total_components'] - self.stats['processed_components']
                    if rate > 0:
                        remaining_minutes = remaining_components / rate
                        remaining_time = timedelta(minutes=remaining_minutes)
                        self.estimated_time_label.config(text=str(remaining_time).split('.')[0])
                        self.processing_rate_label.config(text=f"{rate:.1f}")
                    
            # Update system resources
            try:
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                self.cpu_usage_label.config(text=f"{cpu_percent:.1f}%")
                self.memory_usage_label.config(text=f"{memory_percent:.1f}%")
            except:
                pass
                
            # Update current time
            self.time_label.config(text=datetime.now().strftime('%H:%M:%S'))
            
        except Exception as e:
            pass  # Ignore UI update errors
            
        # Schedule next update
        self.root.after(1000, self.update_ui)
    
    def parse_output_line(self, line):
        """Parse a line of output and extract relevant information"""
        # Add to logs
        log_type = 'INFO'
        if '❌' in line or 'ERROR' in line or 'Failed' in line:
            log_type = 'ERROR'
        elif '⚠️' in line or 'WARNING' in line:
            log_type = 'WARNING'
        elif '✅' in line or '🎉' in line or 'Success' in line:
            log_type = 'SUCCESS'
        elif '🤖' in line or 'LLM' in line:
            log_type = 'LLM'
        elif 'Progress:' in line or '%' in line:
            log_type = 'PROGRESS'
            
        self.add_log(line, log_type)
        
        # Extract component information
        if "Loading component:" in line:
            match = re.search(r"Loading component: '([^']+)'", line)
            if match:
                self.stats['current_component'] = match.group(1)
                self.current_component_label.config(text=self.stats['current_component'])
                self.add_activity(f"📥 Loading: {self.stats['current_component']}", 'COMPONENT')
                
        elif "Processing section:" in line:
            match = re.search(r"Processing section: '([^']+)'", line)
            if match:
                self.stats['current_section'] = match.group(1)
                self.current_section_label.config(text=self.stats['current_section'])
                self.add_activity(f"✍️ Writing: {self.stats['current_section']}", 'SECTION')
                
        elif "Total components to process:" in line:
            match = re.search(r"Total components to process: (\d+)", line)
            if match:
                self.stats['total_components'] = int(match.group(1))
                self.overall_progress.config(maximum=self.stats['total_components'])
                
        elif "Progress:" in line:
            match = re.search(r"Progress: (\d+)/(\d+)", line)
            if match:
                current, total = int(match.group(1)), int(match.group(2))
                self.stats['processed_components'] = current
                self.stats['total_components'] = total
                self.update_progress_display()
                
        # Track LLM calls
        if "Calling LLM" in line or "🤖" in line:
            self.stats['llm_calls'] += 1
            self.llm_calls_label.config(text=str(self.stats['llm_calls']))
    
    def update_progress_display(self):
        """Update the progress display"""
        if self.stats['total_components'] > 0:
            progress_value = (self.stats['processed_components'] / self.stats['total_components']) * 100
            self.overall_progress.config(value=progress_value)
            
            percentage = (self.stats['processed_components'] / self.stats['total_components']) * 100
            self.overall_label.config(text=f"{self.stats['processed_components']}/{self.stats['total_components']} Components ({percentage:.1f}%)")
    
    def update_progress_from_data(self, data):
        """Update progress from incremental save data"""
        if 'processed_components' in data and 'total_components' in data:
            self.stats['processed_components'] = data['processed_components']
            self.stats['total_components'] = data['total_components']
            self.update_progress_display()
            
        if 'operation' in data:
            self.current_status_label.config(text=data['operation'].replace('_', ' ').title())
    
    def handle_process_status(self, status):
        """Handle process completion status"""
        if status == 'completed':
            self.add_log("🎉 Documentation generation completed successfully!", 'SUCCESS')
            self.add_activity("🎉 Generation completed!", 'SUCCESS')
            self.current_status_label.config(text="Completed")
        elif status == 'failed':
            self.add_log("❌ Documentation generation failed", 'ERROR')
            self.add_activity("❌ Generation failed", 'ERROR')
            self.current_status_label.config(text="Failed")
            
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
    
    def add_log(self, message, log_type='INFO'):
        """Add a message to the log display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, f"[{timestamp}] ", 'TIMESTAMP')
        self.log_text.insert(tk.END, f"{message}\n", log_type)
        
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def add_activity(self, message, activity_type='INFO'):
        """Add a message to the activity display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        full_message = f"[{timestamp}] {message}\n"
        
        self.activity_text.insert(tk.END, full_message, activity_type)
        
        # Keep only last 50 lines
        lines = self.activity_text.get('1.0', tk.END).split('\n')
        if len(lines) > 50:
            self.activity_text.delete('1.0', f'{len(lines)-50}.0')
        
        self.activity_text.see(tk.END)
    
    def filter_logs(self, event=None):
        """Filter logs based on selected filter"""
        # This is a placeholder for log filtering functionality
        # In a full implementation, you'd maintain separate log storage
        # and filter display based on the selected type
        pass
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.stats = {
            'total_components': 0,
            'processed_components': 0,
            'current_component': '',
            'current_section': '',
            'sections_completed': 0,
            'llm_calls': 0,
            'start_time': datetime.now(),
            'estimated_time': 'Calculating...'
        }
        
        self.overall_progress.config(value=0)
        self.overall_label.config(text="0/0 Components (0%)")
        self.current_component_label.config(text="None")
        self.current_section_label.config(text="None")
        self.current_status_label.config(text="Initializing...")
        self.start_time_label.config(text=self.stats['start_time'].strftime('%H:%M:%S'))
        self.llm_calls_label.config(text="0")
        self.successful_calls_label.config(text="0")
        self.failed_calls_label.config(text="0")

def main():
    root = tk.Tk()
    app = DocumentationGeneratorUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
